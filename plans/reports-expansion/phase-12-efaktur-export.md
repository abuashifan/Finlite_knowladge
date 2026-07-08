# Fase 12 — Ekspor E-Faktur DJP (CSV)

**Prioritas:** C (design-I2 §3.10, §7 "E-Faktur export format DJP")
**Estimasi:** sedang–besar — format CSV khusus DJP, backend baru.

## Tujuan

Ekspor **E-Faktur Penjualan** & **E-Faktur Pembelian** dalam format CSV DJP (berbeda dari CSV export laporan biasa — punya skema kolom baku DJP). design-I2 §9: "butuh format khusus".

## Prasyarat

- **Fase 11 ✅** — data PPN (masukan/keluaran) sudah tersedia; E-Faktur memakai data yang sama + NPWP/identitas.
- **Klarifikasi spesifikasi format DJP dengan user** — skema kolom E-Faktur (FK/FM lines), versi format, encoding. Tanpa spec format, tidak bisa akurat. Konfirmasi dulu.
- Baca `00-conventions.md` §1–5.
- Cek data identitas pajak: NPWP customer/vendor, nomor faktur pajak — apakah tersimpan? Bila tidak, laporan terbatas / butuh field baru (migration).

## Daftar tugas

### T12.1 — Backend: generator CSV E-Faktur Penjualan — `GET /reports/tax/efaktur/sales`
- [ ] Service menghasilkan baris sesuai skema DJP (header FK + detail FM per faktur). Endpoint mengembalikan CSV (Content-Type text/csv) atau JSON rows yang di-CSV-kan di frontend — **putuskan**: default **backend menghasilkan CSV siap-unduh** karena format DJP ketat.
- [ ] FormRequest (periode, masa pajak), controller (streamed download), route, feature test (assert baris & kolom sesuai skema).

### T12.2 — Backend: generator CSV E-Faktur Pembelian — `GET /reports/tax/efaktur/purchase`
- [ ] Simetris T12.1 dari vendor_bills + PPN masukan.

### T12.3 — Frontend: halaman ekspor
- [ ] `EfakturExportPage.tsx` — pilih masa pajak/periode + tombol "Unduh CSV Penjualan" / "Unduh CSV Pembelian". Panggil endpoint download (blob) — bukan render tabel besar. Bila backend return JSON, pakai `exportCsv` lokal; bila backend return CSV, trigger download langsung.
- [ ] Route `/reports/tax/efaktur`. Katalog: entri di kategori `tax` ("Ekspor E-Faktur").

### T12.4 — struktur_frontend.md
- [ ] Daftarkan page baru.

## Peta File

> Reuse kategori `tax` dari Fase 11 (tidak menambah ribbon lagi). Backend menghasilkan CSV siap-unduh (format DJP ketat).

**➕ Tambah — Backend**
- `laravel_backend/app/Modules/Reports/Services/Tax/EfakturSalesExportService.php`
- `laravel_backend/app/Modules/Reports/Services/Tax/EfakturPurchaseExportService.php`
- `laravel_backend/app/Modules/Reports/Requests/Tax/EfakturExportRequest.php`
- `laravel_backend/app/Modules/Reports/Controllers/Tax/EfakturExportController.php` *(streamed CSV download)*
- `laravel_backend/tests/Feature/Reports/EfakturExportTest.php`

**➕ Tambah — Frontend**
- `react_frontend/src/modules/reports/pages/EfakturExportPage.tsx`

**✏️ Ubah — Backend**
- `laravel_backend/app/Modules/Reports/Routes/api.php` — route `/reports/tax/efaktur/sales`, `/reports/tax/efaktur/purchase`.
- `laravel_backend/database/migrations/tenant/*` — **(kondisional)** hanya bila field identitas pajak (NPWP, no faktur pajak) belum ada di contact/invoice dan harus ditambah.

**✏️ Ubah — Frontend**
- `react_frontend/src/modules/reports/services/reportsApi.ts` — method download blob e-faktur (bukan adapter tabel).
- `react_frontend/src/modules/reports/routes.tsx` — `/reports/tax/efaktur`.
- `react_frontend/src/modules/reports/constants/reportCategories.ts` — entri di kategori `tax`.
- `react_frontend/docs/struktur_frontend.md`.

**🗑️ Hapus** — Tidak ada.

## Checklist Verifikasi

- [ ] `npm run build`/`lint` 0 error.
- [ ] Backend test hijau (validasi skema kolom CSV DJP); `pint --test` hijau; route naik.
- [ ] Runtime: unduh CSV berhasil, buka di spreadsheet, kolom sesuai skema DJP yang dikonfirmasi user.

## Git Checkpoint

- Commit backend: `feat(reports): e-faktur DJP CSV export endpoints (phase 12)`.
- Commit frontend: `feat(reports): e-faktur export page (phase 12)`.
- Update ledger Fase 12 → ✅.
