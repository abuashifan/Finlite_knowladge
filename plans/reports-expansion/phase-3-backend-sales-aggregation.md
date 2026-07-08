# Fase 3 — Backend Agregasi Penjualan

**Prioritas:** B (design-I2 §7 "Laporan Penjualan: agregasi per pelanggan, per barang")
**Estimasi:** sedang — hanya backend (service + request + route + test). Frontend di Fase 4.

## Tujuan

Bangun endpoint agregasi penjualan yang **belum ada**. Ini laporan rekap (SUM per grup), bukan daftar transaksi. Sumber data: `sales_invoices` + `sales_invoice_lines` (verifikasi nama tabel/model aktual di modul Sales).

## Prasyarat

- Fase 0 ✅. (Fase 1/2 tidak wajib selesai, tapi disarankan.)
- Baca `00-conventions.md` §1 (anatomi backend), §8.
- Konfirmasi model & relasi: `laravel_backend/app/Modules/Sales/` — cari model `SalesInvoice`, `SalesInvoiceLine` (nama pasti bisa beda). Cek kolom: customer_id, product_id, qty, unit_price, line_total, invoice_date, status (hanya hitung faktur ter-post, bukan draft/void).
- Cek tidak ada endpoint agregasi yang sudah ada: `php artisan route:list --path=api | grep -Ei 'sales.*(summary|by-customer|by-product)'`.

## Keputusan lokasi endpoint

Taruh di **modul Reports** dengan sub-prefix `/reports/sales/*` (lihat 00-conventions §8). Controller & service baru di `app/Modules/Reports/`, memanggil model Sales (cross-module read, diperbolehkan — Models layer boleh lintas modul per arch test). Alternatif: taruh di modul Sales `Services/Reports/`. **Default: modul Reports** agar terkumpul. Dokumentasikan pilihan di commit.

## Daftar tugas (endpoint yang dibangun)

Bangun 3 endpoint inti (design-I2 §3.3 prioritas):

### T3.1 — Ringkasan Penjualan per periode — `GET /reports/sales/summary`
- Service: total penjualan (SUM line/invoice total), jumlah faktur, per bulan/hari sesuai `group_by` (opsional). Return `{ rows: [{ period, invoice_count, subtotal, tax, total }], totals: {...} }`.
- FormRequest: start_date, end_date (trait `HasReportDateFilters`), `group_by` in [day,month] opsional, dimensi opsional.

### T3.2 — Penjualan per Pelanggan — `GET /reports/sales/by-customer`
- Service: GROUP BY customer_id → `{ rows: [{ customer_id, customer_name, invoice_count, subtotal, tax, total }], totals: { total } }`. Support mode ringkasan (default). Filter periode + `customer_id` opsional.

### T3.3 — Penjualan per Barang — `GET /reports/sales/by-product`
- Service: GROUP BY product_id dari lines → `{ rows: [{ product_id, product_code, product_name, qty, subtotal, total }], totals: { qty, total } }`. Ini juga menutup "Penjualan Per Barang - Omset/Kuantitas".

### Untuk tiap endpoint T3.1–T3.3
- [ ] Service di `app/Modules/Reports/Services/Sales/` (subfolder baru) — query pakai Eloquent/Query Builder, scope hanya faktur ter-post (exclude draft/void), hormati tenant scope.
- [ ] FormRequest di `app/Modules/Reports/Requests/Sales/`.
- [ ] Controller di `app/Modules/Reports/Controllers/Sales/` (atau satu `SalesReportController` dengan method summary/byCustomer/byProduct).
- [ ] Route di `app/Modules/Reports/Routes/api.php` grup `reports` prefix, `permission:reports.view`.
- [ ] Feature test `tests/Feature/Reports/SalesReport*Test.php`: happy path (seed faktur → assert agregasi benar), exclude void/draft (assert tidak terhitung), permission 403, param invalid 422.

## Peta File

> Backend-only. Semua di `laravel_backend/app/Modules/Reports/`. Model dibaca lintas-modul (`Sales\Models\SalesInvoice`, `SalesInvoiceLine`) — read-only, tidak diubah.

**➕ Tambah**
- `laravel_backend/app/Modules/Reports/Services/Sales/SalesSummaryReportService.php`
- `laravel_backend/app/Modules/Reports/Services/Sales/SalesByCustomerReportService.php`
- `laravel_backend/app/Modules/Reports/Services/Sales/SalesByProductReportService.php`
- `laravel_backend/app/Modules/Reports/Requests/Sales/SalesSummaryReportRequest.php`
- `laravel_backend/app/Modules/Reports/Requests/Sales/SalesByCustomerReportRequest.php`
- `laravel_backend/app/Modules/Reports/Requests/Sales/SalesByProductReportRequest.php`
- `laravel_backend/app/Modules/Reports/Controllers/Sales/SalesReportController.php` — (satu controller, method `summary`/`byCustomer`/`byProduct`)
- `laravel_backend/tests/Feature/Reports/SalesSummaryReportTest.php`
- `laravel_backend/tests/Feature/Reports/SalesByCustomerReportTest.php`
- `laravel_backend/tests/Feature/Reports/SalesByProductReportTest.php`

**✏️ Ubah**
- `laravel_backend/app/Modules/Reports/Routes/api.php` — 3 route `/reports/sales/{summary,by-customer,by-product}`.
- `phase-3-backend-sales-aggregation.md` (file ini) — isi bagian "Kontrak response".

**🗑️ Hapus** — Tidak ada.

> Alternatif lokasi (bila diputuskan taruh di modul Sales, lihat §Keputusan lokasi): ganti prefix `app/Modules/Reports/` → `app/Modules/Sales/` dan subfolder `Services/Reports/`. Dokumentasikan di commit bila memilih ini.

## Checklist Verifikasi

- [ ] `php artisan test --filter=SalesReport` hijau (semua endpoint).
- [ ] `vendor/bin/pint --test` hijau untuk file yang diubah.
- [ ] `php artisan route:list --path=api | grep 'reports/sales'` → 3 route baru.
- [ ] Manual/tinker: jalankan service untuk company 2, angka total per grup = SUM faktur ter-post (bandingkan dengan total di laporan L/R atau list sales).
- [ ] Kontrak response (key JSON) dicatat di `phase-4` bagian "Kontrak" ATAU di README modul Reports — supaya Fase 4 (frontend) menulis adapter yang cocok.

## Git Checkpoint

- Commit backend: `feat(reports): sales aggregation endpoints — summary/by-customer/by-product (phase 3)`.
- **Dokumentasikan kontrak response** (contoh JSON tiap endpoint) di file ini bagian bawah atau di `app/Modules/Reports/README.md` — Fase 4 mengandalkannya.
- Update ledger Fase 3 → ✅.

## Kontrak response (isi setelah implementasi)

> Tempel contoh JSON aktual tiap endpoint di sini setelah selesai, agar Fase 4 punya sumber kebenaran shape tanpa menjalankan backend.

```
GET /reports/sales/summary        → { data: { rows: [...], totals: {...} } }
GET /reports/sales/by-customer    → { data: { rows: [...], totals: {...} } }
GET /reports/sales/by-product     → { data: { rows: [...], totals: {...} } }
```
