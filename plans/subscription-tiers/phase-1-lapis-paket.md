# Fase 1 — Lapis Paket di Jalur Permission

**Status: ⬜ Belum dikerjakan. Belum disetujui.**

Menambahkan **lapis kedua** di atas sistem permission yang sudah ada, tanpa
memasang gerbang baru dan tanpa menyentuh satu pun rute. Setelah fase ini,
perilaku aplikasi harus **persis sama** — yang bertambah hanya kemampuan
menjawab "paket client ini membuka izin ini atau tidak".

Rancangan ini menggantikan rencana `FeatureGateService` + middleware `feature:`
yang ditulis 2026-08-11 pagi. Alasannya di bawah.

## Penemuan yang mengubah rancangan

Audit rute 2026-08-11:

| | |
|---|---|
| Total rute API | 441 |
| **Sudah memakai `permission:`** | **421 (95,5%)** |
| Memakai `company.access` | 424 |
| Tanpa `permission:` | 20 |

Kedua puluh yang tidak terjaga persis yang memang tidak boleh terjaga:
`api/health`, `api/auth/*`, seluruh `api/admin/*`, `api/companies` +
`api/companies/select` (dipanggil sebelum ada perusahaan aktif),
`api/tenant-context-test`, dan `api/settings/company/workflow`.

**Seluruh permukaan bisnis aplikasi ini sudah punya gerbang.** Yang belum ada
bukan gerbangnya — hanya alasan kedua untuk menutupnya. Memasang middleware
`feature:` berarti membangun gerbang kedua di sebelah gerbang yang sudah ada.

Namespace permission pun sudah sejajar dengan modul:

```
access  audit  budgets  cash_bank  coa  contacts  dashboard  departments
fiscal_year  fixed_assets  inventory  journal  master_data  opening_balance
payment_terms  period_end  products  projects  purchase  reports  sales
settings  setup  units  warehouses
```

## Dua sumbu yang TIDAK boleh dilebur

Ini keputusan rancangan terpenting di fase ini, ditegaskan pemilik produk
2026-08-11: *"Budget itu fitur dari tipe client, dan permission user itu tentang
peran user tambahan di data perusahaan, bukan user pemilik atau administrator."*

| | **Lapis 1 — Paket** | **Lapis 2 — Permission** |
|---|---|---|
| Menjawab | "Perusahaan ini punya Budget?" | "Si Andi boleh menyentuh Budget?" |
| Milik | client yang berlangganan | perusahaan |
| Berlaku ke | **semua orang**, termasuk owner & admin | hanya user tambahan |
| Owner / admin (`['*']`) | **ikut terikat** | dikecualikan |
| Diubah oleh | pemilik aplikasi (area admin) | owner/admin perusahaan |
| Disimpan di | `users.plan_id` → `plans.features` | `roles`, `role_permissions`, `company_user_permission_overrides` |
| Kalau menolak | `FEATURE_NOT_IN_PLAN` → "hubungi penyedia aplikasi" | `PERMISSION_DENIED` → "hubungi admin perusahaan" |

Dari 8 role, hanya `owner` dan `admin` yang `['*']`. Enam sisanya — `finance`
(38 izin), `accountant` (27), `sales` (46), `purchasing` (39), `warehouse` (32),
`viewer` (3) — adalah "user tambahan" yang dimaksud.

**Konsekuensinya: irisan buta salah.** Menulis
`efektif = (role + allow − deny) ∩ paket` memang menghasilkan angka yang benar
untuk owner (`semua ∩ paket = paket`), tapi mencapainya lewat konsep yang keliru,
dan kekeliruan itu bocor di tiga tempat: pesan error, siapa yang harus dihubungi,
dan editor role. Yang benar adalah **urutan evaluasi**, bukan irisan.

## Urutan evaluasi

```
can(izin):
  1. paket membuka izin ini?      tidak → FEATURE_NOT_IN_PLAN   (owner pun ditolak)
  2. ada deny override?           ya    → PERMISSION_DENIED
  3. role punya '*'?              ya    → LOLOS                 (owner/admin melewati lapis 2)
  4. izin ada di set efektif?     tidak → PERMISSION_DENIED
```

