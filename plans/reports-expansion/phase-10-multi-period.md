# Fase 10 — Multi-Periode (Neraca / L&R Perbandingan)

**Prioritas:** C (design-I2 §7 "Multi-periode: Neraca/L&R perbandingan antar bulan/tahun")
**Estimasi:** besar — API contract baru (backend saat ini 1 periode per request). Butuh diskusi kontrak (design-I2 §9).

## Tujuan

Laporan perbandingan antar-periode design-I2 §3.2: Neraca Multi-Periode, L&R Multi-Periode, Perbandingan Bulan (side-by-side).

## Prasyarat

- Fase 0 ✅; **Fase 9 disarankan selesai** (pola laporan keuangan lanjutan).
- **KLARIFIKASI KONTRAK API DENGAN USER SEBELUM CODING.** Backend saat ini return 1 periode. Opsi:
  - (a) Backend menerima array periode → return kolom per periode. (Direkomendasikan.)
  - (b) Frontend memanggil endpoint 1-periode N kali lalu menggabung. (Lebih sederhana, tapi N request.)
  Putuskan bersama user; catat di file ini. Default rekomendasi: **(a)** untuk L&R/Neraca (backend baru), **(b)** hanya bila (a) terlalu mahal.
- Baca `00-conventions.md`, audit-07.

## Daftar tugas

### T10.1 — Backend: dukung multi-periode (bila opsi a)
- [ ] Extend `ProfitLossService` & `BalanceSheetService` untuk menerima `periods[]` (mis. `[{start,end,label}, ...]`) → return sections dengan nilai per periode. Atau endpoint baru `/reports/profit-loss/multi-period` & `/reports/balance-sheet/multi-period`.
- [ ] FormRequest validasi array periode (max N, format tanggal). Controller/route/feature test.

### T10.2 — Frontend: Neraca Multi-Periode
- [ ] Type + adapter (sections dengan nilai per kolom periode). Page `BalanceSheetMultiPeriodPage.tsx` — tabel dengan kolom per periode. Selector periode (2–4 kolom). Route `/reports/balance-sheet-multi`, katalog `financial`.

### T10.3 — Frontend: L&R Multi-Periode
- [ ] Simetris T10.2: `ProfitLossMultiPeriodPage.tsx`, route `/reports/profit-loss-multi`, katalog `financial`.

### T10.4 — Perbandingan Bulan (side-by-side)
- [ ] Varian dari multi-periode dengan preset bulan Jan..Des tahun berjalan. Bisa mode di halaman multi-periode (preset "12 bulan") daripada halaman terpisah. Default: **mode preset**, bukan halaman baru.

### T10.5 — Katalog & struktur
- [ ] Entri `financial`: "Neraca Multi-Periode", "Laba Rugi Multi-Periode". `struktur_frontend.md`.

## Peta File

> Backend hanya bila **opsi (a)** dipilih (endpoint terima array periode). Opsi (b) = frontend memanggil endpoint 1-periode N kali → tak ada file backend baru.

**➕ Tambah — Backend** *(kondisional: opsi a)*
- `laravel_backend/app/Modules/Reports/Requests/MultiPeriodReportRequest.php` *(validasi `periods[]`)*
- `laravel_backend/app/Modules/Reports/Controllers/MultiPeriodReportController.php` *(method `profitLoss`/`balanceSheet`)*
- `laravel_backend/tests/Feature/Reports/MultiPeriodReportTest.php`

**✏️ Ubah — Backend** *(kondisional: opsi a)*
- `laravel_backend/app/Modules/Reports/Services/ProfitLossService.php` — dukung `periods[]`.
- `laravel_backend/app/Modules/Reports/Services/BalanceSheetService.php` — dukung `periods[]`.
- `laravel_backend/app/Modules/Reports/Routes/api.php` — route `/reports/profit-loss/multi-period`, `/reports/balance-sheet/multi-period`.

**➕ Tambah — Frontend**
- `react_frontend/src/modules/reports/pages/BalanceSheetMultiPeriodPage.tsx`
- `react_frontend/src/modules/reports/pages/ProfitLossMultiPeriodPage.tsx`
- `react_frontend/src/modules/reports/components/PeriodSelector.tsx` *(kondisional: bila belum ada komponen selector multi-periode reusable)*

**✏️ Ubah — Frontend**
- `react_frontend/src/modules/reports/types/reports.types.ts` — type multi-period (sections dgn nilai per kolom).
- `react_frontend/src/modules/reports/services/reportsApi.ts` — adapter multi-period (+ helper gabung N request bila opsi b).
- `react_frontend/src/modules/reports/routes.tsx` — 2 route baru.
- `react_frontend/src/modules/reports/constants/reportCategories.ts` — kategori `financial`.
- `react_frontend/docs/struktur_frontend.md`.

**🗑️ Hapus** — Tidak ada.

## Checklist Verifikasi

- [ ] `npm run build`/`lint` 0 error.
- [ ] Backend (bila opsi a): test multi-period hijau; `pint --test` hijau; route naik.
- [ ] Runtime: kolom per periode benar; total tiap kolom = laporan single-period untuk periode itu (sanity vs Fase existing).
- [ ] Performa: N periode tidak menyebabkan timeout (bila opsi b, batasi N).

## Git Checkpoint

- Commit backend (bila ada): `feat(reports): multi-period P&L/balance-sheet contract (phase 10)`.
- Commit frontend: `feat(reports): multi-period comparison pages (phase 10)`.
- Update ledger Fase 10 → ✅.

## Kontrak API multi-periode (isi setelah diputuskan)

> Catat keputusan (a)/(b) + shape request/response di sini sebelum coding frontend.
