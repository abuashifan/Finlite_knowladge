# Fase 2 — AR/AP Outstanding + Subledger Agregat

**Prioritas:** A/B (design-I2 §7 Prioritas A: "Faktur Belum Lunas", "Hutang Yang Belum Lunas")
**Estimasi:** sedang — 2 laporan frontend + kemungkinan 2 endpoint kecil backend.

## Tujuan

Tambah laporan **Faktur Belum Lunas** (AR) dan **Hutang Yang Belum Lunas** (AP) ke kategori `ar` / `ap`. Data berasal dari status belum-lunas di `sales_invoices` / `vendor_bills`.

## Prasyarat

- Fase 0 ✅.
- Cek apakah endpoint outstanding sudah ada:
  - `php artisan route:list --path=api | grep -Ei 'ar|ap|invoice|bill|outstanding|aging'`
  - AR aging (`/sales/ar/aging`) & AP aging (`/purchase/ap/aging`) sudah ada tapi itu *aging bucket*, bukan *daftar faktur belum lunas*. Verifikasi apakah ada endpoint daftar faktur outstanding. Jika **belum**, backend perlu ditambah (T2.1/T2.3).
- Baca `00-conventions.md` §1 (anatomi backend), §8 (ranjau aging).

## Daftar tugas

### T2.1 — Backend: Faktur Penjualan Belum Lunas (jika belum ada)
Modul: **Sales** (`laravel_backend/app/Modules/Sales/`).
- [ ] Cek dulu: mungkin cukup query `sales_invoices` where `status`/`payment_status` outstanding + sisa (`total - paid`). Bisa jadi list invoice existing sudah bisa difilter. Jika list sudah cukup lewat filter status, **skip backend**, pakai endpoint list existing di frontend (T2.2).
- [ ] Jika perlu endpoint report khusus: buat `Services/Reports/ArOutstandingReportService.php` → return `{ rows: [{ invoice_id, invoice_number, invoice_date, due_date, customer_id, customer_name, total, paid, outstanding, days_overdue }], totals: { outstanding } }`.
- [ ] FormRequest `Requests/ArOutstandingReportRequest.php` (filter: as_of_date, customer_id opsional). Controller tipis. Route `GET /reports/ar/outstanding` (atau `/sales/ar/outstanding`) `permission:reports.view`.
- [ ] Feature test: happy path (ada faktur outstanding), permission 403, param invalid 422.

### T2.2 — Frontend: Faktur Belum Lunas
- [ ] Type `ArOutstandingReport` di `reports.types.ts`.
- [ ] Adapter `adaptArOutstanding` + method `reportsApi.arOutstanding(params)` di `reportsApi.ts` (atau, bila pakai list existing, di service sales — dokumentasikan).
- [ ] Page `ArOutstandingReportPage.tsx` (pola §3): kolom Faktur, Tanggal, Jatuh Tempo, Pelanggan, Total, Terbayar, Sisa, Umur (hari). CSV export + pagination.
- [ ] Route `/reports/ar-outstanding`. Katalog kategori `ar` entri baru (hapus `comingSoon` bila ada).

### T2.3 — Backend: Hutang Belum Lunas (jika belum ada)
Modul: **Purchase**. Simetris T2.1: `ApOutstandingReportService`, `vendor_bills` outstanding, route `GET /reports/ap/outstanding`, feature test.

### T2.4 — Frontend: Hutang Belum Lunas
Simetris T2.2: `ApOutstandingReport`, `adaptApOutstanding`, `ApOutstandingReportPage.tsx`, route `/reports/ap-outstanding`, katalog kategori `ap`.

### T2.5 — (Opsional, jika mudah) Subledger agregat Customer/Vendor Summary
design-I2 §3.5/§3.6 menyebut `/ar/customer-summary` & `/ap/vendor-summary` sudah ada di backend tapi belum di `/reports/`.
- [ ] Bila endpoint `/sales/ar/customer-summary` & `/purchase/ap/vendor-summary` ada, tambahkan halaman ringan + entri katalog `ar`/`ap` ("Ringkasan Pelanggan"/"Ringkasan Pemasok"). Jika tidak sempat, tandai `comingSoon` dan catat.

## Peta File

**➕ Tambah — Backend** *(kondisional: hanya bila endpoint outstanding belum ada / list existing tak memadai)*
- `laravel_backend/app/Modules/Reports/Services/AR/ArOutstandingReportService.php`
- `laravel_backend/app/Modules/Reports/Requests/AR/ArOutstandingReportRequest.php`
- `laravel_backend/app/Modules/Reports/Controllers/AR/ArOutstandingReportController.php`
- `laravel_backend/app/Modules/Reports/Services/AP/ApOutstandingReportService.php`
- `laravel_backend/app/Modules/Reports/Requests/AP/ApOutstandingReportRequest.php`
- `laravel_backend/app/Modules/Reports/Controllers/AP/ApOutstandingReportController.php`
- `laravel_backend/tests/Feature/Reports/ArOutstandingReportTest.php`
- `laravel_backend/tests/Feature/Reports/ApOutstandingReportTest.php`

**➕ Tambah — Frontend**
- `react_frontend/src/modules/reports/pages/ArOutstandingReportPage.tsx`
- `react_frontend/src/modules/reports/pages/ApOutstandingReportPage.tsx`

**✏️ Ubah — Backend** *(kondisional, bila endpoint dibuat)*
- `laravel_backend/app/Modules/Reports/Routes/api.php` — route `/reports/ar/outstanding`, `/reports/ap/outstanding`.

**✏️ Ubah — Frontend**
- `react_frontend/src/modules/reports/types/reports.types.ts` — `ArOutstandingReport`, `ApOutstandingReport` (+ param `as_of_date`, `customer_id?`, `vendor_id?`).
- `react_frontend/src/modules/reports/services/reportsApi.ts` — `adaptArOutstanding`/`adaptApOutstanding` + methods.
- `react_frontend/src/modules/reports/routes.tsx` — `/reports/ar-outstanding`, `/reports/ap-outstanding`.
- `react_frontend/src/modules/reports/constants/reportCategories.ts` — entri kategori `ar`/`ap`.
- `react_frontend/docs/struktur_frontend.md` — daftarkan 2 page baru.

**🗑️ Hapus** — Tidak ada.

## Checklist Verifikasi

- [ ] `npm run build` 0 error, `npm run lint` 0 error.
- [ ] Bila backend diubah: `php artisan test --filter=ArOutstanding` / `ApOutstanding` hijau; `pint --test` hijau; route count naik.
- [ ] Runtime company 2: kedua laporan render, angka sisa = total − terbayar, umur hari benar.
- [ ] Katalog `ar`/`ap` tidak lagi hanya berisi aging.
- [ ] `struktur_frontend.md` + (bila backend) feature test terdaftar.

## Git Checkpoint

- Commit backend (bila ada): `feat(reports): AR/AP outstanding report endpoints (phase 2)`.
- Commit frontend: `feat(reports): AR/AP outstanding report pages (phase 2)`.
- Update ledger Fase 2 → ✅.