Lapis 1 dievaluasi **sebelum** jalan pintas `*`, lapis 2 **sesudah**. Itu satu
satunya cara owner tetap kebal terhadap permission tapi tunduk pada paket.

### Ranjau yang wajib diurus

`EffectivePermissionService::hasPermission()` (baris 50-57) berbunyi:

```php
return in_array($permissionKey, $this->getEffectivePermissionKeys($companyUser), true)
    || in_array('*', $this->rolePermissionsForCompanyUser($companyUser), true);
```

Baris kedua melewati corongnya sepenuhnya. Kalau lapis paket hanya dipasang di
dalam `getEffectivePermissionKeys()`, **owner dan admin tembus ke semua fitur** —
dan owner ada di setiap perusahaan. Gerbangnya akan tampak bekerja saat diuji
dengan role staff, lalu bocor total pada orang yang paling sering memakainya.

Jalan pintas itu **tidak dihapus** (ia benar untuk lapis 2), tapi lapis 1 harus
disisipkan di atasnya. `explainPermission()` punya jalan pintas serupa dan perlu
perlakuan sama, plus sumber baru `not_in_plan`.

## Pekerjaan

### 1a. Peta fitur → izin

`config/plan_features.php` — pemetaan prefix, bukan kosakata baru:

```php
return [
    'enforce'  => env('PLAN_FEATURES_ENFORCE', true),

    'features' => [
        // Pro ke atas
        'multi_warehouse'  => [
            'warehouses.create', 'warehouses.edit', 'warehouses.deactivate',
        ],
        'audit_trail'      => ['audit.*'],   // hanya punya `audit.view`, tidak bisa dipisah
        'advanced_reports' => ['reports.save', 'reports.multi_period'],  // ← kunci BARU

        // Enterprise
        'budgeting'        => [
            'budgets.submit', 'budgets.approve_head', 'budgets.approve_finance', 'budgets.manage',
        ],
        'dimensions'       => [
            'departments.create', 'departments.edit', 'departments.deactivate',
            'projects.create', 'projects.edit', 'projects.deactivate',
        ],
        'user_permission'  => [
            'access.roles.create', 'access.roles.edit', 'access.roles.clone',
            'access.roles.deactivate', 'access.roles.manage',
            'access.permissions.assign', 'access.permissions.revoke', 'access.permissions.manage',
        ],
    ],
];
```

Enam entri. Prefix yang **tidak** disebut selalu terbuka — daftar putih, bukan
daftar hitam, supaya menambah modul baru tidak diam-diam mematikannya.

### Kenapa izin `.view` sengaja TIDAK ikut digerbangi

Keputusan pemilik produk 2026-08-11: client yang turun tier **tetap boleh
membaca** data yang terlanjur dibuatnya. Client Enterprise yang sudah menandai
2.000 jurnal dengan departemen lalu turun ke Pro tidak boleh kehilangan angka itu
dari pandangan.

Jadi peta hanya memuat izin **tulis**. Yang tetap terbuka di semua tier:

| Izin | Kenapa terbuka |
|---|---|
| `budgets.view` | Membaca anggaran yang sudah dibuat |
| `warehouses.view`, `departments.view`, `projects.view` | idem |
| `access.roles.view`, `access.permissions.view` | Melihat role preset yang berlaku |
| `access.users.*`, `access.invitations.*` | **Semua tier** perlu menambah anggota timnya — Basic dengan 3 user tetap harus bisa mengundang orang |
| `reports.view` | Laporan standar |

Konsekuensi yang harus diterima: client Basic yang belum pernah punya anggaran
tetap bisa membuka layar anggaran — dan melihatnya kosong dengan tombol buat
yang mati. Itu justru permukaan upsell yang jujur.

Konsekuensi untuk frontend: modul digerbangi **ditampilkan** kalau paketnya
memuatnya **atau** perusahaan punya data lamanya. Hitungan "punya data lama" itu
ikut dikirim sekali saat perusahaan dipilih, bukan dihitung tiap render.

