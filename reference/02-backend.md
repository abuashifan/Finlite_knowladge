# Backend — Laravel 13 Modular Monolith

`/workspace/laravel_backend/` · PHP 8.3 · Laravel 13 · Sanctum · SQLite
Paket pihak ketiga hanya tiga: `laravel/framework`, `laravel/sanctum`, `laravel/tinker`.

---

## 1. Bentuk project

Refactor ke modular monolith **sudah selesai** (`plans/laravel-modularization/`,
✅ 2026-07-08). Isi `app/`:

```
app/
  Modules/<Modul>/     18 modul — kode bisnis
  Shared/<Subsistem>/  16 subsistem — dipakai lintas modul
  Providers/ Models/ Http/   sisa kerangka Laravel
```

`app/Http/Controllers/` **bukan** lagi tempat controller aplikasi — semuanya pindah ke
modul masing-masing.

### Isi standar sebuah modul

```
app/Modules/Sales/
  Controllers/   Models/   Requests/   Services/   Routes/api.php   Providers/   README.md
```

Beberapa modul punya `README.md` sendiri — baca itu sebelum menyentuh modulnya.

---

## 2. Daftar modul

Angka = jumlah endpoint di `Routes/api.php` (total **429**).

| Modul | Endpoint | Prefix rute | Model | Service |
|---|---|---|---|---|
| **Sales** | 85 | `sales` | 16 | 17 |
| **Purchase** | 72 | `purchase` | 14 | 16 |
| **MasterData** | 59 | `master-data` | 10 | 11 |
| **Inventory** | 38 | `inventory`, `reports` | 7 | 17 |
| **Reports** | 35 | `reports`, `sales`, `purchase`, `tax`, `saved` | 2 | 25 |
| **Access** | 27 | `access` | 0 | 0 |
| **CashBank** | 27 | `cash-bank` | 7 | 6 |
| **Budget** | 16 | `budget-periods`, `budget-submissions` | 3 | 5 |
| **FixedAssets** | 14 | `fixed-assets`, `reports` | 8 | 2 |
| **Accounting** | 12 | `accounting`, `v1/accounting` | 3 | 6 |
| **OpeningBalance** | 11 | `opening-balance` | 2 | 3 |
| **Journal** | 8 | `/journals` (tanpa prefix group) | 2 | 6 |
| **Setup** | 8 | `setup` | 0 | 1 |
| **Auth** | 5 | `auth` | 0 | 0 |
| **Settings** | 5 | `/settings/company/*` | 0 | 1 |
| **Dashboard** | 4 | `dashboard` | 0 | 1 |
| **Companies** | 2 | `/companies`, `/companies/select` | 0 | 1 |
| **Tenant** | 1 | `/tenant-context-test` | 0 | 0 |

`routes/api.php` isinya hanya `/health` + 18 baris `require` ke
`app/Modules/*/Routes/api.php`. **Untuk mencari sebuah endpoint, buka file rute
modulnya, bukan `routes/api.php`.**

### Catatan pemetaan yang bisa membingungkan

- **Reports memakai prefix milik modul lain** (`sales`, `purchase`) untuk laporan
  spesifik domain — mis. laporan piutang ada di prefix `sales`, bukan `reports`.
- **FixedAssets dan Inventory juga mendaftarkan rute di prefix `reports`.**
  Jadi satu prefix bisa dilayani lebih dari satu modul; cari dengan grep lintas modul.
- **Journal, Companies, Settings, Tenant tidak memakai `prefix()`** — path lengkapnya
  ditulis langsung di tiap baris rute.

---

## 3. `app/Shared/` — 16 subsistem

| Subsistem | Isi penting |
|---|---|
| **Api** | `ApiResponse` (trait), `ApiResponseBuilder`, `ApiErrorCode`, `AppliesListQuery`, `ResolvesAdjacentRecords` |
| **TransactionLifecycle** | status/aksi dokumen, policy, date guard, dependency, void effect, revision, due date |
| **Tenant** | `TenantContext`, `TenantConnectionManager`, `TenantProvisioningService`, `TenantMigrationService` |
| **DocumentNumbering** | `DocumentNumberService`, `DocumentType`, `DocumentNumberFormat` |
| **Permission** | `PermissionService` — sumber jawaban "boleh atau tidak" |
| **Http** | middleware `EnsureCompanyAccess`, `EnsurePermission` |
| **Audit** | `AuditLogService`, `AuditEvent`, `AuditAction` |
| **Models** | model central: `Company`, `CompanyUser`, `TenantDatabase`, … |
| **AccountMapping** | pemetaan akun default per jenis transaksi |
| **SourceDocument** | penelusuran dokumen sumber → dokumen turunan |
| **Reports** | kerangka bersama laporan |
| **Enums, Exceptions, Validation, DataRetention, Providers, Contracts, Checkers** | penunjang |

`ResolvesAdjacentRecords` menyediakan endpoint `adjacent` (record sebelum/sesudah)
yang dipakai tombol navigasi Prev/Next di form frontend.

---

## 4. Konvensi wajib (dari `AGENTS.md` backend)

