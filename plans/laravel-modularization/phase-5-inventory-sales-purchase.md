# Fase 5 — Inventory · Sales · Purchase (paling kompleks)

**Goal**: Migrasi tiga modul yang saling terintegrasi. **Model tidak disentuh** (Fase 7).

Integrasi (satu arah, tidak ada siklus):
- Inventory menyediakan `InventorySalesIntegrationService` & `InventoryPurchaseIntegrationService`.
- Sales meng-consume `InventorySalesIntegrationService`; Purchase meng-consume `InventoryPurchaseIntegrationService`.
- Inventory **tidak** bergantung ke Sales/Purchase.

> Karena ketiganya di fase yang sama, referensi antar-mereka boleh diupdate langsung; alias tetap ditambahkan sebagai jaring pengaman.

Prasyarat baca: `00-conventions.md` §1–§3, §9.

## Prasyarat
```bash
cd laravel_backend
test -d app/Modules/CashBank/Services && echo "Fase 4 OK" || echo "STOP: selesaikan Fase 4"
php artisan test 2>&1 | tail -3
```

## Transform: `00-conventions.md` §1.

---

### Modul Inventory (`app/Modules/Inventory/`)
**Controllers** (6): `InventoryReportController`, `InventoryValuationController`, `StockAdjustmentController`, `StockBalanceController`, `StockMovementController`, `StockOpnameController`.
**Requests** (10): `StockAdjustmentActionRequest`, `StockOpnameActionRequest`, `StoreStockAdjustmentRequest`, `StoreStockMovementRequest`, `StoreStockOpnameRequest`, `UpdateStockAdjustmentRequest`, `UpdateStockOpnameLineRequest`, `VoidStockAdjustmentRequest`, `VoidStockMovementRequest`, `VoidStockOpnameRequest`.
**Services** (16, `Services/Inventory` → `Modules/Inventory/Services`): `AverageCostService`, `InventoryAccountMappingService`, `InventoryConfigService`, `InventoryPurchaseIntegrationService`, `InventoryQuantityService`, `InventorySalesIntegrationService`, `InventorySourceService`, `InventoryValuationService`, `OpeningStockService`, `StockAdjustmentService`, `StockBalanceRebuildService`, `StockBalanceService`, `StockMovementJournalService`, `StockMovementService`, `StockMovementValidationService`, `StockOpnameService`.
**Services/Reports** (5, → `Modules/Inventory/Services/Reports`, ns `App\Modules\Inventory\Services\Reports`): `InventoryAlertReportService`, `InventoryValuationReportService`, `StockBalanceReportService`, `StockCardReportService`, `StockMovementReportService`.
**Support → modul** (`Support/Inventory/*` → `Modules/Inventory/Support`, ns `App\Modules\Inventory\Support`): `InventoryMovementStatus.php`, `InventoryMovementType.php`.
Config `inventory.php` tetap di `config/`.

### Modul Sales (`app/Modules/Sales/`)
**Controllers** (9): `AccountsReceivableController`, `CustomerDepositController`, `DeliveryOrderController`, `ProformaInvoiceController`, `SalesInvoiceController`, `SalesOrderController`, `SalesQuotationController`, `SalesReceiptController`, `SalesReturnController`.
**Requests** (18): `AllocateCustomerDepositRequest`, `PostSalesInvoiceRequest`, `RefundCustomerDepositRequest`, `SalesActionRequest`, `StoreCustomerDepositRequest`, `StoreDeliveryOrderRequest`, `StoreProformaInvoiceRequest`, `StoreSalesInvoiceRequest`, `StoreSalesOrderRequest`, `StoreSalesQuotationRequest`, `StoreSalesReceiptRequest`, `StoreSalesReturnRequest`, `UpdateDeliveryOrderRequest`, `UpdateProformaInvoiceRequest`, `UpdateSalesInvoiceRequest`, `UpdateSalesOrderRequest`, `UpdateSalesQuotationRequest`, `UpdateSalesReturnRequest`.
**Services** (16, termasuk `Concerns/`): `ARAgingService`, `ARReconciliationService`, `ARSubsidiaryLedgerService`, `Concerns/HandlesSalesDocuments` (⚠️ trait — lihat catatan), `CustomerDepositService`, `DeliveryOrderService`, `ProformaInvoiceService`, `SalesAccountMappingService`, `SalesAccountResolverService`, `SalesCalculationService`, `SalesInvoiceService`, `SalesOrderService`, `SalesQuotationService`, `SalesReceiptService`, `SalesReturnService`, `SalesSourceChainService`, `SalesStatusService`.
Config `sales_workflow.php` tetap di `config/`.

