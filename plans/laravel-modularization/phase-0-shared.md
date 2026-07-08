# Fase 0 — Shared Foundation (tanpa Model)

**Goal**: Pindahkan semua kode cross-cutting ke `app/Shared/`, buat `SharedServiceProvider` + `AliasServiceProvider`, verifikasi seluruh test tetap lulus. **Model TIDAK disentuh** (Fase 7).

Prasyarat baca: `00-conventions.md` §1–§6, §8–§9.

---

## Prasyarat (verifikasi titik awal)

```bash
cd laravel_backend
# Harus BELUM ada isi Shared selain README stub:
ls app/Shared/Api/            # hanya README.md
test -f app/Providers/AliasServiceProvider.php && echo "SUDAH ADA (fase mungkin setengah jalan)" || echo "OK belum ada"
# Catat baseline:
php artisan test 2>&1 | tail -5   # CATAT jumlah test & assertion
php artisan route:list --path=api | wc -l   # CATAT jumlah route
```

Jika `AliasServiceProvider` sudah ada, fase ini mungkin setengah jalan — cek isi `app/Shared/*` dan bandingkan dengan tabel di bawah untuk tahu file mana yang belum dipindah.

---

## A. Buat provider baru

### `app/Shared/Providers/SharedServiceProvider.php` (namespace `App\Shared\Providers`)
Pindahkan binding dari `AppServiceProvider` ke sini:
- `singleton(TenantContext::class)` → gunakan `App\Shared\Tenant\TenantContext`.
- `bind(TransactionDependencyChecker::class, TransactionDependencyService::class)` → gunakan namespace `App\Shared\TransactionLifecycle\...` dan `App\Shared\TransactionLifecycle\Contracts\...`.
- `bind(TransactionDateGuard::class, TransactionDateGuardService::class)` → idem.
- `boot()`: `$this->loadMigrationsFrom(database_path('migrations/central'));`

### `app/Providers/AliasServiceProvider.php` (namespace `App\Providers`)
Struktur di `00-conventions.md` §3. Isi konstanta `ALIASES` dengan daftar di bagian **D** bawah.

---

## B. Edit file infra (WAJIB — bukan alias)

| File | Perubahan |
|---|---|
| `bootstrap/providers.php` | Tambah `App\Shared\Providers\SharedServiceProvider::class`, lalu `App\Providers\AliasServiceProvider::class` (urutan: Shared dulu, Alias kedua). |
| `bootstrap/app.php` | `use App\Support\Api\ApiResponseBuilder;` → `use App\Shared\Api\ApiResponseBuilder;` |
| `bootstrap/app.php` | middleware alias `'company.access' => \App\Http\Middleware\EnsureCompanyAccess::class` → `\App\Shared\Http\Middleware\EnsureCompanyAccess::class` |
| `bootstrap/app.php` | middleware alias `'permission' => \App\Http\Middleware\EnsurePermission::class` → `\App\Shared\Http\Middleware\EnsurePermission::class` |
| `app/Providers/AppServiceProvider.php` | Hapus binding yang sudah pindah ke `SharedServiceProvider` (TenantContext, kedua bind Transactions) + hapus `use` yang tak terpakai + hapus `loadMigrationsFrom` (pindah ke Shared). Sisakan kelas minimal. |
| `routes/api.php` | `use App\Http\Controllers\Api\HealthController;` → `use App\Shared\Http\Controllers\HealthController;` |

Referensi `SourceDocumentPickerController` di file route modul (dijembatani alias, boleh update sekarang atau saat modulnya): `App\Http\Controllers\Api\Transactions\SourceDocumentPickerController` → `App\Shared\SourceDocument\SourceDocumentPickerController`. Cari dengan:
```bash
grep -rln "Api\\\\Transactions\\\\SourceDocumentPickerController" app/Modules/*/Routes/api.php
```

---

## C. Mapping file (pindah + ganti namespace)

Semua `git mv` + edit baris `namespace`. Trait ditandai ⚠️ (lihat catatan bawah).

