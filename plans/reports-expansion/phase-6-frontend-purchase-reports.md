# Fase 6 — Frontend Laporan Pembelian

**Prioritas:** B
**Estimasi:** sedang — 3 halaman, simetris Fase 4.

## Tujuan

Halaman untuk 3 endpoint agregasi pembelian Fase 5; aktifkan kategori `purchase` (ganti placeholder `comingSoon`).

## Prasyarat

- **Fase 5 ✅** — endpoint `/reports/purchase/{summary,by-vendor,by-product}` ada & diuji. Baca "Kontrak response" di `phase-5-*.md`.
- Baca `00-conventions.md` §2–5, dan `phase-4-frontend-sales-reports.md` (pola identik — tiru).
- Katalog `purchase` saat ini: 2 entri `comingSoon` (`purchase-summary`, `purchase-by-vendor`).

## Daftar tugas

### T6.1 — Types
- [ ] `PurchaseSummaryReport`, `PurchaseByVendorReport`, `PurchaseByProductReport` di `reports.types.ts`.

### T6.2 — Adapters + methods
- [ ] `adaptPurchaseSummary/ByVendor/ByProduct` + `reportsApi.purchaseSummary/purchaseByVendor/purchaseByProduct`.

### T6.3 — Halaman
- [ ] `PurchaseSummaryReportPage.tsx`, `PurchaseByVendorReportPage.tsx`, `PurchaseByProductReportPage.tsx` — pola §3, CSV + pagination + filter periode (+ vendor/group_by opsional).

### T6.4 — Routes + katalog
- [ ] `routes.tsx`: `/reports/purchase/summary`, `/reports/purchase/by-vendor`, `/reports/purchase/by-product`.
- [ ] `reportCategories.ts` kategori `purchase`: hapus `comingSoon`, betulkan path, tambah `by-product`.

### T6.5 — struktur_frontend.md
- [ ] Daftarkan 3 page baru.

## Peta File

> Frontend-only. Konsumsi endpoint Fase 5.

**➕ Tambah**
- `react_frontend/src/modules/reports/pages/PurchaseSummaryReportPage.tsx`
- `react_frontend/src/modules/reports/pages/PurchaseByVendorReportPage.tsx`
- `react_frontend/src/modules/reports/pages/PurchaseByProductReportPage.tsx`

**✏️ Ubah**
- `react_frontend/src/modules/reports/types/reports.types.ts` — `PurchaseSummaryReport`, `PurchaseByVendorReport`, `PurchaseByProductReport` (+ param `vendor_id?`, `group_by?`).
- `react_frontend/src/modules/reports/services/reportsApi.ts` — `adaptPurchaseSummary/ByVendor/ByProduct` + methods.
- `react_frontend/src/modules/reports/routes.tsx` — 3 route `/reports/purchase/*`.
- `react_frontend/src/modules/reports/constants/reportCategories.ts` — kategori `purchase`: hapus `comingSoon`, betulkan path, tambah `by-product`.
- `react_frontend/docs/struktur_frontend.md` — daftarkan 3 page baru.

**🗑️ Hapus** — Tidak ada.

## Checklist Verifikasi

- [ ] `npm run build` 0 error, `npm run lint` 0 error.
- [ ] Runtime company 2: 3 halaman render; total pembelian cocok dengan L/R (beban/HPP) untuk sanity.
- [ ] Tidak ada `comingSoon` tersisa di kategori `purchase`.

## Git Checkpoint

- Commit: `feat(reports): purchase aggregation report pages (phase 6)`.
- Update ledger Fase 6 → ✅.
