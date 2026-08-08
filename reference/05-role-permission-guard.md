# Role, Permission, dan Guard

Aturan project: **jangan pernah merender tombol aksi tanpa cek permission**, dan
jangan pernah menaruh logika permission langsung di controller.

---

## 1. Sumber kebenaran

| Lapis | Lokasi | Isi |
|---|---|---|
| Katalog | `config/permissions.php` | **240 permission**, **8 role** |
| Tabel central | `roles`, `permissions`, `role_permissions` | role & permission yang benar-benar tersimpan |
| Override per user | `company_user_permission_overrides` | `allow` / `deny` per user per perusahaan |
| Resolver | `app/Shared/Permission/PermissionService` + `EffectivePermissionService` | menjawab "boleh atau tidak" |

**Permission bersifat per perusahaan.** User yang sama bisa `owner` di perusahaan A dan
`viewer` di perusahaan B. Karena itu frontend memanggil `GET /api/auth/permissions`
setiap kali perusahaan dipilih.

---

## 2. Delapan role

| Role | Permission | Ringkas |
|---|---|---|
| `owner` | `*` | semua |
| `admin` | `*` | semua |
| `sales` | 46 | siklus penjualan + master data terkait |
| `purchasing` | 39 | siklus pembelian |
| `finance` | 38 | jurnal, kas & bank, laporan, tahun fiskal, anggaran |
| `warehouse` | 32 | persediaan, penerimaan/pengiriman barang |
| `accountant` | 27 | jurnal + master data, tanpa hak posting kas/bank |
| `viewer` | 3 | baca saja |

> `owner` dan `admin` memakai wildcard `*`, jadi **semua tombol tampil untuk mereka**.
> Menguji visibilitas permission dengan akun demo (`admin@example.com`) **tidak akan
> membuktikan apa pun** — pakai role lain.
>
> Perhatikan juga: `finance` dan `accountant` punya `coa.view/create/edit` tapi **tidak**
> `coa.deactivate`. Tombol nonaktifkan memang seharusnya hilang untuk mereka.

---

## 3. 240 permission menurut kelompok

| Kelompok | Jml | Kelompok | Jml |
|---|---|---|---|
| `sales.*` | 54 | `fiscal_year.*` | 6 |
| `purchase.*` | 47 | `settings.*` | 6 |
| `inventory.*` | 25 | `opening_balance.*` | 6 |
| `access.*` | 21 | `journal.*` | 6 |
| `fixed_assets.*` | 11 | `budgets.*` | 5 |
| `cash_bank.*` | 7 | `setup.*` | 5 |
| `coa.*` `contacts.*` `products.*` `units.*` `warehouses.*` `payment_terms.*` `departments.*` `projects.*` | 4 masing-masing | `period_end.*` | 3 |
| `master_data.*` `reports.*` | 2 masing-masing | `dashboard.*` `audit.*` | 1 masing-masing |

Polanya:
- **Master data**: `<entitas>.view|create|edit|deactivate` (tidak ada `delete` —
  penonaktifan menggantikan penghapusan).
- **Transaksi**: `<modul>.view|create|edit|void|approve|post` di tingkat modul, lalu
  per dokumen `<modul>.<dokumen>.<aksi>` dengan aksi khusus domain
  (`convert`, `confirm`, `ship`, `deliver`, `issue`, `receive`, `refund`, `finalize`, …).

---

## 4. Cara permission dihitung (`EffectivePermissionService`)

```
efektif = ( permission_role  ∪  override_allow )  −  override_deny
```

Dua hal yang penting:

1. **`deny` selalu menang** atas role maupun `allow`.
2. Role berwildcard `*` diperluas menjadi seluruh katalog permission saat dihitung,
   tapi `hasPermission()` juga memeriksa `*` secara langsung — jadi wildcard tetap
   lolos walau katalognya berubah.

`explainPermission()` mengembalikan sumber keputusan (`user_override_deny`,
`user_override_allow`, role, …) — berguna untuk mendiagnosis "kenapa tombol ini hilang".

---

## 5. Penegakan di backend

Middleware alias `permission` (`EnsurePermission`), didaftarkan di `bootstrap/app.php`:

```php
Route::post('/journals/{id}/post', [JournalController::class, 'post'])
    ->middleware(['auth:sanctum', 'company.access', 'permission:journal.post']);
```

- Beberapa permission dipisah `|` = **salah satu cukup**:
  `permission:fiscal_year.lock_manage|fiscal_year.view`