### Modul Purchase (`app/Modules/Purchase/`)
**Controllers** (8): `AccountsPayableController`, `GoodsReceiptController`, `PurchaseOrderController`, `PurchaseRequestController`, `PurchaseReturnController`, `VendorBillController`, `VendorDepositController`, `VendorPaymentController`.
**Requests** (16): `AllocateVendorDepositRequest`, `PostVendorBillRequest`, `PurchaseRequestActionRequest`, `RefundVendorDepositRequest`, `StoreGoodsReceiptRequest`, `StorePurchaseOrderRequest`, `StorePurchaseRequestRequest`, `StorePurchaseReturnRequest`, `StoreVendorBillRequest`, `StoreVendorDepositRequest`, `StoreVendorPaymentRequest`, `UpdateGoodsReceiptRequest`, `UpdatePurchaseOrderRequest`, `UpdatePurchaseRequestRequest`, `UpdatePurchaseReturnRequest`, `UpdateVendorBillRequest`.
**Services** (16, termasuk `Concerns/`): `APAgingService`, `APReconciliationService`, `APSubsidiaryLedgerService`, `Concerns/HandlesPurchaseDocuments` (⚠️ trait), `GoodsReceiptService`, `PurchaseAccountMappingService`, `PurchaseAccountResolverService`, `PurchaseCalculationService`, `PurchaseOrderService`, `PurchaseRequestService`, `PurchaseReturnService`, `PurchaseSourceChainService`, `PurchaseStatusService`, `VendorBillService`, `VendorDepositService`, `VendorPaymentService`.
Config `purchase_workflow.php` tetap di `config/`.

---

## ⚠️ Trait di Services/Concerns
`HandlesSalesDocuments` & `HandlesPurchaseDocuments` adalah trait (tak bisa `class_alias`). Setelah dipindah, update `use` di file yang memakainya (biasanya service di modul yang sama):
```bash
grep -rln "Services\\\\Sales\\\\Concerns\\\\HandlesSalesDocuments" app/
grep -rln "Services\\\\Purchase\\\\Concerns\\\\HandlesPurchaseDocuments" app/
```

## Update Routes/api.php
`app/Modules/{Inventory,Sales,Purchase}/Routes/api.php` — ganti `use ...Controller`.

## Alias (tambah ke `ALIASES`)
Semua service non-trait (Inventory 16 + Reports 5, Sales 15, Purchase 15) + `Support/Inventory` (2). Contoh kritis integrasi:
```
App\Services\Inventory\InventorySalesIntegrationService    => App\Modules\Inventory\Services\InventorySalesIntegrationService
App\Services\Inventory\InventoryPurchaseIntegrationService => App\Modules\Inventory\Services\InventoryPurchaseIntegrationService
App\Support\Inventory\InventoryMovementStatus => App\Modules\Inventory\Support\InventoryMovementStatus
App\Support\Inventory\InventoryMovementType   => App\Modules\Inventory\Support\InventoryMovementType
...
```

## Checklist Verifikasi (lebih ketat — fase kritis)
- [ ] `php artisan route:list --path=api | wc -l` = baseline.
- [ ] `php artisan test` hijau (perhatikan test integrasi Inventory-Sales & Inventory-Purchase).
- [ ] Endpoint: `/api/sales/invoices`, `/api/purchase/bills`, `/api/inventory/stock-balances` merespons.
- [ ] Alur manual/test: Sales Quotation → SO → DO → Proforma → Sales Invoice; stock movement otomatis terbentuk.
- [ ] Alur manual/test: Purchase Request → PO → Goods Receipt → Vendor Bill; stock terupdate.
- [ ] `grep -rn "App\\\\Support\\\\Inventory" app/` — file sumber hilang (hanya referensi ter-alias).

## Git Checkpoint
```
refactor(inventory,sales,purchase): Fase 5 — move HTTP+service+support to modules
```
Update ledger (Fase 5 → ✅) & commit. Disarankan commit per modul (Inventory dulu, lalu Sales, lalu Purchase) untuk rollback granular.

## Definition of Done
Ketiga modul self-contained (kecuali model); `app/Support/Inventory` hilang; integrasi stok berfungsi; test hijau.