### → `app/Shared/Api/` (ns `App\Shared\Api`)
- `Support/Api/ApiResponseBuilder.php`
- `Support/Api/ApiErrorCode.php`
- `Traits/ApiResponse.php` ⚠️

### → `app/Shared/Audit/` (ns `App\Shared\Audit`)
- `Services/Audit/AuditLogService.php`
- `Support/Audit/AuditAction.php`
- `Support/Audit/AuditEvent.php`
- `Support/Audit/AuditResult.php`

### → `app/Shared/DocumentNumbering/` (ns `App\Shared\DocumentNumbering`)
- `Services/DocumentNumbering/DocumentNumberService.php`
- `Support/DocumentNumbering/DocumentNumberFormat.php`
- `Support/DocumentNumbering/DocumentType.php`

### → `app/Shared/TransactionLifecycle/` (ns `App\Shared\TransactionLifecycle`)
- `Services/Transactions/NoopTransactionDateGuard.php`
- `Services/Transactions/NoopTransactionDependencyChecker.php`
- `Services/Transactions/PaymentTermDueDateService.php`
- `Services/Transactions/TransactionDateGuardService.php`
- `Services/Transactions/TransactionDependencyService.php`
- `Services/Transactions/TransactionPolicyService.php`
- `Services/Transactions/TransactionRevisionService.php`
- `Services/Transactions/TransactionVoidEffectService.php`
- `Support/Transaction/DependencyCheckResult.php`
- `Support/Transaction/TransactionAction.php`
- `Support/Transaction/TransactionLifecycle.php`
- `Support/Transaction/TransactionModule.php`
- `Support/Transaction/TransactionPolicyResult.php`
- `Support/Transaction/TransactionStatus.php`
- `Support/Revision/RevisionSnapshot.php`
- `Support/Revision/TransactionRevisionAction.php`
- `Traits/HasTransactionLifecycle.php` ⚠️
- `Traits/HasRevisionTracking.php` ⚠️

### → `app/Shared/TransactionLifecycle/Contracts/` (ns `App\Shared\TransactionLifecycle\Contracts`)
- `Contracts/Transactions/TransactionDateGuard.php`
- `Contracts/Transactions/TransactionDependencyChecker.php`

### → `app/Shared/TransactionLifecycle/Checkers/` (ns `App\Shared\TransactionLifecycle\Checkers`)
- `Services/Transactions/Checkers/BaseTransactionDependencyChecker.php`
- `Services/Transactions/Checkers/CashBankTransactionDependencyChecker.php`
- `Services/Transactions/Checkers/InventoryTransactionDependencyChecker.php`
- `Services/Transactions/Checkers/JournalTransactionDependencyChecker.php`
- `Services/Transactions/Checkers/PurchaseTransactionDependencyChecker.php`
- `Services/Transactions/Checkers/SalesTransactionDependencyChecker.php`

### → `app/Shared/SourceDocument/` (ns `App\Shared\SourceDocument`)
- `Http/Controllers/Api/Transactions/SourceDocumentPickerController.php`
- `Services/Transactions/SourceDocumentPickerService.php`
- `Support/SourceLink/SourceLink.php`
- `Support/SourceLink/SourceLinkFactory.php`
- `Support/SourceLink/SourceModule.php`
- `Support/SourceLink/SourceType.php`
- `Traits/HasSourceLink.php` ⚠️

### → `app/Shared/AccountMapping/` (ns `App\Shared\AccountMapping`)
- `Services/AccountMapping/AccountMappingService.php`
- `Services/AccountMapping/AccountMappingValidator.php`
- `Support/AccountMapping/AccountMappingKey.php`
- `Support/AccountMapping/AccountMappingModule.php`
- `Support/AccountMapping/AccountMappingRequirement.php`

### → `app/Shared/Permission/` (ns `App\Shared\Permission`)
- `Services/Permissions/EffectivePermissionService.php`
- `Services/Permissions/PermissionCatalogService.php`
- `Services/Permissions/PermissionService.php`

### → `app/Shared/Tenant/` (ns `App\Shared\Tenant`)
- `Services/Tenant/TenantConnectionManager.php`
- `Services/Tenant/TenantContext.php`
- `Services/Tenant/TenantMigrationService.php`
- `Services/Tenant/TenantProvisioningService.php`

