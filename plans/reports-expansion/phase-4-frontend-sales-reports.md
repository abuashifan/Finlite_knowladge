# Fase 4 — Frontend Laporan Penjualan

**Prioritas:** B
**Estimasi:** sedang — 3 halaman, konsumsi endpoint Fase 3.

## Tujuan

Bangun halaman untuk 3 endpoint agregasi penjualan dari Fase 3, dan aktifkan kategori `sales` di katalog (mengganti placeholder `comingSoon`).

## Prasyarat

- **Fase 3 ✅** — endpoint `/reports/sales/{summary,by-customer,by-product}` ada & diuji. Baca "Kontrak response" di `phase-3-*.md` untuk shape JSON.
- Baca `00-conventions.md` §2 (adapter), §3 (pola halaman), §5 (katalog).
- Katalog saat ini: kategori `sales` punya 2 entri `comingSoon` (`sales-summary`, `sales-by-customer`).

## Daftar tugas

### T4.1 — Types
- [ ] Di `reports.types.ts`: `SalesSummaryReport`, `SalesByCustomerReport`, `SalesByProductReport` (rows + totals sesuai kontrak Fase 3). Tambah param opsional ke `ReportParams` bila perlu (`customer_id?`, `group_by?`).

### T4.2 — Adapters + methods
- [ ] `adaptSalesSummary`, `adaptSalesByCustomer`, `adaptSalesByProduct` di `reportsApi.ts` (pakai num/str/asArray/asRecord).
- [ ] Methods `reportsApi.salesSummary/salesByCustomer/salesByProduct(params)`.

### T4.3 — Halaman
- [ ] `SalesSummaryReportPage.tsx` — tabel per periode (period, jumlah faktur, subtotal, pajak, total) + baris total. Filter periode + `group_by` (day/month) via `ReportFilterParameter` extras. CSV + pagination.
- [ ] `SalesByCustomerReportPage.tsx` — tabel per pelanggan (nama, jumlah faktur, total) urut total desc. Filter periode + customer (opsional pakai `SearchableSelect`). CSV + pagination.
- [ ] `SalesByProductReportPage.tsx` — tabel per barang (kode, nama, qty, total). CSV + pagination.

### T4.4 — Routes + katalog
- [ ] `routes.tsx`: `/reports/sales/summary`, `/reports/sales/by-customer`, `/reports/sales/by-product`.
- [ ] `reportCategories.ts` kategori `sales`: update 2 entri existing (hapus `comingSoon`, betulkan path) + tambah `by-product`. Deskripsi jelas ("agregasi", bukan "daftar transaksi").

### T4.5 — struktur_frontend.md
- [ ] Daftarkan 3 page baru.

## Peta File

> Frontend-only. Konsumsi endpoint Fase 3.

**➕ Tambah**
- `react_frontend/src/modules/reports/pages/SalesSummaryReportPage.tsx`
- `react_frontend/src/modules/reports/pages/SalesByCustomerReportPage.tsx`
- `react_frontend/src/modules/reports/pages/SalesByProductReportPage.tsx`

**✏️ Ubah**
- `react_frontend/src/modules/reports/types/reports.types.ts` — `SalesSummaryReport`, `SalesByCustomerReport`, `SalesByProductReport` (+ param `customer_id?`, `group_by?`).
- `react_frontend/src/modules/reports/services/reportsApi.ts` — `adaptSalesSummary/ByCustomer/ByProduct` + methods.
- `react_frontend/src/modules/reports/routes.tsx` — 3 route `/reports/sales/*`.
- `react_frontend/src/modules/reports/constants/reportCategories.ts` — kategori `sales`: hapus `comingSoon`, betulkan path, tambah `by-product`.
- `react_frontend/docs/struktur_frontend.md` — daftarkan 3 page baru.

**🗑️ Hapus** — Tidak ada.

## Checklist Verifikasi

- [ ] `npm run build` 0 error, `npm run lint` 0 error.
- [ ] Runtime company 2: 3 halaman render, angka cocok dengan Ringkasan Keuangan/L&R untuk periode sama (sanity check total penjualan).
- [ ] Tidak ada `comingSoon` tersisa di kategori `sales`.
- [ ] Kartu di kategori `sales` semua klik → halaman.

## Git Checkpoint

- Commit: `feat(reports): sales aggregation report pages (phase 4)`.
- Update ledger Fase 4 → ✅.
