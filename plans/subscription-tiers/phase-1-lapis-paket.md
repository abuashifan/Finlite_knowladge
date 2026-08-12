# Fase 1 — Lapis Paket di Jalur Permission

**Status: ✅ SELESAI 2026-08-11**

Menambahkan **lapis kedua** di atas sistem permission yang sudah ada, tanpa
memasang gerbang baru dan tanpa menyentuh satu pun rute. Setelah fase ini,
perilaku aplikasi **persis sama** — yang bertambah hanya kemampuan menjawab
"paket client ini membuka izin ini atau tidak", dan saklarnya masih mati.

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

## Dua sumbu yang TIDAK dilebur

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

## Urutan evaluasi yang dibangun

```
can(izin):
  1. paket membuka izin ini?      tidak → FEATURE_NOT_IN_PLAN   (owner pun ditolak)
  2. ada deny override?           ya    → PERMISSION_DENIED
  3. role punya '*'?              ya    → LOLOS                 (owner/admin melewati lapis 2)
  4. izin ada di set efektif?     tidak → PERMISSION_DENIED
```

Lapis 1 dievaluasi **sebelum** jalan pintas `*`, lapis 2 **sesudah**. Itu satu
satunya cara owner tetap kebal terhadap permission tapi tunduk pada paket.

### Ranjau yang diurus

`EffectivePermissionService::hasPermission()` berbunyi:

```php
return in_array($permissionKey, $this->getEffectivePermissionKeys($companyUser), true)
    || in_array('*', $this->rolePermissionsForCompanyUser($companyUser), true);
```

Baris kedua melewati corongnya sepenuhnya. Kalau lapis paket hanya dipasang di
dalam `getEffectivePermissionKeys()`, **owner dan admin tembus ke semua fitur** —
dan owner ada di setiap perusahaan. Gerbangnya akan tampak bekerja saat diuji
dengan role staff, lalu bocor total pada orang yang paling sering memakainya.

Jalan pintas itu **tidak dihapus** (ia benar untuk lapis 2); lapis 1 disisipkan
di atasnya, di `hasPermission()` maupun `explainPermission()`. Dikunci test
`test_owner_with_wildcard_is_still_bound_by_the_plan`.

## File yang disentuh

### Baru

| File | Isi |
|---|---|
| `app/Shared/Subscription/PlanOwnerResolver.php` | Rantai tunggal perusahaan → pemilik (`companies.created_by`) → paket, dengan jatuh ke `free`. |
| `app/Shared/Subscription/PlanPermissionResolver.php` | Lapis 1. `featuresFor()`, `blockedKeysFor()`, `allows()`, `allowedKeysFor()`, `enforcing()`, `flush()`. Cache per request. |
| `config/plan_features.php` | Saklar `enforce` + peta fitur → izin. |
| `tests/Feature/Subscription/PlanPermissionTest.php` | 14 test. |

### Diubah

| File | Perubahan |
|---|---|
| `app/Shared/Subscription/UserQuotaService.php` | `ownerOf()` privat dihapus, memakai `PlanOwnerResolver`. Import `Plan` ikut hilang. |
| `app/Shared/Subscription/CompanyQuotaService.php` | `planFor()` mendelegasi ke `PlanOwnerResolver`. `DEFAULT_PLAN_CODE` jadi alias ke konstanta di resolver. |
| `app/Shared/Permission/EffectivePermissionService.php` | Lapis 1 disisipkan di `hasPermission()` dan `explainPermission()` (sumber baru `not_in_plan`); `getEffectivePermissionKeys()` disaring; helper `planFeaturesFor()`, `planAllows()`, `planFilter()`, `companyOf()`. |
| `app/Shared/Permission/PermissionService.php` | `explain()` dan `planFeatures()` baru. |
| `app/Shared/Http/Middleware/EnsurePermission.php` | Memilih kode error lewat `errorCodeFor()`; alasannya ikut masuk metadata audit. |
| `app/Shared/Api/ApiErrorCode.php` + `config/api_errors.php` | `FEATURE_NOT_IN_PLAN`. |
| `app/Modules/Auth/Controllers/PermissionController.php` | Respons menambah `plan_features`. |
| `app/Shared/Providers/SharedServiceProvider.php` | `PlanPermissionResolver` didaftarkan singleton. |

**Nol rute disentuh. Nol middleware baru. Nol perubahan frontend.**

## Peta fitur

`config/plan_features.php`, enam entri, **daftar putih**: izin yang tidak
disebut selalu terbuka, supaya menambah modul baru tidak diam-diam mematikannya
di semua tier.

| Fitur | Izin yang digerbangi |
|---|---|
| `multi_warehouse` | `warehouses.create/edit/deactivate` |
| `audit_trail` | `audit.*` |
| `advanced_reports` | `reports.save`, `reports.multi_period` |
| `budgeting` | `budgets.submit/approve_head/approve_finance/manage` |
| `dimensions` | `departments.create/edit/deactivate`, `projects.create/edit/deactivate` |
| `user_permission` | `access.roles.create/edit/clone/deactivate/manage`, `access.permissions.assign/revoke/manage` |

`reports.save` dan `reports.multi_period` **belum ada** di
`config/permissions.php` — laporan tersimpan dan banding multi-periode belum
dibangun. Entrinya ditulis sekarang supaya petanya lengkap saat fitur itu datang;
sampai saat itu ia tidak berefek apa pun.

### Kenapa izin `.view` sengaja TIDAK digerbangi

