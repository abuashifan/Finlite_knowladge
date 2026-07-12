# Fase 9 — Laporan Keuangan Lanjutan

**Prioritas:** C (design-I2 §7 "Laba Ditahan, Perubahan Ekuitas, Arus Kas metode langsung")
**Estimasi:** besar — butuh desain akuntansi + backend baru. Konsultasi audit-07.

## Tujuan

Menutup laporan keuangan lanjutan design-I2 §3.2 yang butuh logika akuntansi baru:
- **Laba Ditahan (Retained Earnings)**
- **Perubahan Ekuitas Pemilik (Statement of Equity)**
- **Arus Kas Metode Langsung** (rincian) — pelengkap metode tidak langsung yang sudah ada.
- **Arus Kas Tidak Langsung - Rincian** (breakdown per akun) — endpoint cash-flow saat ini sudah 3-seksi (Phase 36 A13-243); "rincian" = per akun.

## Prasyarat

- Fase 0 ✅; disarankan A/B (Fase 1–8) sudah stabil dulu.
- **Baca `react_frontend/docs/audit_docs/audit-07-accounting-and-reporting-audit.md`** — kontrak akuntansi & aturan.
- Baca `00-conventions.md` §1–3.
- Modul **Reports** + **Accounting**/**Journal**. Cek `CashFlowService` (sudah punya `getSectionedCashFlow`).
- **Klarifikasi API contract dengan user/audit sebelum coding** (design-I2 §9: "Multi-periode & lanjutan butuh diskusi API contract").

## Daftar tugas

### T9.1 — Laba Ditahan — `GET /reports/retained-earnings` (backend baru)
- [x] Service: akumulasi laba/rugi tahun-tahun sebelumnya + laba tahun berjalan, per periode. Butuh definisi akun retained earnings di COA + hasil period-end closing. Cek modul period-end/fiscal-year closing.
- [x] FormRequest (as_of_date / fiscal_year), controller, route, feature test.
- [x] Frontend: type, adapter, `RetainedEarningsReportPage.tsx`, route, katalog `financial`.

### T9.2 — Perubahan Ekuitas — `GET /reports/equity-changes` (backend baru)
- [x] Service: saldo ekuitas awal + setoran/penarikan + laba/rugi periode → saldo akhir, per komponen ekuitas. 
- [x] Request/controller/route/test + frontend page `EquityChangesReportPage.tsx`, katalog `financial`.

### T9.3 — Arus Kas Metode Langsung — `GET /reports/cash-flow-direct` (backend baru)
- [x] Service: klasifikasi penerimaan/pembayaran kas aktual (dari cash/bank movements) ke operasi/investasi/pendanaan. Berbeda dari metode tidak langsung (yang menyesuaikan laba).
- [x] Request/controller/route/test + frontend page atau mode tambahan di `CashFlowPage` (toggle Langsung/Tidak Langsung).

### T9.4 — Arus Kas Tidak Langsung - Rincian
- [x] **Sudah lengkap tanpa perubahan.** `CashFlowService` sudah mengembalikan `sections` (per-seksi) + `accounts` (per akun kas), dan `CashFlowPage.tsx` existing sudah merender KEDUANYA (tabel klasifikasi seksi + tabel rincian per akun kas/bank). Tidak ada backend/adapter yang perlu diubah.

### T9.5 — Katalog & struktur
- [x] Entri kategori `financial`: "Laba Ditahan", "Perubahan Ekuitas", "Arus Kas (Langsung)". `struktur_frontend.md`.

## Peta File

> Semua backend di modul Reports. Angka akuntansi sensitif — validasi vs audit-07.

**➕ Tambah — Backend**
- `laravel_backend/app/Modules/Reports/Services/RetainedEarningsService.php`
- `laravel_backend/app/Modules/Reports/Services/EquityChangesService.php`
- `laravel_backend/app/Modules/Reports/Services/CashFlowDirectService.php`
- `laravel_backend/app/Modules/Reports/Requests/RetainedEarningsRequest.php`
- `laravel_backend/app/Modules/Reports/Requests/EquityChangesRequest.php`
- `laravel_backend/app/Modules/Reports/Requests/CashFlowDirectRequest.php`
- `laravel_backend/app/Modules/Reports/Controllers/RetainedEarningsController.php`
- `laravel_backend/app/Modules/Reports/Controllers/EquityChangesController.php`
- `laravel_backend/app/Modules/Reports/Controllers/CashFlowDirectController.php`
- `laravel_backend/tests/Feature/Reports/RetainedEarningsReportTest.php`
- `laravel_backend/tests/Feature/Reports/EquityChangesReportTest.php`
- `laravel_backend/tests/Feature/Reports/CashFlowDirectReportTest.php`

**➕ Tambah — Frontend**
- `react_frontend/src/modules/reports/pages/RetainedEarningsReportPage.tsx`
- `react_frontend/src/modules/reports/pages/EquityChangesReportPage.tsx`
- `react_frontend/src/modules/reports/pages/CashFlowDirectReportPage.tsx` *(atau mode toggle di `CashFlowPage.tsx` — putuskan T9.3)*

**✏️ Ubah — Backend**
- `laravel_backend/app/Modules/Reports/Routes/api.php` — route retained-earnings, equity-changes, cash-flow-direct.
- `laravel_backend/app/Modules/Reports/Services/CashFlowService.php` — **(kondisional T9.4)** breakdown per akun bila belum lengkap.

**✏️ Ubah — Frontend**
- `react_frontend/src/modules/reports/types/reports.types.ts` — 3 type baru.
- `react_frontend/src/modules/reports/services/reportsApi.ts` — 3 adapter + methods.
- `react_frontend/src/modules/reports/pages/CashFlowPage.tsx` — **(kondisional T9.4)** render detail per akun / toggle langsung.
- `react_frontend/src/modules/reports/routes.tsx` — 3 route baru.
- `react_frontend/src/modules/reports/constants/reportCategories.ts` — kategori `financial`: 3 entri baru.
- `react_frontend/docs/struktur_frontend.md`.

**🗑️ Hapus** — Tidak ada.

## Checklist Verifikasi

- [x] `npm run build`/`lint` 0 error.
- [x] Backend test per endpoint hijau; `pint --test` hijau; route naik.
- [x] Runtime company 2 + validasi akuntansi: laba ditahan konsisten dengan neraca (ekuitas), arus kas langsung ≈ perubahan saldo kas periode.
- [x] **Angka divalidasi terhadap audit-07 / laporan existing** (ini laporan akuntansi sensitif — salah angka = bug serius).

## Git Checkpoint

- Commit backend: `feat(reports): retained earnings, equity changes, direct cash flow (phase 9)`.
- Commit frontend: `feat(reports): advanced financial report pages (phase 9)`.
- Update ledger Fase 9 → ✅.
