# Fase 8 — Inventory: Umur Persediaan, Jurnal Persediaan, Kertas Kerja Opname

**Prioritas:** B (design-I2 §7 "Inventory: Kertas Kerja Fisikal dari data opname, Jurnal Persediaan"; §3.7 gap)
**Estimasi:** sedang–besar — beberapa butuh backend baru.

## Tujuan

Menutup gap inventory design-I2 §3.7 di luar yang sudah ada (stock balance/movement/card/valuation/low/negative sudah ada). Fokus:
- **Umur Persediaan (Inventory Aging)** — ringkasan & rincian.
- **Jurnal Persediaan** — jurnal terkait pergerakan stok.
- **Kertas Kerja Fisikal (Opname Worksheet)** — dari data stock opname.
- **Valuasi Rincian** — pisah dari ringkasan (endpoint sama, detail belum dipisah).

## Prasyarat

- Fase 0 ✅.
- Baca `00-conventions.md` §1–3, §8 (ranjau: response inventory `{filters,rows,totals}`).
- Modul **Inventory** (`app/Modules/Inventory/`). Cek model: `StockBalance`, `StockMovement`, `StockOpname`, `StockAdjustment`. Cek endpoint existing `route:list | grep inventory/reports`.
- Finlite pakai **average cost**, BUKAN FIFO — jangan bangun valuasi FIFO (design-I2 §7 "tidak akan diimplementasi"). Umur persediaan berbasis tanggal movement/received, bukan lot FIFO.

## Daftar tugas

### T8.1 — Umur Persediaan — `GET /inventory/reports/aging` (backend baru)
- [x] Service: hitung umur stok per produk/gudang berdasarkan tanggal penerimaan terakhir / rata-rata, bucket (0-30, 31-60, 61-90, >90 hari). Return `{ rows: [{ product_id, product_name, warehouse_name, qty, buckets:{...}, value }], totals }`. **Klarifikasi metode aging dengan data** (received date vs last movement) — dokumentasikan asumsi.
- [x] FormRequest (as_of_date, warehouse_id opsional), controller, route `permission:inventory.stock.view` atau `reports.view`, feature test.
- [x] Frontend: type `InventoryAgingReport`, adapter, `InventoryAgingReportPage.tsx`, route `/reports/inventory-aging`, katalog `inventory`.

### T8.2 — Jurnal Persediaan — `GET /inventory/reports/journal` (atau reuse journal report Fase 7)
- [x] Bila Fase 7 sudah membuat journal report dengan filter source, **reuse** dengan filter source inventory (movement/adjustment). Tambah entri katalog `inventory` yang membuka `JournalListReportPage` dengan filter inventory. Tidak perlu backend baru bila Fase 7 memadai.
- [x] Bila Fase 7 belum jalan, buat endpoint kecil khusus jurnal inventory ATAU tandai `comingSoon` sampai Fase 7. Default: **depend on Fase 7 bila sudah selesai; else comingSoon**.

### T8.3 — Kertas Kerja Fisikal (Opname Worksheet) — `GET /inventory/reports/opname-worksheet` (backend baru)
- [x] Service dari data `StockOpname`: qty sistem vs qty fisik vs selisih per produk/gudang untuk satu sesi opname. Return `{ opname_id, rows: [{ product, warehouse, system_qty, physical_qty, difference, value_difference }], totals }`.
- [x] FormRequest (opname_id atau periode), controller, route, feature test.
- [x] Frontend: type, adapter, `OpnameWorksheetReportPage.tsx`, route `/reports/inventory-opname`, katalog `inventory`.

### T8.4 — Valuasi Rincian
- [~] **DITUNDA (bukan comingSoon di katalog).** Finlite memakai average cost — tidak ada lot/layer, sehingga "rincian valuasi per lot/FIFO" tidak relevan. Rincian per-gudang sudah tersedia lewat Laporan Stok (saldo per produk×gudang) + Analisis Inventori (valuasi). Tidak ada entri katalog baru ditambah agar tidak menyesatkan. Bila kelak diperlukan breakdown per-movement, dapat memakai Kartu Stok existing. Keputusan didokumentasikan di sini.