### → `app/Shared/Validation/` (ns `App\Shared\Validation`)
- `Services/Validation/BusinessReferenceValidator.php`

### → `app/Shared/DataRetention/` (ns `App\Shared\DataRetention`)
- `Services/DataRetention/DataRetentionService.php`
- `Services/DataRetention/DataRetentionValidator.php`
- `Support/DataRetention/DataRetentionPolicy.php`
- `Support/DataRetention/RetentionAction.php`
- `Support/DataRetention/RetentionDecision.php`

### → `app/Shared/Reports/Data/` (ns `App\Shared\Reports\Data`)
Semua 16 file `Data/Reports/*.php`:
`AccountLedgerFilter, AccountLedgerLineData, BalanceSheetFilter, CashFlowFilter, FinancialSummaryFilter, LedgerAccountSummaryData, LedgerFilter, LedgerLineData, ProfitLossFilter, ReportDateRange, ReportDimensionFilter, ReportMeta, ReportResponse, ReportTotals, TrialBalanceAccountData, TrialBalanceFilter`.

### → `app/Shared/Reports/` (ns `App\Shared\Reports`)
- `Support/Reports/ReportVisibilityMode.php`
- `Traits/HasReportVisibility.php` ⚠️

### → `app/Shared/Enums/` (ns `App\Shared\Enums`)
- `Enums/SourceType.php`

### → `app/Shared/Exceptions/` (ns `App\Shared\Exceptions`)
- `Exceptions/ApiException.php`

### → `app/Shared/Http/Middleware/` (ns `App\Shared\Http\Middleware`)
- `Http/Middleware/EnsureCompanyAccess.php`
- `Http/Middleware/EnsurePermission.php`

### → `app/Shared/Http/Controllers/` (ns `App\Shared\Http\Controllers`)
- `Http/Controllers/Api/HealthController.php`

---

## ⚠️ Trait — update referensi langsung (tak bisa di-alias)

Trait tidak bisa `class_alias`. Setelah memindah tiap trait, grep pemakainya dan ganti `use App\Traits\X;` → namespace baru. Perintah:

```bash
grep -rln "App\\\\Traits\\\\ApiResponse"            app/    # → App\Shared\Api\ApiResponse
grep -rln "App\\\\Traits\\\\HasTransactionLifecycle" app/    # → App\Shared\TransactionLifecycle\HasTransactionLifecycle
grep -rln "App\\\\Traits\\\\HasRevisionTracking"     app/    # → App\Shared\TransactionLifecycle\HasRevisionTracking
grep -rln "App\\\\Traits\\\\HasSourceLink"           app/    # → App\Shared\SourceDocument\HasSourceLink
grep -rln "App\\\\Traits\\\\HasReportVisibility"     app/    # → App\Shared\Reports\HasReportVisibility
```
Catatan: `HasTransactionLifecycle`, `HasRevisionTracking`, `HasSourceLink`, `HasReportVisibility` dipakai oleh **model tenant** (mis. `JournalEntry`). Model belum pindah, tapi baris `use ...Trait` di dalam model **harus** diupdate sekarang (trait yang pindah, bukan model-nya).

---

## D. Daftar alias untuk `AliasServiceProvider::ALIASES`

Isi array `'Nama\\Lama' => \Namespace\Baru::class` untuk **class & interface** (bukan trait) berikut. (Format: kunci = FQCN lama, nilai = class baru.)

