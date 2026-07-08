# Fase 7 — Model Migration (central + tenant)

**Goal**: Pindahkan model ke Shared/modul, dengan mitigasi **morph map** & **factory resolution**. Ini fase paling delikat — kerjakan setelah Fase 0–6 hijau. Boleh dipecah per sub-grup model (commit terpisah) karena banyak (92 model).

Prasyarat baca: `00-conventions.md` §3 (alias), **§7 (ranjau morph & factory)**, §9. Baca §7 dua kali.

## Prasyarat
```bash
cd laravel_backend
test -d app/Modules/Reports/Services && echo "Fase 6 OK" || echo "STOP: selesaikan Fase 6"
php artisan test 2>&1 | tail -3
grep -rn "morphTo\|morphMany\|morphOne" app/Models   # konfirmasi hanya ActivityLog (central)
```

## Fakta terverifikasi (dasar mitigasi)
- **Morph**: hanya `ActivityLog::subject` (`morphTo`). Kolom `*_type` menyimpan FQCN penuh → butuh `morphMap` (§7a). `TenantAuditLog` juga model audit; cek relasinya saat dipindah.
- **Factory nyata (12 file)** — hanya model ini yang butuh `newFactory()` + update `$model` di factory:
  `User`; tenant: `AccountMapping, ChartOfAccount, Contact, GoodsReceipt, Product, StockAdjustment, StockBalance, StockMovement, StockOpname, VendorBill, Warehouse`.
  Model lain memakai trait `HasFactory` tapi **tanpa file factory** → tidak ada yang perlu diubah (factory() tak pernah dipanggil untuknya).

---

## A. Central models → `app/Shared/Models/` (ns `App\Shared\Models`)
18 file dari `app/Models/*.php`:
`AccountingPeriod, ActivityLog, Company, CompanyAccountingSetting, CompanyInvitation, CompanyModuleSetting, CompanySetupState, CompanyUser, CompanyUserPermissionOverride, DocumentNumberingSetting, DocumentNumberSequence, FiscalYear, Permission, Plan, Role, Subscription, TenantDatabase, User`.

> Semua central model → Shared/Models (bukan ke modul) untuk menghindari dependensi antar-modul: `User`/`Company` dipakai hampir semua modul.

## B. Tenant models → module `Models/`
`app/Models/Tenant/X.php` → `app/Modules/{Modul}/Models/X.php`, ns `App\Modules\{Modul}\Models`.

| Modul | Model tenant |
|---|---|
| **MasterData** (10) | AccountMapping, ChartOfAccount, Contact, Department, PaymentTerm, Product, ProductCategory, Project, Unit, Warehouse |
| **Journal** (2) | JournalEntry, JournalEntryLine |
| **Accounting** (3) | FiscalYearClosing, PeriodEndRun, PeriodEndRunRoutine |
| **CashBank** (7) | BankReconciliation, BankReconciliationLine, BankTransfer, CashPayment, CashPaymentLine, CashReceipt, CashReceiptLine |
| **Budget** (3) | BudgetLine, BudgetPeriod, BudgetSubmission |
| **OpeningBalance** (2) | OpeningBalanceBatch, OpeningBalanceLine |
| **Inventory** (7) | StockAdjustment, StockAdjustmentLine, StockBalance, StockMovement, StockMovementLine, StockOpname, StockOpnameLine |
| **Sales** (16) | CustomerDeposit, CustomerDepositAllocation, DeliveryOrder, DeliveryOrderLine, ProformaInvoice, ProformaInvoiceLine, SalesInvoice, SalesInvoiceLine, SalesOrder, SalesOrderLine, SalesQuotation, SalesQuotationLine, SalesReceipt, SalesReceiptLine, SalesReturn, SalesReturnLine |
| **Purchase** (14) | GoodsReceipt, GoodsReceiptLine, PurchaseOrder, PurchaseOrderLine, PurchaseRequest, PurchaseRequestLine, PurchaseReturn, PurchaseReturnLine, VendorBill, VendorBillLine, VendorDeposit, VendorDepositAllocation, VendorPayment, VendorPaymentLine |
| **FixedAssets** (8) | FixedAsset, FixedAssetAcquisition, FixedAssetCategory, FixedAssetDepreciationRun, FixedAssetDepreciationRunLine, FixedAssetDepreciationSchedule, FixedAssetDisposal, FixedAssetTransaction |

**Cross-cutting tenant models → `app/Shared/Models/` (2)**: `TenantAuditLog` (audit), `TransactionRevision` (transaction lifecycle). ns `App\Shared\Models`.

