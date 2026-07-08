# Fase 11 — Laporan Pajak PPN (Masukan / Keluaran)

**Prioritas:** C (design-I2 §3.9, §7 "Laporan Pajak PPN")
**Estimasi:** besar — backend baru + **kategori navigasi baru** (`tax`).

## Tujuan

Bangun **Daftar PPN Masukan** (input VAT dari pembelian) & **Daftar PPN Keluaran** (output VAT dari penjualan). design-I2 §9: "butuh backend baru yang membaca dari journal entries yang tagged sebagai tax". Ini kategori pertama yang **menambah item ribbon baru**.

## Prasyarat

- Fase 0 ✅; A/B stabil disarankan.
- **Klarifikasi sumber data PPN dengan user**: apakah ada akun PPN Masukan/Keluaran di COA? Apakah faktur menyimpan komponen pajak (tax amount per line/header)? Cek modul Sales/Purchase (kolom tax di invoice/bill) & COA. Tanpa data pajak yang tersimpan, laporan tidak bisa dibuat — **konfirmasi ketersediaan data dulu**.
- Baca `00-conventions.md` §1–5, audit-07.

## Daftar tugas

### T11.1 — Backend: PPN Keluaran — `GET /reports/tax/output-vat`
- [ ] Service: daftar faktur penjualan dengan komponen PPN dalam periode → `{ rows: [{ invoice_number, invoice_date, customer_name, dpp (base), ppn (tax), total }], totals: { dpp, ppn } }`. Sumber: sales_invoices tax fields ATAU journal entries akun PPN keluaran.
- [ ] FormRequest (periode), controller, route `permission:reports.view` (atau granular `reports.tax.view` bila diputuskan), feature test.

### T11.2 — Backend: PPN Masukan — `GET /reports/tax/input-vat`
- [ ] Simetris: vendor_bills tax fields / akun PPN masukan. `{ rows: [{ bill_number, bill_date, vendor_name, dpp, ppn, total }], totals }`.

### T11.3 — Frontend: 2 halaman
- [ ] Types `OutputVatReport`/`InputVatReport`, adapters, methods.
- [ ] `OutputVatReportPage.tsx` & `InputVatReportPage.tsx` (pola §3, CSV + pagination). Kolom DPP, PPN, Total.

### T11.4 — Kategori navigasi BARU `tax`
- [ ] `reportCategories.ts`: tambah domain `{ id: 'tax', label: 'Pajak', categoryPath: 'tax', reports: [ppn-keluaran, ppn-masukan] }`.
- [ ] `router/moduleConfig.ts` grup `reports`: tambah item ribbon `{ id: 'tax', label: 'Pajak', icon: <ikon>, path: '/reports/tax', permission: 'reports.view' }`. (Ini satu-satunya fase yang menyentuh ribbon — lihat 00-conventions §5.)
- [ ] Routes `/reports/tax/output-vat`, `/reports/tax/input-vat`.

### T11.5 — struktur_frontend.md
- [ ] Daftarkan 2 page baru.

## Peta File

> **Satu-satunya fase yang menambah kategori ribbon baru (`tax`)** → menyentuh `moduleConfig.ts`.

**➕ Tambah — Backend**
- `laravel_backend/app/Modules/Reports/Services/Tax/OutputVatReportService.php`
- `laravel_backend/app/Modules/Reports/Services/Tax/InputVatReportService.php`
- `laravel_backend/app/Modules/Reports/Requests/Tax/OutputVatReportRequest.php`
- `laravel_backend/app/Modules/Reports/Requests/Tax/InputVatReportRequest.php`
- `laravel_backend/app/Modules/Reports/Controllers/Tax/TaxReportController.php` *(method `outputVat`/`inputVat`)*
- `laravel_backend/tests/Feature/Reports/OutputVatReportTest.php`
- `laravel_backend/tests/Feature/Reports/InputVatReportTest.php`

**➕ Tambah — Frontend**
- `react_frontend/src/modules/reports/pages/OutputVatReportPage.tsx`
- `react_frontend/src/modules/reports/pages/InputVatReportPage.tsx`

**✏️ Ubah — Backend**
- `laravel_backend/app/Modules/Reports/Routes/api.php` — route `/reports/tax/output-vat`, `/reports/tax/input-vat`.
- `laravel_backend/database/seeders/*Permission*` — **(kondisional)** bila memakai permission granular `reports.tax.view` (default: pakai `reports.view`, tak perlu).

**✏️ Ubah — Frontend**
- `react_frontend/src/modules/reports/types/reports.types.ts` — `OutputVatReport`, `InputVatReport`.
- `react_frontend/src/modules/reports/services/reportsApi.ts` — 2 adapter + methods.
- `react_frontend/src/modules/reports/routes.tsx` — 2 route baru.
- `react_frontend/src/modules/reports/constants/reportCategories.ts` — **tambah domain baru `tax`**.
- `react_frontend/src/router/moduleConfig.ts` — **tambah item ribbon `tax`** di grup `reports` (satu-satunya fase yang ubah ribbon).
- `react_frontend/docs/struktur_frontend.md`.

**🗑️ Hapus** — Tidak ada.

## Checklist Verifikasi

- [ ] `npm run build`/`lint` 0 error.
- [ ] Backend test PPN hijau; `pint --test` hijau; route naik (2).
- [ ] Kategori "Pajak" muncul di ribbon Reports; klik → halaman kategori dengan 2 kartu.
- [ ] Runtime company 2: total PPN keluaran/masukan cocok dengan saldo akun PPN di neraca (sanity).

## Git Checkpoint

- Commit backend: `feat(reports): input/output VAT (PPN) report endpoints (phase 11)`.
- Commit frontend: `feat(reports): PPN reports + Tax nav category (phase 11)`.
- Update ledger Fase 11 → ✅.