### T8.5 — Katalog & struktur
- [x] Tambah entri kategori `inventory`: "Umur Persediaan", "Jurnal Persediaan", "Kertas Kerja Opname", (opsional "Valuasi Rincian").
- [x] `struktur_frontend.md` daftarkan page baru.

## Peta File

> Endpoint inventory tinggal di **modul Inventory** (bukan Reports) agar sejalan dengan endpoint inventory report existing (`/inventory/reports/*`). Model: `Inventory\Models\{StockBalance,StockMovement,StockOpname,StockOpnameLine,StockAdjustment}`.

**➕ Tambah — Backend**
- `laravel_backend/app/Modules/Inventory/Services/Reports/InventoryAgingReportService.php`
- `laravel_backend/app/Modules/Inventory/Services/Reports/OpnameWorksheetReportService.php`
- `laravel_backend/app/Modules/Inventory/Requests/Reports/InventoryAgingReportRequest.php`
- `laravel_backend/app/Modules/Inventory/Requests/Reports/OpnameWorksheetReportRequest.php`
- `laravel_backend/app/Modules/Inventory/Controllers/Reports/InventoryAgingReportController.php` *(atau tambah method ke controller reports inventory existing — cek dulu)*
- `laravel_backend/app/Modules/Inventory/Controllers/Reports/OpnameWorksheetReportController.php`
- `laravel_backend/tests/Feature/Reports/InventoryAgingReportTest.php`
- `laravel_backend/tests/Feature/Reports/OpnameWorksheetReportTest.php`

> Verifikasi nama controller/dir reports inventory existing dulu (`app/Modules/Inventory/Controllers/`) — ikuti pola yang sudah ada, jangan buat subfolder baru bila sudah ada konvensi lain.

**➕ Tambah — Frontend**
- `react_frontend/src/modules/reports/pages/InventoryAgingReportPage.tsx`
- `react_frontend/src/modules/reports/pages/OpnameWorksheetReportPage.tsx`

**✏️ Ubah — Backend**
- `laravel_backend/app/Modules/Inventory/Routes/api.php` — route `/inventory/reports/aging`, `/inventory/reports/opname-worksheet`.
- `.../Services/Reports/InventoryValuationReportService.php` — **(kondisional T8.4)** mode `detail` bila mudah.

**✏️ Ubah — Frontend**
- `react_frontend/src/modules/reports/types/reports.types.ts` — `InventoryAgingReport`, `OpnameWorksheetReport`.
- `react_frontend/src/modules/reports/services/reportsApi.ts` — adapter aging & opname (ingat: response inventory dibungkus `{filters,rows,totals}`).
- `react_frontend/src/modules/reports/routes.tsx` — `/reports/inventory-aging`, `/reports/inventory-opname`.
- `react_frontend/src/modules/reports/constants/reportCategories.ts` — kategori `inventory`: entri Umur Persediaan, Jurnal Persediaan (link ke Fase 7), Kertas Kerja Opname.
- `react_frontend/docs/struktur_frontend.md` — daftarkan page baru.

**🗑️ Hapus** — Tidak ada. (T8.2 Jurnal Persediaan reuse Fase 7 — tanpa backend baru.)

## Checklist Verifikasi

- [x] `npm run build` 0 error, `npm run lint` 0 error.
- [x] Backend: `php artisan test --filter=InventoryAging`/`OpnameWorksheet` hijau; `pint --test` hijau; route count naik.
- [x] Runtime company 2: umur persediaan bucket masuk akal; opname worksheet selisih = fisik − sistem.

## Git Checkpoint

- Commit backend: `feat(reports): inventory aging & opname worksheet endpoints (phase 8)`.
- Commit frontend: `feat(reports): inventory aging, journal, opname worksheet pages (phase 8)`.
- Update ledger Fase 8 → ✅.