- Ditolak → **`403` dengan `code: PERMISSION_DENIED`** dan `meta.permission` berisi
  permission yang diminta.
- Penolakan **dicatat ke audit log** (`AuditEvent::PERMISSION_DENIED`). Kegagalan
  pencatatan audit sengaja tidak memblokir request.

Urutan middleware yang benar: `auth:sanctum` → `company.access` → `permission:*`.
`company.access` harus lebih dulu karena permission diambil dari `TenantContext`.

---

## 6. Penegakan di frontend

### `hooks/usePermission.ts`

```ts
const { can, canAny, canAll, permissionsLoaded } = usePermission()
```

`hasPermission()` mencoba beberapa kandidat berurutan:

1. permission apa adanya
2. versi dengan `-` diganti `_`
3. alias di `PERMISSION_ALIASES`

Wildcard `*` di daftar permission user selalu lolos.

> **Kenapa ada alias:** penamaan frontend dan backend berbeda dalam beberapa kasus —
> frontend memakai `master-data.coa.create` sementara backend `coa.create`;
> `sales.delivery-orders.update` dipetakan ke `sales.delivery_orders.edit`;
> `inventory.opnames.view` ke `inventory.opname.view`.
> **Saat menambahkan permission baru, periksa apakah butuh entri alias** — kalau tidak,
> tombolnya akan hilang diam-diam padahal user berhak.

### `components/shared/PermissionGuard.tsx`

```tsx
<PermissionGuard permission="master-data.coa.create">
  <Button>Tambah Akun</Button>
</PermissionGuard>

<PermissionGuard permission={['a', 'b']} mode="all" fallback={<Locked />}>…</PermissionGuard>
```

`mode`: `'any'` (default) atau `'all'`. `fallback` default `null` (elemen hilang).

`BulkAction.permission` dan `RibbonItem.permission` dibungkus otomatis dengan guard ini —
cukup isi field-nya.

---

## 7. Guard rute (`src/router/guards.tsx`)

Tiga guard, dan **`ProtectedRoute` juga yang merender `AppShell`**:

| Guard | Syarat | Gagal → |
|---|---|---|
| `ProtectedRoute` | `token` | `/login` (membawa `state.from`) |
| | `requireCompany` → `activeCompanyId` | `/select-company` |
| | `requireOnboarding` → onboarding perusahaan selesai | `/onboarding` |
| | `permission` → `hasPermission` | `/403` |
| `CompanySelectionGuard` | `token` saja, **di luar** `AppShell` | `/login` |
| `OnboardingGuard` | `token` + `activeCompanyId`, di luar `AppShell` | `/login` atau `/select-company` |

Pemakaian di route modul — tiap modul mendefinisikan **helper lokal** supaya guard tidak
ditulis ulang di setiap baris (`guard`, di beberapa modul bernama `wrap`):

```tsx
const guard = (permission: string, children: React.ReactNode) => (
  <ProtectedRoute permission={permission} requireCompany requireOnboarding>
    {children}
  </ProtectedRoute>
)

export const masterDataRoutes = [
  { path: '/master-data/coa',        element: guard('master-data.coa.view',   <CoaListPage />) },
  { path: '/master-data/coa/create', element: guard('master-data.coa.create', <CoaFormPage />) },
  { path: '/master-data/coa/:id',    element: guard('master-data.coa.view',   <CoaFormPage />) },
]
```

Perhatikan: **rute `create` memakai permission `create`**, bukan `view`. Ikuti pola ini.

> ⚠️ **Route yang tidak dibungkus `ProtectedRoute` berada di luar `AppShell`.**
> Pernah terjadi: `<Navigate>` telanjang di router membuat shell unmount lalu mount
> berulang setiap effect memaksa URL kembali ke path tab. Kalau butuh redirect di dalam
> aplikasi, bungkus dengan guard yang sama seperti rute lain.

---

## 8. Daftar periksa saat menambah endpoint + tombolnya

1. Tambahkan permission ke `config/permissions.php` **dan** ke role yang berhak.
2. Pasang `permission:<key>` di rute backend.
3. Tambah feature test untuk **berhak** dan **tidak berhak** (`tests/Feature/Permissions/`).
4. Frontend: bungkus tombolnya dengan `PermissionGuard`.
5. Kalau penamaannya berbeda dari backend, tambahkan entri `PERMISSION_ALIASES`.
6. Kalau ini halaman baru, isi `permission` di route dan di `RibbonItem`.
7. Uji dengan role **selain** `owner`/`admin` — keduanya wildcard dan akan selalu lolos.
