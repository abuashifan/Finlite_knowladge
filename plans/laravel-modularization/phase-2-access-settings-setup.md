# Fase 2 — Access · Settings · Setup

**Goal**: Migrasi modul yang bergantung ke Auth & Companies. **Model tidak disentuh** (Fase 7).

Prasyarat baca: `00-conventions.md` §1–§3, §9.

## Prasyarat
```bash
cd laravel_backend
grep -q "Fase 1" ../Finlite_knowladge/plans/laravel-modularization/README.md   # cek ledger manual: Fase 1 = ✅
test -d app/Modules/Auth/Controllers && echo "Fase 1 OK" || echo "STOP: selesaikan Fase 1"
php artisan test 2>&1 | tail -3
```

## Transform: `00-conventions.md` §1.

---

### Modul Access (`app/Modules/Access/`)
**Controllers**: `AccessAuditController`, `CompanyInvitationAccessController`, `CompanyUserAccessController`, `PermissionCatalogController`, `RoleAccessController`.
**Requests**: `CopyAccessRequest`, `InviteCompanyUserRequest`, `StoreRoleRequest`, `UpdateCompanyUserPermissionRequest`, `UpdateCompanyUserRoleRequest`, `UpdateRolePermissionsRequest`, `UpdateRoleRequest`.
**Services**: tidak ada dir `Services/Access`. Access memakai `Shared/Permission` + `Modules/Companies/Services/CompanyUserAssignmentService` (via alias/namespace baru).

### Modul Settings (`app/Modules/Settings/`)
**Controllers**: `CompanySettingController`.
**Requests**: `UpdateCompanyAccountingSettingRequest`, `UpdateCompanyModuleSettingRequest`, `UpdateCompanyTransactionDefaultRequest`.
**Services**: `CompanySettingService`.
Config terkait (tetap di `config/`): —

### Modul Setup (`app/Modules/Setup/`)
**Controllers**: `SetupWizardController`.
**Requests**: `ReopenSetupRequest`, `UpdateSetupCurrentStepRequest`, `ValidateSetupStepRequest`.
**Services**: `SetupWizardService`.

---

## Update Routes/api.php
Ganti `use ...Controller` di `app/Modules/{Access,Settings,Setup}/Routes/api.php` → `App\Modules\{X}\Controllers\...`.

## Alias (tambah ke `ALIASES`)
Services:
```
App\Services\Settings\CompanySettingService => App\Modules\Settings\Services\CompanySettingService
App\Services\Setup\SetupWizardService       => App\Modules\Setup\Services\SetupWizardService
```
Controller/Request: cek grep lintas modul, tambah bila perlu.

## Checklist Verifikasi
- [ ] `php artisan route:list --path=api | wc -l` = baseline.
- [ ] `php artisan test` hijau.
- [ ] Endpoint: `/api/access/users`, `/api/settings/company`, endpoint setup wizard merespons.

## Git Checkpoint
```
refactor(access,settings,setup): Fase 2 — move HTTP+service layers to modules
```
Update ledger (Fase 2 → ✅) & commit.

## Definition of Done
Access/Settings/Setup self-contained; folder lama kosong; test hijau.