Support/Services → Shared (non-trait):
```
App\Support\Api\ApiResponseBuilder        => App\Shared\Api\ApiResponseBuilder
App\Support\Api\ApiErrorCode              => App\Shared\Api\ApiErrorCode
App\Services\Audit\AuditLogService        => App\Shared\Audit\AuditLogService
App\Support\Audit\AuditAction             => App\Shared\Audit\AuditAction
App\Support\Audit\AuditEvent              => App\Shared\Audit\AuditEvent
App\Support\Audit\AuditResult             => App\Shared\Audit\AuditResult
App\Services\DocumentNumbering\DocumentNumberService => App\Shared\DocumentNumbering\DocumentNumberService
App\Support\DocumentNumbering\DocumentNumberFormat   => App\Shared\DocumentNumbering\DocumentNumberFormat
App\Support\DocumentNumbering\DocumentType           => App\Shared\DocumentNumbering\DocumentType
App\Services\Transactions\NoopTransactionDateGuard        => App\Shared\TransactionLifecycle\NoopTransactionDateGuard
App\Services\Transactions\NoopTransactionDependencyChecker=> App\Shared\TransactionLifecycle\NoopTransactionDependencyChecker
App\Services\Transactions\PaymentTermDueDateService       => App\Shared\TransactionLifecycle\PaymentTermDueDateService
App\Services\Transactions\TransactionDateGuardService     => App\Shared\TransactionLifecycle\TransactionDateGuardService
App\Services\Transactions\TransactionDependencyService    => App\Shared\TransactionLifecycle\TransactionDependencyService
App\Services\Transactions\TransactionPolicyService        => App\Shared\TransactionLifecycle\TransactionPolicyService
App\Services\Transactions\TransactionRevisionService      => App\Shared\TransactionLifecycle\TransactionRevisionService
App\Services\Transactions\TransactionVoidEffectService    => App\Shared\TransactionLifecycle\TransactionVoidEffectService
App\Support\Transaction\DependencyCheckResult => App\Shared\TransactionLifecycle\DependencyCheckResult
App\Support\Transaction\TransactionAction     => App\Shared\TransactionLifecycle\TransactionAction
App\Support\Transaction\TransactionLifecycle  => App\Shared\TransactionLifecycle\TransactionLifecycle
App\Support\Transaction\TransactionModule     => App\Shared\TransactionLifecycle\TransactionModule
App\Support\Transaction\TransactionPolicyResult => App\Shared\TransactionLifecycle\TransactionPolicyResult
App\Support\Transaction\TransactionStatus     => App\Shared\TransactionLifecycle\TransactionStatus
App\Support\Revision\RevisionSnapshot          => App\Shared\TransactionLifecycle\RevisionSnapshot
App\Support\Revision\TransactionRevisionAction => App\Shared\TransactionLifecycle\TransactionRevisionAction
App\Contracts\Transactions\TransactionDateGuard        => App\Shared\TransactionLifecycle\Contracts\TransactionDateGuard
App\Contracts\Transactions\TransactionDependencyChecker=> App\Shared\TransactionLifecycle\Contracts\TransactionDependencyChecker
App\Services\Transactions\Checkers\BaseTransactionDependencyChecker     => App\Shared\TransactionLifecycle\Checkers\BaseTransactionDependencyChecker
App\Services\Transactions\Checkers\CashBankTransactionDependencyChecker => App\Shared\TransactionLifecycle\Checkers\CashBankTransactionDependencyChecker
App\Services\Transactions\Checkers\InventoryTransactionDependencyChecker=> App\Shared\TransactionLifecycle\Checkers\InventoryTransactionDependencyChecker
App\Services\Transactions\Checkers\JournalTransactionDependencyChecker  => App\Shared\TransactionLifecycle\Checkers\JournalTransactionDependencyChecker
App\Services\Transactions\Checkers\PurchaseTransactionDependencyChecker => App\Shared\TransactionLifecycle\Checkers\PurchaseTransactionDependencyChecker
App\Services\Transactions\Checkers\SalesTransactionDependencyChecker    => App\Shared\TransactionLifecycle\Checkers\SalesTransactionDependencyChecker
App\Http\Controllers\Api\Transactions\SourceDocumentPickerController => App\Shared\SourceDocument\SourceDocumentPickerController
App\Services\Transactions\SourceDocumentPickerService => App\Shared\SourceDocument\SourceDocumentPickerService
App\Support\SourceLink\SourceLink        => App\Shared\SourceDocument\SourceLink
App\Support\SourceLink\SourceLinkFactory => App\Shared\SourceDocument\SourceLinkFactory
App\Support\SourceLink\SourceModule      => App\Shared\SourceDocument\SourceModule
App\Support\SourceLink\SourceType        => App\Shared\SourceDocument\SourceType
App\Services\AccountMapping\AccountMappingService   => App\Shared\AccountMapping\AccountMappingService
App\Services\AccountMapping\AccountMappingValidator => App\Shared\AccountMapping\AccountMappingValidator
App\Support\AccountMapping\AccountMappingKey         => App\Shared\AccountMapping\AccountMappingKey
App\Support\AccountMapping\AccountMappingModule      => App\Shared\AccountMapping\AccountMappingModule
App\Support\AccountMapping\AccountMappingRequirement => App\Shared\AccountMapping\AccountMappingRequirement
App\Services\Permissions\EffectivePermissionService => App\Shared\Permission\EffectivePermissionService
App\Services\Permissions\PermissionCatalogService   => App\Shared\Permission\PermissionCatalogService
App\Services\Permissions\PermissionService          => App\Shared\Permission\PermissionService
App\Services\Tenant\TenantConnectionManager  => App\Shared\Tenant\TenantConnectionManager
App\Services\Tenant\TenantContext            => App\Shared\Tenant\TenantContext
App\Services\Tenant\TenantMigrationService   => App\Shared\Tenant\TenantMigrationService
App\Services\Tenant\TenantProvisioningService=> App\Shared\Tenant\TenantProvisioningService
App\Services\Validation\BusinessReferenceValidator => App\Shared\Validation\BusinessReferenceValidator
App\Services\DataRetention\DataRetentionService   => App\Shared\DataRetention\DataRetentionService
App\Services\DataRetention\DataRetentionValidator => App\Shared\DataRetention\DataRetentionValidator
App\Support\DataRetention\DataRetentionPolicy => App\Shared\DataRetention\DataRetentionPolicy
App\Support\DataRetention\RetentionAction     => App\Shared\DataRetention\RetentionAction
App\Support\DataRetention\RetentionDecision   => App\Shared\DataRetention\RetentionDecision
App\Support\Reports\ReportVisibilityMode => App\Shared\Reports\ReportVisibilityMode
App\Enums\SourceType       => App\Shared\Enums\SourceType
App\Exceptions\ApiException=> App\Shared\Exceptions\ApiException
App\Http\Middleware\EnsureCompanyAccess => App\Shared\Http\Middleware\EnsureCompanyAccess
App\Http\Middleware\EnsurePermission    => App\Shared\Http\Middleware\EnsurePermission
App\Http\Controllers\Api\HealthController=> App\Shared\Http\Controllers\HealthController
```
Semua 16 DTO `App\Data\Reports\*` → `App\Shared\Reports\Data\*` (satu baris per class, nama sama).