1. **Logika bisnis di Service.** Controller tipis: validasi lewat FormRequest,
   panggil service, balas lewat trait `ApiResponse`.
2. **Validasi di FormRequest** (`Requests/`), bukan di controller.
3. **Operasi tulis wajib transaction-safe.**
4. **Perubahan schema wajib lewat migration.** Jangan menyunting file SQLite atau data
   bisnis existing secara langsung.
5. **Pertahankan** tenant middleware, permission, journal immutability, period/date
   guard, dan perilaku rollback/void.
6. **Jangan refactor modul yang tidak diminta.**
7. Tambah/perbarui feature test untuk happy path **dan** failure path utama.

### Anatomi service daftar yang benar

```php
class SalesInvoiceService
{
    use AppliesListQuery;

    // WAJIB dideklarasikan sendiri — trait tidak mendeklarasikannya.
    protected array $listSearchable = ['invoice_number'];
    protected array $listSearchableRelations = ['customer' => ['name', 'contact_code']];
    protected string $listDateColumn = 'invoice_date';
    protected string $listStatusColumn = 'status';
    protected array $listDefaultSort = ['invoice_date' => 'desc', 'id' => 'desc'];
    protected array $listSortable = ['invoice_number', 'invoice_date', 'total_amount'];

    public function list(array $filters = []): LengthAwarePaginator|Collection
    {
        $query = SalesInvoice::query()->with('customer');
        // filter khusus modul dipasang di sini, SEBELUM applyListQuery()
        if (! empty($filters['customer_id'])) {
            $query->where('customer_id', $filters['customer_id']);
        }
        return $this->applyListQuery($query, $filters);   // <- selalu baris terakhir
    }
}
```

> **Jebakan yang pernah terjadi:** menyisakan `->get()` di akhir `list()` setelah
> beralih ke trait. Tidak ada error — request-nya diam-diam kembali memakai jalur
> lama. Cek mekanis sebelum selesai:
> ```bash
> rtk grep -n "function list" -A 30 app/Modules/**/Services/*.php | rtk grep "\->get()"
> ```

---

## 5. Database

```
config/database.php
  connections.default -> sqlite  (database/database.sqlite)   CENTRAL
  connections.tenant  -> sqlite  (path di-set runtime oleh middleware)
```

- Migrasi central: `database/migrations/*.php` (25)
- Migrasi tenant: `database/migrations/tenant/*.php` (87)
- File tenant: `database/tenants/company_%06d.sqlite`

**Jangan pernah menebak nama kolom.** Periksa dulu:

```bash
rtk php -r '$db=new PDO("sqlite:database/tenants/company_000001.sqlite");
foreach($db->query("pragma table_info(sales_invoices)") as $c) echo $c["name"]."\n";'
```

Ini bukan formalitas: dokumen rencana sebelumnya pernah memuat kolom `description`
untuk `cash_receipts`/`cash_payments` yang tidak pernah ada (yang ada `notes`), dan
filter `due_from`/`due_to` yang tidak pernah ada di backend mana pun.

---

## 6. Test

147 file test. `tests/Feature/` disusun per modul: `Access`, `Accounting`,
`Architecture`, `Budget`, `CashBank`, `Dashboard`, `Demo`, `DocumentNumbering`,
`FixedAssets`, `Inventory`, `Journal`, `MasterData`, `OpeningBalance`, `Permissions`,
`Purchase`, `Reports`, `Sales`, `Settings`, `Setup`, `Shared`, `Tenant`.

Plus dua test lepas: `DocumentLifecycleMatrixTest.php` (matriks status × aksi lintas
modul) dan `ExampleTest.php`.

```bash
rtk php artisan test tests/Feature/MasterData      # jalankan yang relevan saja
rtk vendor/bin/pint --test                          # gaya kode
```

Suite penuh ±6 menit. Untuk perubahan sempit, **jangan** jalankan semuanya — pemilik
produk pernah menolak itu secara eksplisit.

Test tenant memakai base class per modul (mis. `MasterDataTestCase`) yang menyediakan
`setUpTenant()` → mengembalikan `headers` berisi token + `X-Company-ID`.

> **Catatan data uji:** migrasi tenant sudah menanam beberapa baris default (mis.
> payment terms). Assertion urutan/jumlah harus memperhitungkannya.

---

## 7. Galat & kode error

`ApiErrorCode` memuat konstanta kode galat beserta pesan defaultnya. Contoh yang sering
muncul: `VALIDATION_ERROR`, `PERMISSION_DENIED`, `COMPANY_ACCESS_DENIED`,
`X_COMPANY_ID_REQUIRED`, `TENANT_DATABASE_NOT_ACTIVE`, `DATABASE_ERROR`,
`DUPLICATE_ACCOUNT_CODE`, `INVALID_PARENT_ACCOUNT`, `MAX_ACCOUNT_DEPTH_EXCEEDED`,
`ACCOUNT_HAS_ACTIVE_CHILDREN`.

Saat menambah kode galat baru, daftarkan di `ApiErrorCode` supaya punya pesan default —
jangan mengirim string mentah dari service.