`audit.*` adalah pengecualian: ia hanya punya `audit.view` dan isinya catatan
sistem, bukan data yang dibuat client. Digerbangi utuh.

### 1b. Resolver

`app/Shared/Subscription/PlanPermissionResolver.php`:

```php
public function allowedKeysFor(Company $company): array;  // izin yang dibuka paket
public function allows(Company $company, string $key): bool;
public function featuresFor(Company $company): array;     // untuk dikirim ke frontend
```

Rantainya: perusahaan → pemilik (`companies.created_by`) → `users.plan_id` →
`plans.features` → prefix → daftar izin.

**Rantai "perusahaan → pemilik → paket" sudah ada dua kali** (`CompanyQuotaService`,
`UserQuotaService::ownerOf()`). Fase ini tidak boleh menambah salinan ketiga —
naikkan `ownerOf()` ke `app/Shared/Subscription/PlanOwnerResolver.php` lebih
dulu, lalu ketiganya memakainya.

### 1c. Saklar transisi

`config('plan_features.enforce')`, bawaan **false**.

Selama false, `allowedKeysFor()` mengembalikan seluruh daftar izin — perilaku
persis seperti sekarang. Ini yang membuat fase ini netral, dan yang membuat
peluncuran di Fase 2 bisa dibatalkan tanpa deploy ulang.

### 1d. Penyisipan

Di `EffectivePermissionService`:

- `getEffectivePermissionKeys()` — hasilnya diiris dengan `allowedKeysFor()`,
  supaya daftar yang dikirim ke frontend sudah bersih
- `hasPermission()` — lapis 1 disisipkan **di atas** jalan pintas `*`
- `explainPermission()` — sama, plus `source: 'not_in_plan'`

`EnsurePermission` membaca `explainPermission()` untuk memilih kode error:
`FEATURE_NOT_IN_PLAN` (403) atau `PERMISSION_DENIED` (403). Tidak ada rute yang
disentuh.

### 1e. Dua daftar ke frontend

`GET /api/auth/permissions` mengirim `permissions` (hasil irisan, dipakai guard)
**plus** daftar fitur paket. Tanpa yang kedua, UI tidak bisa membedakan "minta ke
admin perusahaan" dari "naikkan paket" — dan kehilangan satu-satunya tempat wajar
untuk menawarkan upgrade.

### 1f. Cache per request

`can()` menembak database, dan `EnsurePermission` memanggilnya tiap request.
Menambah resolusi paket berarti dua query lagi per pemeriksaan. Hasil
`allowedKeysFor()` di-cache selama satu request. Belum ada cache sama sekali hari
ini, jadi ini sekalian perbaikan.

## Test

`tests/Feature/Subscription/PlanPermissionTest.php`:

- paket memuat fitur → izinnya lolos
- paket tidak memuat → 403 `FEATURE_NOT_IN_PLAN`
- **owner (`*`) tetap ditolak** oleh lapis paket — test terpenting di fase ini
- owner tetap lolos lapis permission untuk izin yang dibuka paket
- deny override tetap menang atas `*`
- prefix di luar peta selalu terbuka
- client tanpa paket → jatuh ke Free
- `enforce = false` → seluruh perilaku identik dengan sebelum fase ini

Plus satu test yang menjaga janji fase ini: dengan `enforce = false`, jumlah test
yang lulus di seluruh suite harus **sama persis** seperti sebelumnya.

## Verifikasi

```bash
php artisan test          # wajib 0 gagal — fase ini tidak boleh mengubah perilaku
./vendor/bin/pint --dirty
```

## Risiko

- **Menaikkan `ownerOf()` menyentuh dua penegakan produksi** (kuota perusahaan &
  kuota user). Refactor murni; `CompanyQuotaTest` dan `UserQuotaTest` adalah
  jaringnya. Jangan ubah perilaku sambil memindahkan — dua langkah, dua commit.
- **`ModuleBoundariesTest`** melarang `app/Shared/` bergantung ke `app/Modules/`.
  Semua berkas fase ini tinggal di `Shared`; perhatikan arah import.