> Trait TIDAK masuk daftar alias (ApiResponse, HasTransactionLifecycle, HasRevisionTracking, HasSourceLink, HasReportVisibility) — sudah diupdate langsung di bagian ⚠️.

---

## Checklist Verifikasi

- [ ] `composer dump-autoload` tanpa error.
- [ ] `php artisan config:clear && php artisan route:clear` sukses.
- [ ] `php artisan route:list --path=api | wc -l` = baseline (tidak berubah).
- [ ] `php artisan test` = jumlah test/assert baseline, semua hijau.
- [ ] `grep -rn "App\\\\Support\\\\" app/` hanya menyisakan `Support/Inventory`, `Support/OpeningBalance` (belum dipindah — normal). Tidak ada sisa di `Support/Api|Audit|...` yang sudah dipindah.
- [ ] Endpoint kritis (`00-conventions.md` §8) merespons.
- [ ] `app/Shared/*/README.md` boleh dibiarkan atau dihapus (stub lama).

## Git Checkpoint
```
refactor(shared): Fase 0 — move cross-cutting code to app/Shared + alias bridge
```
Lalu update ledger `README.md` (Fase 0 → ✅) & commit.

## Definition of Done
Semua kode cross-cutting ada di `app/Shared/`, `SharedServiceProvider` + `AliasServiceProvider` aktif, test hijau, tidak ada model yang dipindah. `app/Support/` hanya menyisakan `Inventory/` & `OpeningBalance/`.
