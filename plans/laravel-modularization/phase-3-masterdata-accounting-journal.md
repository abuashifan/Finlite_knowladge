# Fase 3 — MasterData · Accounting · Journal

**Goal**: Migrasi modul foundational (menyediakan data & posting ke downstream). **Model tidak disentuh** (Fase 7) — meski model tenant (ChartOfAccount, Product, JournalEntry, dll) "milik" modul ini, pemindahannya ditunda ke Fase 7.

Prasyarat baca: `00-conventions.md` §1–§3, §9.

## Prasyarat
```bash
cd laravel_backend
test -d app/Modules/Access/Controllers && echo "Fase 2 OK" || echo "STOP: selesaikan Fase 2"
php artisan test 2>&1 | tail -3
```

## Transform: `00-conventions.md` §1.

---

### Modul MasterData (`app/Modules/MasterData/`)
**Controllers** (10): `AccountMappingController`, `ChartOfAccountController`, `ContactController`, `DepartmentController`, `PaymentTermController`, `ProductCategoryController`, `ProductController`, `ProjectController`, `UnitController`, `WarehouseController`.
**Requests** (19): `StoreChartOfAccountRequest`, `StoreContactRequest`, `StoreDepartmentRequest`, `StorePaymentTermRequest`, `StoreProductCategoryRequest`, `StoreProductRequest`, `StoreProjectRequest`, `StoreUnitRequest`, `StoreWarehouseRequest`, `UpdateAccountMappingRequest`, `UpdateChartOfAccountRequest`, `UpdateContactRequest`, `UpdateDepartmentRequest`, `UpdatePaymentTermRequest`, `UpdateProductCategoryRequest`, `UpdateProductRequest`, `UpdateProjectRequest`, `UpdateUnitRequest`, `UpdateWarehouseRequest`.
**Services** (10): `AccountMappingStorageService`, `ChartOfAccountService`, `ContactService`, `DepartmentService`, `PaymentTermService`, `ProductCategoryService`, `ProductService`, `ProjectService`, `UnitService`, `WarehouseService`.
> Catatan: `AccountMappingController` memakai `Shared/AccountMapping` (service inti sudah shared). `AccountMappingStorageService` (penyimpanan per-tenant) tetap milik MasterData.

### Modul Accounting (`app/Modules/Accounting/`)
**Controllers** (5): `AccountMappingHealthController`, `FiscalYearClosingController`, `FiscalYearStatusController`, `PeriodEndController`, `PeriodLockController`.
**Requests** (5): `CloseFiscalYearRequest`, `PeriodEndPeriodRequest`, `ReopenFiscalYearRequest`, `ReopenPeriodEndRequest`, `UpdatePeriodLockRequest`.
**Services** (6): `AccountMappingHealthService`, `AnnualClosingGateService`, `FiscalYearClosingService`, `FiscalYearService`, `PeriodEndService`, `PeriodLockService`.
> `FiscalYearClosingService` memakai `App\Shared\Reports\Data\*` (sudah shared sejak Fase 0).

### Modul Journal (`app/Modules/Journal/`)
**Controllers** (1): `JournalEntryController`.
**Requests** (5): `ApproveJournalEntryRequest`, `PostJournalEntryRequest`, `StoreJournalEntryRequest`, `UpdateJournalEntryRequest`, `VoidJournalEntryRequest`.
**Services** (6): `JournalEntryService`, `JournalLineNormalizer`, `JournalPostingService`, `JournalValidationService`, `JournalVoidService`, `SystemJournalBuilder`.

---

## Update Routes/api.php
Ganti `use ...Controller` di `app/Modules/{MasterData,Accounting,Journal}/Routes/api.php`.

## Alias (tambah ke `ALIASES`)
Semua **service** modul ini (dipakai lintas modul — mis. `JournalPostingService`, `ChartOfAccountService`, `FiscalYearService`, `PeriodLockService` dipakai Sales/Purchase/CashBank/Inventory). Tambah baris `App\Services\{X}\Y => App\Modules\{X}\Services\Y` untuk semua 22 service di atas. Contoh:
```
App\Services\Journal\JournalPostingService => App\Modules\Journal\Services\JournalPostingService
App\Services\MasterData\ChartOfAccountService => App\Modules\MasterData\Services\ChartOfAccountService
App\Services\Accounting\PeriodLockService  => App\Modules\Accounting\Services\PeriodLockService
...
```

## Checklist Verifikasi
- [ ] `php artisan route:list --path=api | wc -l` = baseline.
- [ ] `php artisan test` hijau.
- [ ] Endpoint: `/api/master-data/products`, `/api/journals`, fiscal-year/period endpoints merespons.

## Git Checkpoint
```
refactor(masterdata,accounting,journal): Fase 3 — move HTTP+service layers to modules
```
Update ledger (Fase 3 → ✅) & commit.

## Definition of Done
Ketiga modul self-contained (kecuali model, Fase 7); folder lama kosong; test hijau.
