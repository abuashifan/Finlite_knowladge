# Arsitektur — Yang Berlaku Lintas Modul

> Empat hal di file ini menentukan hampir semua keputusan teknis di project:
> **multi-tenancy**, **kontrak API**, **siklus hidup dokumen**, dan **penomoran dokumen**.
> Salah memahami salah satunya akan menghasilkan kode yang "jalan" tapi salah diam-diam.

---

## 1. Multi-tenancy: satu file database per perusahaan

Ini bukan multi-tenancy berbasis kolom `company_id`. Tiap perusahaan punya **file
SQLite terpisah**.

```
database/database.sqlite               <- CENTRAL: users, companies, roles, permissions,
                                          plans, subscriptions, tenant_databases,
                                          fiscal_years, accounting_periods, activity_logs
database/tenants/company_000001.sqlite <- TENANT 1: seluruh data bisnis
database/tenants/company_000002.sqlite <- TENANT 2: seluruh data bisnis
```

27 tabel central, 77 tabel tenant.

### Konsekuensi yang paling sering terlewat

**Id record berulang di tiap tenant.** Autoincrement mulai dari 1 di setiap file:

| id | company 1 | company 2 |
|----|-----------|-----------|
| 1 | `1100 Kas Kecil` | `1100 Kas` |
| 2 | `1110 Bank Operasional` | `1110 Bank` |

Artinya id **tidak pernah** cukup untuk mengidentifikasi record — konteks perusahaan
selalu diperlukan. Ini yang membuat cache frontend yang tidak ber-scope perusahaan jadi
bug integritas data, bukan sekadar bug tampilan (lihat
`plans/company-session-layer/README.md`).

### Bagaimana perusahaan aktif ditentukan

Setiap request API membawa header **`X-Company-ID`**. Middleware
`EnsureCompanyAccess` (`app/Shared/Http/Middleware/`) mengerjakan berurutan:

1. user terautentikasi? kalau tidak → `401 UNAUTHENTICATED`
2. header `X-Company-ID` ada? kalau tidak → `422 X_COMPANY_ID_REQUIRED`
3. perusahaannya ada? kalau tidak → `404 COMPANY_NOT_FOUND`
4. user punya baris `company_users` berstatus `active`? kalau tidak → `403 COMPANY_ACCESS_DENIED`
5. `tenant_databases` untuk perusahaan itu berstatus `active`? kalau tidak → `422 TENANT_DATABASE_NOT_ACTIVE`
6. `TenantContext` diisi, lalu `TenantConnectionManager::connect()` mengarahkan
   koneksi Eloquent bernama `tenant` ke file SQLite perusahaan tersebut

Model tenant menyatakan dirinya lewat `protected $connection = 'tenant';`.
Model central tidak menyatakan connection (memakai `default`).

**Alias middleware** terdaftar di `bootstrap/app.php`: `company.access` dan `permission`.

### Provisioning

`app/Shared/Tenant/`: `TenantProvisioningService` membuat file database baru,
`TenantMigrationService` menjalankan 87 migrasi tenant di atasnya.

---

## 2. Kontrak API

### Bentuk response — tiga varian, dibentuk `ApiResponseBuilder`

```jsonc
// sukses
{ "success": true,  "message": "Success", "data": <apa pun>, "meta": {} }

// galat
{ "success": false, "code": "DUPLICATE_ACCOUNT_CODE", "message": "...",
  "errors": { "field": ["pesan"] }, "meta": {} }

// warning — butuh konfirmasi user, HTTP 409
{ "success": false, "code": "...", "message": "...",
  "requires_confirmation": true, "errors": [], "meta": {} }
```

> **Jalur kode galat adalah `code` di akar, BUKAN `error.code`.**
> Kesalahan ini pernah membuat assertion test lolos-salah.

Validasi Laravel (`ValidationException`) dan `QueryException` di-render ulang ke bentuk
yang sama lewat handler di `bootstrap/app.php` — termasuk menerjemahkan pelanggaran
`NOT NULL` / `UNIQUE` SQLite menjadi `422` dengan `errors` per-field.

### Endpoint daftar — dua bentuk, ditentukan ada-tidaknya `page`/`per_page`

`ApiResponse::listResponse()` (trait di `app/Shared/Api/`):

| Request | Response `data` |
|---|---|
| tanpa `page` & `per_page` | array datar seluruh baris |
| ada salah satunya | `{ data: [...], current_page, per_page, total, last_page, from, to }` |

Kalau cabang kedua menerima sesuatu yang bukan `LengthAwarePaginator`, ia
**melempar `LogicException`**. Ini disengaja: sampai Fase 6 `list-query-pushdown` ada
jalur cadangan yang menyaring di memori PHP, dan justru jalur "tetap jalan diam-diam"
itu yang menyembunyikan masalah performa berbulan-bulan.

### `AppliesListQuery` — search/filter/sort/paginate dikerjakan di SQL

Trait `app/Shared/Api/AppliesListQuery.php` dipakai **32 endpoint daftar**. Kelas
pemakainya **wajib mendeklarasikan enam properti** berikut sendiri:

| Properti | Isi |
|---|---|
| `$listSearchable` | kolom tabel sendiri yang dicari, mis. `['invoice_number']` |
| `$listSearchableRelations` | relasi ikut dicari, mis. `['customer' => ['name']]`; `[]` bila tidak ada |
| `$listDateColumn` | kolom tanggal untuk filter periode; `''` bila tidak ada |
| `$listStatusColumn` | `'status'` (transaksi) atau `'is_active'` (master data) |
| `$listDefaultSort` | mis. `['invoice_date' => 'desc', 'id' => 'desc']` |
| `$listSortable` | daftar putih kolom untuk `sort_by` — input di luar ini diabaikan |