> Total: 18 central + 2 shared-tenant + 72 module-tenant = 92.
> Model tenant mempertahankan `protected $connection` (koneksi tenant) — pindah namespace **tidak** mengubah connection/`$table`; jangan diedit selain `namespace`.

---

## C. Mitigasi WAJIB

### C1. Morph map — `SharedServiceProvider::boot()`
Tambahkan (agar `*_type` lama yang menyimpan FQCN `App\Models\...` tetap resolve):
```php
use Illuminate\Database\Eloquent\Relations\Relation;

Relation::morphMap([
    // Petakan SETIAP FQCN lama → class baru. Karena kolom morph bisa berisi
    // model apa pun yang pernah jadi subject ActivityLog/TenantAuditLog,
    // daftarkan semua model yang dipindah.
    'App\\Models\\User'                 => \App\Shared\Models\User::class,
    'App\\Models\\Tenant\\JournalEntry' => \App\Modules\Journal\Models\JournalEntry::class,
    // ... satu baris per model (92 baris) — sama dengan daftar alias di C3.
]);
```
> Untuk memastikan tidak ada yang terlewat, generate daftar dari mapping A+B. `morphMap` key = FQCN lama (string), value = class baru.

### C2. Factory — hanya 12 model
Untuk tiap model ber-factory (daftar di "Fakta terverifikasi"):
1. Di **model**, tambah:
   ```php
   protected static function newFactory()
   {
       return \Database\Factories\Tenant\ProductFactory::new(); // sesuaikan
   }
   ```
   (`User` → `\Database\Factories\UserFactory::new()`.)
2. Di **factory file** (tetap di `database/factories/...`), set eksplisit:
   ```php
   protected $model = \App\Modules\MasterData\Models\Product::class; // class baru
   ```
   Factory file **tidak dipindah**, hanya `$model` diupdate.

### C3. Alias model (old→new) → `AliasServiceProvider::ALIASES`
Tambah 92 baris `App\Models\...`/`App\Models\Tenant\...` → class baru. Contoh:
```
App\Models\User                 => App\Shared\Models\User
App\Models\Company              => App\Shared\Models\Company
App\Models\Tenant\Product       => App\Modules\MasterData\Models\Product
App\Models\Tenant\SalesInvoice  => App\Modules\Sales\Models\SalesInvoice
App\Models\Tenant\TenantAuditLog=> App\Shared\Models\TenantAuditLog
...
```
Ini menjaga ratusan referensi `::class` di service/controller/command/relasi model yang belum diupdate tetap bekerja sampai Fase 8.

---

## D. Urutan kerja disarankan (aman lintas sesi)
Kerjakan & commit per sub-grup; update morphMap + alias + factory tiap sub-grup:
1. **7a** Central (18) → Shared/Models + morphMap + alias + `User` factory. Test.
2. **7b** MasterData (10) + factory (AccountMapping, ChartOfAccount, Contact, Product, Warehouse). Test.
3. **7c** Journal + Accounting (5). Test.
4. **7d** CashBank + Budget + OpeningBalance (12). Test.
5. **7e** Inventory (7) + factory (StockAdjustment/Balance/Movement/Opname). Test.
6. **7f** Sales (16). Test.
7. **7g** Purchase (14) + factory (GoodsReceipt, VendorBill). Test.
8. **7h** FixedAssets (8) + shared-tenant (TenantAuditLog, TransactionRevision). Test.

Tiap sub-grup: `git mv` + edit namespace + tambah alias/morphMap + (jika ada) factory → `php artisan test`. Jika hijau, commit. Ledger boleh dicatat "Fase 7 (7c/8 selesai)".

## Checklist Verifikasi (per sub-grup & akhir)
- [ ] `php artisan test` hijau (khususnya test yang pakai `->factory()` & morph/audit).
- [ ] `php artisan tinker` → `ActivityLog::latest()->first()->subject` resolve (morph map benar).
- [ ] Seeder demo jalan: `php artisan db:seed` / command demo (memakai factory).
- [ ] `php artisan route:list --path=api | wc -l` = baseline.
- [ ] Endpoint kritis merespons (§8 conventions).
- [ ] `ls app/Models app/Models/Tenant` → kosong.

## Git Checkpoint
```
refactor(models): Fase 7 — migrate central & tenant models with morphMap+factory mitigations
```
Update ledger (Fase 7 → ✅) & commit.

## Definition of Done
`app/Models/` & `app/Models/Tenant/` kosong. Model ada di `Shared/Models` & `Modules/{X}/Models`. morphMap & newFactory terpasang. Semua test hijau.
