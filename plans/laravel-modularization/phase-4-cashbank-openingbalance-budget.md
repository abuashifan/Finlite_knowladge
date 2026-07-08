# Fase 4 — CashBank · OpeningBalance · Budget

**Goal**: Migrasi modul dependensi moderat. Fase ini juga memindahkan **value object domain** `Support/OpeningBalance` ke modulnya. **Model tidak disentuh** (Fase 7).

Prasyarat baca: `00-conventions.md` §1–§3, §9.

## Prasyarat
```bash
cd laravel_backend
test -d app/Modules/Journal/Services && echo "Fase 3 OK" || echo "STOP: selesaikan Fase 3"
php artisan test 2>&1 | tail -3
```

## Transform: `00-conventions.md` §1.

---

### Modul CashBank (`app/Modules/CashBank/`)
**Controllers** (6): `BankReconciliationController`, `BankTransferController`, `CashBankAccountController`, `CashBankReportController`, `CashPaymentController`, `CashReceiptController`.
**Requests** (8): `CashBankAccountStatementRequest`, `CashBankActionRequest`, `MarkBankReconciliationLinesRequest`, `StoreBankReconciliationRequest`, `StoreBankTransferRequest`, `StoreCashPaymentRequest`, `StoreCashReceiptRequest`, `UpdateBankReconciliationRequest`.
**Services** (6): `BankReconciliationService`, `BankTransferService`, `CashBankAccountService`, `CashBankReportService`, `CashPaymentService`, `CashReceiptService`.

### Modul OpeningBalance (`app/Modules/OpeningBalance/`)
**Controllers** (1): `OpeningBalanceController`.
**Requests** (4): `ReopenOpeningBalanceRequest`, `ReplaceOpeningBalanceLinesRequest`, `StoreOpeningBalanceBatchRequest`, `UpdateOpeningBalanceBatchRequest`.
**Services** (3): `OpeningBalanceBatchService`, `OpeningBalanceService`, `OpeningBalanceValidator`.
**Support → modul** (`Support/OpeningBalance/*` → `app/Modules/OpeningBalance/Support/`, ns `App\Modules\OpeningBalance\Support`):
- `OpeningBalanceBatch.php`, `OpeningBalanceLine.php`, `OpeningBalanceType.php`
Config `opening_balance.php` tetap di `config/`.

### Modul Budget (`app/Modules/Budget/`)
**Controllers** (3): `BudgetConsolidationController`, `BudgetPeriodController`, `BudgetSubmissionController`.
**Requests** (7): `BudgetApprovalRequest`, `BudgetComparisonRequest`, `StoreBudgetPeriodRequest`, `StoreBudgetSubmissionRequest`, `UpdateBudgetLinesRequest`, `UpdateBudgetPeriodRequest`, `UpdateBudgetSubmissionRequest`.
**Services** (5): `BudgetComparisonService`, `BudgetConsolidationService`, `BudgetPeriodService`, `BudgetSubmissionService`, `BudgetWarningService`.

---

## Update Routes/api.php
`app/Modules/{CashBank,OpeningBalance,Budget}/Routes/api.php` — ganti `use ...Controller`.

## Alias (tambah ke `ALIASES`)
Semua service (17) + value object `Support/OpeningBalance`:
```
App\Services\CashBank\CashBankAccountService => App\Modules\CashBank\Services\CashBankAccountService
... (semua service CashBank/OpeningBalance/Budget)
App\Support\OpeningBalance\OpeningBalanceBatch => App\Modules\OpeningBalance\Support\OpeningBalanceBatch
App\Support\OpeningBalance\OpeningBalanceLine  => App\Modules\OpeningBalance\Support\OpeningBalanceLine
App\Support\OpeningBalance\OpeningBalanceType  => App\Modules\OpeningBalance\Support\OpeningBalanceType
```

## Checklist Verifikasi
- [ ] `php artisan route:list --path=api | wc -l` = baseline.
- [ ] `php artisan test` hijau.
- [ ] Endpoint: `/api/cash-bank/accounts`, opening-balance & budget endpoints merespons.
- [ ] `grep -rn "App\\\\Support\\\\OpeningBalance" app/` hanya menemukan referensi (dijembatani alias), bukan file di `app/Support/OpeningBalance` (sudah hilang).

## Git Checkpoint
```
refactor(cashbank,openingbalance,budget): Fase 4 — move HTTP+service+support to modules
```
Update ledger (Fase 4 → ✅) & commit.

## Definition of Done
Ketiga modul self-contained (kecuali model); `app/Support/OpeningBalance` hilang; test hijau.