> ⚠️ **Trait sengaja tidak mendeklarasikan properti-properti itu** (PHP menolak trait
> dan kelas mendeklarasikan properti bertipe sama dengan default berbeda). Kalau kelas
> lupa mendeklarasikan salah satunya, **gagalnya baru saat runtime** dengan
> "Typed property must not be accessed before initialization".

Parameter yang diterima: `search`, `status` (boleh dipisah koma),
`date_from`/`start_date`, `date_to`/`end_date`, `sort_by`/`sort`,
`sort_direction`/`direction`, `page`, `per_page` (**diklem maksimum 100**).

Untuk master data, `?status=active|inactive` dipetakan ke boolean `is_active` —
bukan `is_active=1/0` mentah.

### Frontend meratakan bentuk paginasi

`src/services/http.ts` → `normalizeApiResponse()` mengubah
`data: { data: [...], current_page, ... }` menjadi:

```ts
{ data: [...],  meta: { current_page, last_page, per_page, total } }
```

Jadi di hook frontend, `data.data` adalah baris dan `data.meta.total` adalah totalnya.
**Response tanpa paginasi menghasilkan `meta: []`** — pernah membuat lima halaman
menampilkan `totalRows` 0.

Interceptor `http.ts` juga:
- menyisipkan `Authorization: Bearer` dan `X-Company-ID` di setiap request
- `401` → logout + redirect `/login`
- `503` atau header `x-maintenance-mode` → `/maintenance`
- **menolak balasan GET yang `X-Company-ID`-nya sudah tidak cocok** dengan perusahaan
  aktif (mencegah data tenant lama mendarat setelah ganti perusahaan; hanya GET, karena
  mutasi sudah dieksekusi server)

---

## 3. Siklus hidup dokumen

Didefinisikan di `app/Shared/TransactionLifecycle/`.

**Status** (`TransactionStatus`): `draft` → `approved` → `posted` → `void`.
Plus `obsolete` — status efek/sistem, bukan status transaksi utama.

**Aksi** (`TransactionAction`): `create`, `edit`, `void`, `approve`, `post`, `view`.

**Penjaga yang berlaku** (dipakai lintas modul, jangan dilewati):

| Layanan | Perannya |
|---|---|
| `TransactionPolicyService` | boleh/tidaknya sebuah aksi pada status tertentu |
| `TransactionDateGuardService` | menolak tanggal di periode terkunci |
| `TransactionDependencyService` | menolak void bila dokumen dipakai dokumen lain |
| `TransactionVoidEffectService` | membereskan efek saat dokumen di-void |
| `TransactionRevisionService` | menyimpan snapshot revisi (`transaction_revisions`) |
| `PaymentTermDueDateService` | menghitung jatuh tempo dari syarat pembayaran |

Aturan yang tidak boleh dilanggar (dari `AGENTS.md` backend): **journal immutability**,
period/date guard, atomicity transaksi, dan perilaku rollback/void.

Hasil kebijakan dikembalikan sebagai `TransactionPolicyResult`, dan
`ApiResponseBuilder::fromPolicyResult()` menerjemahkannya: ditolak → `error` 403,
diizinkan-tapi-warning → `warning` 409 dengan `requires_confirmation: true`.

---

## 4. Penomoran dokumen

`app/Shared/DocumentNumbering/` — `DocumentNumberService` + `DocumentType` (±20 jenis
dokumen: `journal_entry`, `sales_quotation`, `sales_order`, `delivery_order`,
`proforma_invoice`, `sales_invoice`, `sales_receipt`, `sales_return`,
`customer_deposit`, `purchase_request`, `purchase_order`, `goods_receipt`,
`vendor_bill`, `vendor_payment`, `vendor_deposit`, `purchase_return`, `cash_receipt`,
`cash_payment`, `bank_transfer`, …).

Nomor urut disimpan di tabel **central**: `document_number_sequences` +
`document_numbering_settings`.

Nama kolom nomor berbeda-beda per modul (`invoice_number`, `order_number`,
`receipt_number`, …). Frontend menyamakannya lewat alias di `http.ts`
(`DOCUMENT_NUMBER_FIELDS` → field kanonik `number`). Ini **fallback yang
didokumentasikan** (spec-33/GAP-08), bukan solusi utama: resource yang punya lebih dari
satu field nomor sekaligus (mis. Sales Order punya `order_number` **dan**
`quotation_number`) **wajib** override eksplisit lewat adapter di service-nya —
contohnya `salesOrderApi.toSalesOrder`.

---

## 5. Alur autentikasi & sesi

1. `POST /api/auth/login` → token Sanctum + data user
2. `GET /api/companies` → daftar perusahaan yang boleh diakses
3. Satu perusahaan → langsung dipilih. Lebih dari satu → halaman pemilih perusahaan
4. `POST /api/companies/select` → `active_company`
5. `GET /api/auth/permissions` → daftar permission **untuk perusahaan itu**

Permission bersifat **per perusahaan**, jadi harus diambil ulang setiap kali perusahaan
berganti.

**Tutup Database vs Keluar** (lihat `plans/company-session-layer/README.md`):
- *Tutup Database* — menutup perusahaan aktif, sesi login tetap hidup. Ini satu-satunya
  jalur ganti perusahaan.
- *Keluar* — mengakhiri sesi login.

Keduanya mengosongkan cache TanStack Query dan menutup semua tab, dan keduanya
**diblokir** selama ada form dengan isian belum tersimpan.

Tidak ada endpoint "deselect" di backend — tenancy ditentukan per request lewat header,
jadi menutup database cukup dikerjakan di klien.