Keputusan pemilik produk 2026-08-11: client yang turun tier **tetap boleh
membaca** data yang terlanjur dibuatnya. Client Enterprise yang sudah menandai
2.000 jurnal dengan departemen lalu turun ke Pro tidak boleh kehilangan angka itu
dari pandangan.

Jadi peta hanya memuat izin **tulis**. Yang tetap terbuka di semua tier:
`budgets.view`, `warehouses.view`, `departments.view`, `projects.view`,
`access.roles.view`, `access.permissions.view`, `reports.view`, dan seluruh
`access.users.*` + `access.invitations.*` (Basic dengan 3 user tetap harus bisa
mengundang orang — yang membatasi jumlahnya kuota user, bukan gerbang fitur).

Dikunci test `test_read_permissions_survive_a_tier_downgrade`.

`audit.*` adalah pengecualian: ia hanya punya `audit.view` dan isinya catatan
sistem, bukan data yang dibuat client. Digerbangi utuh.

## Deviasi dari rancangan

| | Rancangan | Yang dibangun | Kenapa |
|---|---|---|---|
| Bawaan `enforce` | §1a menulis `env(..., true)`, §1c menulis `false` | **`false`** | §1c yang benar dan konsisten dengan janji fase ini ("perilaku persis sama"). Menyalakannya hari ini akan menutup keenam fitur untuk **semua** tier — tidak ada satu pun paket di seeder yang mencantumkan `multi_warehouse`, `budgeting`, dst. Mengisinya pekerjaan Fase 2. |
| Bentuk resolver | `allowedKeysFor(Company): array` — daftar izin yang dibuka | **`blockedKeysFor(Company): array`** — pola izin yang ditutup; `allowedKeysFor(Company, array $kandidat)` menyaring daftar yang dikirim masuk | Menghitung "yang dibuka" butuh katalog izin lengkap, dan katalog itu tinggal di `EffectivePermissionService::allPermissionKeys()` — yang justru memanggil resolver ini. Menyuntikkannya balik = **ketergantungan melingkar** yang gagal saat container me-resolve. Bentuk "yang ditutup" juga lebih murah: daftar putih membuat himpunan tertutup selalu kecil. |

## Test

`tests/Feature/Subscription/PlanPermissionTest.php` — 14 test:

| Test | Mengunci |
|---|---|
| `..._passes_when_the_plan_includes_the_feature` | paket memuat → lolos (role `finance`, lapis 2 pasti lolos) |
| `..._is_refused_when_the_plan_omits_the_feature` | paket tidak memuat → ditolak, `source: not_in_plan` |
| `..._owner_with_wildcard_is_still_bound_by_the_plan` | **terpenting** — `*` tidak menembus lapis 1 |
| `..._owner_still_passes_layer_two_...` | owner tetap kebal permission untuk izin yang dibuka paket |
| `..._deny_override_still_beats_the_wildcard` | lapis 2 masih bekerja, dan alasannya tetap `user_override_deny` |
| `..._prefixes_outside_the_map_are_always_open` | daftar putih, bukan daftar hitam |
| `..._read_permissions_survive_a_tier_downgrade` | `.view` tidak ikut tertutup |
| `..._wildcard_pattern_closes_the_whole_prefix` | `audit.*` |
| `..._client_without_a_plan_falls_back_to_free` | jaring pengaman paket bawaan |
| `..._effective_permission_list_is_filtered_...` | daftar yang dikirim ke frontend sudah bersih |
| `..._permissions_endpoint_reports_the_plan_features` | `plan_features` terkirim |
| `..._route_refused_by_the_plan_answers_feature_not_in_plan` | 403 `FEATURE_NOT_IN_PLAN` lewat rute nyata |
| `..._route_refused_by_permission_still_answers_permission_denied` | pesan tidak salah alamat |
| `..._switch_off_restores_the_behaviour_from_before_this_phase` | `enforce = false` → identik |

## Verifikasi yang dijalankan

```
php artisan test              → 1196 test, 1191 lulus, 5 skip, 0 gagal
./vendor/bin/pint --dirty     → lulus
```

Janji fase ini terverifikasi: **0 gagal**, dan jumlah test yang lulus sebelum
fase ini (1174 saat Fase 0, ditambah 8 dari pekerjaan impor yang sedang berjalan
di tree yang sama) utuh — 14 tambahannya semua milik fase ini.

## Temuan sampingan (bukan bagian fase ini)

Di database test yang segar, tabel `permissions` hanya berisi **56 baris**, bukan
~240 dari `config/permissions.php`: yang mengisinya cuma tujuh migrasi `sync_*`
per modul, sementara katalog penuhnya hanya ditulis `PermissionSeeder`.
`EffectivePermissionService::allPermissionKeys()` berhenti di hasil database
begitu ia tidak kosong, jadi daftar izin efektif owner ikut terpotong ke 56 kunci
itu — `warehouses.view` dan kawan-kawan hilang dari respons
`GET /api/auth/permissions`.

Di produksi seeder itu dijalankan, jadi ini belum tentu bug hidup. Tapi **Fase 2
menyentuh editor role**, yang membaca katalog yang sama — sebaiknya diperiksa
lebih dulu di sana.

## Yang belum dikerjakan

- **Mengisi `plans.features`** dengan peta tier yang disetujui → Fase 2.
- **Menyalakan `enforce`** → Fase 2, setelah seeder terisi.
- **Frontend**: `plan_features` sudah dikirim tapi belum dibaca siapa pun. Editor
  role dan permukaan upsell → Fase 2.
