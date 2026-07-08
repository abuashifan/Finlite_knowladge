# Fase 1 — Quick Wins Frontend-Only (backend siap)

**Prioritas:** A (design-I2 §7 "Backend siap, hanya butuh frontend page")
**Estimasi:** sedang — beberapa halaman, TANPA backend baru.

## Tujuan

Surface laporan yang **endpoint backend-nya sudah ada** tapi belum punya halaman / belum masuk katalog. Ini quick win terbaik (design-I2 §9). Tidak ada perubahan backend.

## Prasyarat

- Fase 0 ✅ (katalog sudah diaudit).
- Verifikasi endpoint berikut ADA (cek `laravel_backend/app/Modules/*/Routes/api.php` atau `php artisan route:list --path=api`):
  - `GET /reports/account-ledger/{account}` — Buku Besar per Akun. **Sudah ada halaman** `AccountLedgerPage` + route `/reports/account-ledger`. → tinggal pastikan masuk katalog (kemungkinan sudah).
  - `GET /cash-bank/reports/account-statement` — Mutasi Rekening. **Sudah ada** `CashBankStatementPage` + route `/reports/account-statement`. → pastikan masuk katalog Kas & Bank.
  - `GET /fixed-assets/reports/{register,depreciation,disposals,reconciliation}` — **sudah ada 4 halaman**. → pastikan katalog benar (Fase 0 sudah tangani).
- Baca `00-conventions.md` §2–5.

## Daftar tugas

> Sebagian besar Fase 1 mungkin **sudah selesai** karena kode lebih maju dari design-I2 §6. Tugas nyata = **audit + isi gap kecil**. Untuk tiap item, cek dulu "sudah ada?" sebelum membangun.

### T1.1 — Buku Besar per Akun (`/reports/account-ledger`)
- [ ] Verifikasi `AccountLedgerPage` render benar (pilih akun COA → tampil mutasi + running balance).
- [ ] Verifikasi entri katalog di kategori `gl` (`account-ledger`) tanpa `comingSoon`. (Saat ini: sudah ada.)
- [ ] Jika ada bug/adapter mismatch, perbaiki via adapter di `reportsApi.ts` (`adaptAccountLedger` sudah ada).

### T1.2 — Mutasi Rekening Kas & Bank (`/reports/account-statement`)
- [ ] Verifikasi `CashBankStatementPage`: pilih rekening kas/bank → tampil mutasi + saldo berjalan.
- [ ] Verifikasi entri katalog kategori `cash-bank`. (Saat ini: sudah ada.)

### T1.3 — Fixed Assets (4 laporan)
- [ ] Verifikasi 4 halaman FA report render benar (register as-of period, depreciation, disposals, reconciliation).
- [ ] Verifikasi 4 entri katalog `fixed-assets` tanpa `comingSoon`.

### T1.4 — Kartu Stok / Laporan Stok / Analisis Inventori
Endpoint sudah ada (`stock-balances`, `stock-movements`, `stock-card`, `valuation`, `low-stock`, `negative-stock`). Halaman `StockReportPage` + `InventoryAnalysisPage` sudah ada.
- [ ] Verifikasi keduanya render + entri katalog `inventory` benar.

### T1.5 — Gap kecil yang mungkin nyata (bangun bila belum ada)
Cek apakah ini sudah ada; bila belum, INI pekerjaan frontend nyata Fase 1:
- [ ] **Semua Jurnal / Jurnal Transaksi** (design-I2 §3.1 #3/#17) — daftar semua jurnal per periode. Cek apakah endpoint jurnal (`/journals`) bisa dipakai sebagai laporan read-only di kategori `gl`. Jika `/journals` list sudah cukup, tambahkan entri katalog yang **link ke halaman journal list existing** (cross-module, no duplicate) ATAU tandai `comingSoon` bila butuh agregasi khusus → serahkan ke Fase 7.
  - Keputusan default: **tandai `comingSoon`**, bangun di Fase 7 (GL detail/journals). Jangan bangun di sini kecuali `/journals` list langsung memadai.

## Peta File

> Fase ini **mayoritas verifikasi** — kemungkinan besar hanya menyentuh katalog, atau bahkan nol perubahan.

**✏️ Ubah**
- `react_frontend/src/modules/reports/constants/reportCategories.ts` — hapus `comingSoon` untuk laporan yang halaman+endpoint-nya sudah siap; tambah entri yang belum terdaftar (account-ledger, account-statement, FA).
- `react_frontend/src/modules/reports/services/reportsApi.ts` — hanya bila ada adapter mismatch pada laporan existing (perbaikan, bukan tambah).
- `react_frontend/docs/struktur_frontend.md` — hanya bila ada file baru (kemungkinan tidak).

**➕ Tambah**
- Tidak ada (semua halaman quick-win sudah ada). Kecuali T1.5 memutuskan membangun halaman "Semua Jurnal" di sini — default: TIDAK, diserahkan ke Fase 7.

**🗑️ Hapus**
- Tidak ada.

## Checklist Verifikasi

- [ ] `npm run build` 0 error, `npm run lint` 0 error.
- [ ] 3 kategori (gl, cash-bank, fixed-assets, inventory) semua kartu klik → halaman render tanpa crash di company 2.
- [ ] Tidak ada `comingSoon` tersisa untuk laporan yang endpoint+halamannya sudah ada.
- [ ] `struktur_frontend.md` konsisten (kemungkinan tidak berubah bila tidak ada file baru).

## Git Checkpoint

- Commit: `feat(reports): surface backend-ready reports in catalog (phase 1)`.
- Update ledger Fase 1 → ✅ + commit hash, commit di `Finlite_Knowladge`.

> Jika saat audit ternyata SEMUA sudah beres tanpa perubahan kode, tetap tandai Fase 1 ✅ dengan catatan "verified, no changes needed" di ledger — agar fase berikut tahu quick-wins sudah tervalidasi.
