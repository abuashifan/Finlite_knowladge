# Fase 1 — Auth · Companies · Tenant

**Goal**: Migrasi 3 modul pertama ke self-contained (Controllers/Requests/Services). Menetapkan pola untuk fase modul berikutnya. **Model tidak disentuh** (Fase 7).

Prasyarat baca: `00-conventions.md` §1 (transform modul), §2 (langkah pindah), §3 (alias), §9.

## Prasyarat (verifikasi titik awal)
```bash
cd laravel_backend
test -d app/Shared/Api && test -f app/Providers/AliasServiceProvider.php && echo "Fase 0 OK" || echo "STOP: selesaikan Fase 0 dulu"
php artisan test 2>&1 | tail -3   # baseline hijau
```

## Transform (berlaku semua modul di fase ini)
Lihat `00-conventions.md` §1: Controllers/Requests/Services `App\Http\Controllers\Api\{X}` / `App\Http\Requests\{X}` / `App\Services\{X}` → `App\Modules\{X}\{Controllers|Requests|Services}`. Untuk tiap file dipindah: `git mv` + edit `namespace`.

---

### Modul Auth (`app/Modules/Auth/`)
**Controllers** (`Controllers/Api/Auth` → `Modules/Auth/Controllers`): `AuthController`, `PermissionController`.
**Requests** (`Requests/Auth` → `Modules/Auth/Requests`): `LoginRequest`, `RegisterRequest`.
**Services**: tidak ada (evaluasi permission sudah di `Shared/Permission` sejak Fase 0). `PermissionController` memakai `App\Shared\Permission\*`.

### Modul Companies (`app/Modules/Companies/`)
**Controllers**: `CompanyController`, `MyCompaniesController`.
**Requests**: tidak ada.
**Services** (`Services/Companies` → `Modules/Companies/Services`): `CompanyUserAssignmentService`.

### Modul Tenant (`app/Modules/Tenant/`)
**Controllers**: `TenantContextTestController`.
**Requests**: tidak ada.
**Services**: tidak ada (service tenant sudah di `Shared/Tenant` sejak Fase 0). Controller memakai `App\Shared\Tenant\TenantContext`.

---

## Update Routes/api.php (WAJIB per modul)
Ganti baris `use` controller di file route modul → namespace `App\Modules\{X}\Controllers\...`:
```bash
# contoh Auth:
grep -n "use App\\\\Http\\\\Controllers\\\\Api\\\\Auth" app/Modules/Auth/Routes/api.php
```
Lakukan untuk `Auth`, `Companies`, `Tenant`.

## Alias (tambah ke `AliasServiceProvider::ALIASES`)
Tambah untuk **service** yang dipindah (bisa direferensikan lintas modul/test):
```
App\Services\Companies\CompanyUserAssignmentService => App\Modules\Companies\Services\CompanyUserAssignmentService
```
Controller & Request: tambahkan alias **hanya jika** grep menemukan referensi di luar modulnya:
```bash
grep -rln "App\\\\Http\\\\Controllers\\\\Api\\\\Auth\\\\AuthController" app/ tests/
```
(Controller/Request umumnya self-contained → tak perlu alias. Feature test memanggil URL, bukan class.)

## Checklist Verifikasi
- [ ] `php artisan route:list --path=api | wc -l` = baseline.
- [ ] `php artisan test` hijau (baseline).
- [ ] Endpoint: `/api/auth/login`, `/api/companies`, `/api/tenant-context-test` merespons.
- [ ] `ls app/Http/Controllers/Api/Auth app/Http/Controllers/Api/Companies app/Http/Controllers/Api/Tenant` → kosong/hilang.

## Git Checkpoint
```
refactor(auth,companies,tenant): Fase 1 — move HTTP+service layers to modules
```
Update ledger `README.md` (Fase 1 → ✅) & commit.

## Definition of Done
Auth/Companies/Tenant berisi Controllers/Requests/Services sendiri; folder lama di `Http/Controllers/Api/{X}`, `Http/Requests/{X}`, `Services/{X}` untuk 3 modul ini kosong; test hijau.
