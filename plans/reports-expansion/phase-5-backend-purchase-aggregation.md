# Fase 5 — Backend Agregasi Pembelian

**Prioritas:** B (design-I2 §7 "Laporan Pembelian: agregasi per pemasok, per barang")
**Estimasi:** sedang — backend saja. Simetris Fase 3.

## Tujuan

Bangun endpoint agregasi pembelian yang belum ada. Rekap SUM per grup dari `vendor_bills` + lines (verifikasi nama model/tabel aktual di modul Purchase). Frontend di Fase 6.

## Prasyarat

- Fase 0 ✅. (Fase 3/4 tidak wajib, tapi ikuti pola yang sama bila sudah ada.)
- Baca `00-conventions.md` §1, §8, dan `phase-3-backend-sales-aggregation.md` (pola identik — tiru).
- Konfirmasi model Purchase: `app/Modules/Purchase/` — `VendorBill`, `VendorBillLine` (nama pasti bisa beda). Kolom: vendor_id, product_id, qty, unit_price, line_total, bill_date, status (hanya ter-post).

## Keputusan lokasi endpoint

Modul **Reports**, sub-prefix `/reports/purchase/*` (konsisten dengan Fase 3). Service/controller/request di `app/Modules/Reports/{Services,Controllers,Requests}/Purchase/`.

## Daftar tugas

### T5.1 — Ringkasan Pembelian per periode — `GET /reports/purchase/summary`
Return `{ rows: [{ period, bill_count, subtotal, tax, total }], totals: {...} }`.

### T5.2 — Pembelian per Pemasok — `GET /reports/purchase/by-vendor`
GROUP BY vendor_id → `{ rows: [{ vendor_id, vendor_name, bill_count, subtotal, tax, total }], totals: { total } }`.

### T5.3 — Pembelian per Barang — `GET /reports/purchase/by-product`
GROUP BY product_id dari lines → `{ rows: [{ product_id, product_code, product_name, qty, subtotal, total }], totals: { qty, total } }`.

### Untuk tiap endpoint
- [ ] Service (scope hanya bill ter-post, exclude draft/void, hormati tenant).
- [ ] FormRequest (periode + dimensi + filter grup opsional).
- [ ] Controller tipis (boleh satu `PurchaseReportController` dengan 3 method).
- [ ] Route grup `reports`, `permission:reports.view`.
- [ ] Feature test `tests/Feature/Reports/PurchaseReport*Test.php`: happy path, exclude void/draft, 403, 422.

## Peta File

> Backend-only. Model dibaca lintas-modul (`Purchase\Models\VendorBill`, `VendorBillLine`) — read-only.

**➕ Tambah**
- `laravel_backend/app/Modules/Reports/Services/Purchase/PurchaseSummaryReportService.php`
- `laravel_backend/app/Modules/Reports/Services/Purchase/PurchaseByVendorReportService.php`
- `laravel_backend/app/Modules/Reports/Services/Purchase/PurchaseByProductReportService.php`
- `laravel_backend/app/Modules/Reports/Requests/Purchase/PurchaseSummaryReportRequest.php`
- `laravel_backend/app/Modules/Reports/Requests/Purchase/PurchaseByVendorReportRequest.php`
- `laravel_backend/app/Modules/Reports/Requests/Purchase/PurchaseByProductReportRequest.php`
- `laravel_backend/app/Modules/Reports/Controllers/Purchase/PurchaseReportController.php`
- `laravel_backend/tests/Feature/Reports/PurchaseSummaryReportTest.php`
- `laravel_backend/tests/Feature/Reports/PurchaseByVendorReportTest.php`
- `laravel_backend/tests/Feature/Reports/PurchaseByProductReportTest.php`

**✏️ Ubah**
- `laravel_backend/app/Modules/Reports/Routes/api.php` — 3 route `/reports/purchase/{summary,by-vendor,by-product}`.
- `phase-5-backend-purchase-aggregation.md` (file ini) — isi "Kontrak response".

**🗑️ Hapus** — Tidak ada.

## Checklist Verifikasi

- [ ] `php artisan test --filter=PurchaseReport` hijau.
- [ ] `pint --test` hijau.
- [ ] `route:list --path=api | grep 'reports/purchase'` → 3 route baru.
- [ ] Tinker/manual company 2: total per grup = SUM bill ter-post.

## Git Checkpoint

- Commit: `feat(reports): purchase aggregation endpoints — summary/by-vendor/by-product (phase 5)`.
- **Dokumentasikan kontrak response** (contoh JSON) di bawah — Fase 6 mengandalkannya.
- Update ledger Fase 5 → ✅.

## Kontrak response (terisi — Fase 6 mengandalkannya)

Semua endpoint dibungkus `ApiResponse::successResponse` → `{ success, message, data }`.
Hanya bill `status = 'posted'` yang dihitung (draft/void di-exclude). Sumber:
`vendor_bills` (kolom `bill_date`, `vendor_id`, `subtotal_after_discount`, `tax_total`,
`grand_total`) + `vendor_bill_lines` (`quantity`, `subtotal_after_discount`, `line_total`,
`product_id`, `product_code`).

**`GET /reports/purchase/summary`** — param: `start_date`, `end_date`, `group_by` (day|month, default month), `department_id`, `project_id`.
```json
{ "data": {
  "rows": [ { "period": "2026-06", "bill_count": 2, "subtotal": 250.0, "tax": 0.0, "total": 250.0 } ],
  "totals": { "bill_count": 2, "subtotal": 250.0, "tax": 0.0, "total": 250.0 }
} }
```
`period` = `YYYY-MM` (month) atau `YYYY-MM-DD` (day). Empty period → `rows: []`.

**`GET /reports/purchase/by-vendor`** — param: date + dimensi + `vendor_id` (opsional). Urut `total` desc.
```json
{ "data": {
  "rows": [ { "vendor_id": 1, "vendor_name": "Vendor Alpha", "bill_count": 2, "subtotal": 250.0, "tax": 0.0, "total": 250.0 } ],
  "totals": { "bill_count": 3, "subtotal": 450.0, "tax": 0.0, "total": 450.0 }
} }
```

**`GET /reports/purchase/by-product`** — param: date + dimensi + `product_id` (opsional). Hanya line dengan `product_id` non-null (join `products`). Urut `total` desc.
```json
{ "data": {
  "rows": [ { "product_id": 1, "product_code": "PRD-A", "product_name": "Product Alpha", "qty": 5.0, "subtotal": 500.0, "total": 500.0 } ],
  "totals": { "qty": 6.0, "subtotal": 700.0, "total": 700.0 }
} }
```

### Catatan implementasi
- **Simetris Fase 3** (sales). Service pakai driver-detect SQLite/MySQL untuk `strftime`/`DATE_FORMAT` di summary; `groupByRaw`/`orderByRaw` dengan ekspresi penuh (alias tidak jalan di SQLite).
- **Feature test seed langsung** `VendorBill`/`VendorBillLine` via model (bukan lewat HTTP create). Alasan: di branch modular ini `VendorBillService::withDraftPurchaseExpenseSnapshots()` mewajibkan setiap line = inventory stock (butuh warehouse) atau fixed_asset — expense line polos ditolak, jadi jalur create+post HTTP tak bisa menghasilkan bill sederhana untuk uji agregasi (VendorBillTest existing pun merah karena aturan ini). Seed langsung ke tabel = deterministik & tepat sasaran untuk laporan.
- `product_name`/`product_code` (bukan `name`/`code`) — kolom aktual `products`.
