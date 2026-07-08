# Fase 6 — FixedAssets · Reports · Dashboard

**Goal**: Migrasi modul tersisa. Report primitives sudah di `Shared/Reports` (Fase 0); di sini yang pindah adalah controller/request/service khusus Reports + `Requests/Concerns` report-filter. **Model tidak disentuh** (Fase 7).

Prasyarat baca: `00-conventions.md` §1–§3, §9.

## Prasyarat
```bash
cd laravel_backend
test -d app/Modules/Sales/Services && echo "Fase 5 OK" || echo "STOP: selesaikan Fase 5"
php artisan test 2>&1 | tail -3
```

## Transform: `00-conventions.md` §1.

---

### Modul FixedAssets (`app/Modules/FixedAssets/`)
**Controllers** (3): `FixedAssetCategoryController`, `FixedAssetController`, `FixedAssetReportController`.
**Requests** (6): `CapitalizeFixedAssetRequest`, `DisposeFixedAssetRequest`, `StoreFixedAssetCategoryRequest`, `StoreFixedAssetRequest`, `UpdateFixedAssetCategoryRequest`, `UpdateFixedAssetRequest`.
**Services** (2): `FixedAssetReportService`, `FixedAssetService`.

### Modul Reports (`app/Modules/Reports/`)
**Controllers** (9): `AccountLedgerDetailController`, `BalanceSheetController`, `BudgetComparisonController`, `CashFlowController`, `FinancialSummaryController`, `GeneralLedgerController`, `ProfitLossController`, `ReconciliationReportController`, `TrialBalanceController`.
**Requests** (8): `AccountLedgerDetailRequest`, `BalanceSheetRequest`, `CashFlowRequest`, `FinancialSummaryRequest`, `GeneralLedgerRequest`, `ProfitLossRequest`, `ReconciliationReportRequest`, `TrialBalanceRequest`.
**Requests/Concerns → modul** (`Http/Requests/Concerns/*` → `Modules/Reports/Requests/Concerns`, ns `App\Modules\Reports\Requests\Concerns`) — ⚠️ **trait**: `HasReportDateFilters.php`, `HasReportDimensionFilters.php`. Hanya dipakai request Reports (yang ikut pindah) → update `use` di 8 request di atas.
**Services** (16): `AccountLedgerDetailService`, `BalanceSheetService`, `CashFlowService`, `FinancialSummaryService`, `GeneralLedgerQueryService`, `LedgerBalanceCalculator`, `LedgerFilterValidator`, `ProfitLossService`, `ReconciliationReportService`, `ReportFilterService`, `ReportPeriodResolver`, `ReportQueryService`, `ReportResponseBuilder`, `ReportVisibilityService`, `TrialBalanceCalculator`, `TrialBalanceService`.
Config `report_visibility.php` tetap di `config/`. Report DTO & `HasReportVisibility` sudah di `Shared/Reports` (Fase 0).

### Modul Dashboard (`app/Modules/Dashboard/`)
**Controllers** (1): `DashboardController`.
**Requests**: tidak ada.
**Services** (1): `DashboardService`. (Memakai `App\Shared\Reports\Data\*` — sudah shared.)

---

## Update Routes/api.php
`app/Modules/{FixedAssets,Reports,Dashboard}/Routes/api.php` — ganti `use ...Controller`.

## Alias (tambah ke `ALIASES`)
Semua service (FixedAssets 2, Reports 16, Dashboard 1). Concerns adalah trait → tidak di-alias, sudah diupdate langsung.
```
App\Services\FixedAssets\FixedAssetService => App\Modules\FixedAssets\Services\FixedAssetService
App\Services\Reports\ProfitLossService     => App\Modules\Reports\Services\ProfitLossService
App\Services\Dashboard\DashboardService    => App\Modules\Dashboard\Services\DashboardService
... (semua service di atas)
```

## Checklist Verifikasi
- [ ] `php artisan route:list --path=api | wc -l` = baseline.
- [ ] `php artisan test` hijau.
- [ ] Endpoint: `/api/reports/profit-loss`, fixed-asset & dashboard endpoints merespons.
- [ ] `ls app/Http/Requests/Concerns` → hilang. `ls app/Http/Controllers/Api` → tinggal (kosong, dihapus di Fase 8). `ls app/Services` → tinggal folder yang belum? seharusnya semua domain service sudah pindah.

## Git Checkpoint
```
refactor(fixedassets,reports,dashboard): Fase 6 — move HTTP+service layers to modules
```
Update ledger (Fase 6 → ✅) & commit.

## Definition of Done
Semua modul non-model self-contained. `app/Http/Controllers/Api/*` (kecuali base `Controller.php`) & `app/Http/Requests/*` & `app/Services/*` (kecuali yang sudah ke Shared) kosong. Test hijau. **Model masih di `app/Models` & `app/Models/Tenant`** → Fase 7.
