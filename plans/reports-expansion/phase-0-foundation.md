# Fase 0 — Fondasi & Audit Nav Shell

**Prioritas:** — (prasyarat semua fase)
**Estimasi:** kecil (audit + rapikan, tanpa laporan baru)

## Tujuan

Memastikan nav shell yang sudah ada benar-benar sesuai design-I2 §8, merapikan katalog, dan menyiapkan konvensi teknis (helper/type) yang dipakai fase-fase berikutnya. **Tidak menambah laporan baru** — hanya audit + fondasi.

## Prasyarat

- Repo frontend hijau: `cd react_frontend && npm run build` 0 error.
- Baca `00-conventions.md` §1–5.
- Buka `react_frontend/src/modules/reports/constants/reportCategories.ts` dan `router/moduleConfig.ts` grup `reports`.

## Daftar tugas

### T0.1 — Audit katalog vs design-I2 §8
Bandingkan `REPORT_DOMAINS` dengan tabel target design-I2 §8. Untuk tiap kategori, verifikasi:
- [ ] Kategori ada di `REPORT_DOMAINS` DAN sebagai item ribbon di `moduleConfig.ts` grup `reports`.
- [ ] `Neraca Saldo` berada di kategori **Buku Besar** (`gl`), bukan Keuangan. (Cek: saat ini sudah benar.)
- [ ] Setiap `path` di `ReportEntry` cocok dengan route nyata di `routes.tsx` ATAU ditandai `comingSoon: true`. Tidak boleh ada path yang mengarah ke route tak terdaftar tanpa `comingSoon`.
- [ ] Kategori `reconciliation` (saat ini `reports: []`) — putuskan: isi dengan entri yang menunjuk `/reports/reconciliation` (halaman `ReconciliationPage` sudah punya 6 tab) ATAU biarkan kosong dengan catatan. **Rekomendasi:** tambahkan 1 entri `{ id: 'reconciliation-all', title: 'Rekonsiliasi', description: 'AR · AP · Inventory · GRNI · Deposits', path: '/reports/reconciliation' }` agar kategori tidak tampil kosong.

Catat temuan sebagai daftar di commit message / catatan fase. Perbaiki mismatch yang ditemukan (path salah, kategori hilang dari ribbon, dll).

### T0.2 — Surface Fixed Assets di katalog (verifikasi, bukan bangun)
- [ ] Konfirmasi 4 entri FA di kategori `fixed-assets` menunjuk `/reports/fixed-assets/*` dan halaman + route-nya benar-benar ada (`routes.tsx` baris 47–50, pages ada). Jika sudah benar (saat audit ini: sudah), tidak ada perubahan. Jika `comingSoon` masih menempel di salah satu, hapus.

### T0.3 — Fondasi type & helper untuk laporan agregasi
Fase 3–8 akan butuh type/adapter untuk laporan "rows + totals". Siapkan pola reusable:
- [ ] Di `reports.types.ts`, tambah type generik ringan bila belum ada, mis. `interface AggregateReportRow { [k: string]: string | number | null }` TIDAK dipakai (hindari `any`/index-signature longgar) — sebagai gantinya, **jangan** buat type generik; cukup pastikan helper `num/str/asArray/asRecord` di `reportsApi.ts` sudah ada (sudah ada) dan terekspor bila fase lain perlu. Bila belum diekspor dan fase lain butuh, ekspor `asRecord/asArray/num/str` dari sebuah `reports/services/adapterHelpers.ts` (refactor kecil: pindahkan helper ke file itu, re-import di `reportsApi.ts`). **Opsional** — lakukan hanya jika mempermudah; kalau tidak, biarkan helper lokal dan tiap fase menambah helper sendiri.
- [ ] Pastikan `ReportParams` di `reports.types.ts` mengakomodasi param umum (start_date, end_date, department_id, project_id, warehouse_id, dan tempat untuk param baru). Bila fase berikut butuh param baru (mis. `customer_id`, `product_id`, `group_by`), tambahkan secara opsional di sana saat fase itu, bukan sekarang.

> Catatan: T0.3 sengaja konservatif — jangan over-engineer fondasi. Cukup pastikan tidak ada blocker. Kalau ragu, lewati refactor helper dan biarkan tiap fase menambah helpernya sendiri.

### T0.4 — Dokumentasikan status "sudah ada vs belum" di plan
- [ ] Buat tabel ringkas (di commit note atau file `phase-0-foundation.md` bagian bawah) memetakan tiap laporan design-I2 §4 ke fase mana di rencana ini yang akan membangunnya. Ini membantu agent fase berikut tahu di mana laporannya. (Sudah sebagian tercermin di ledger `README.md`; lengkapi bila ada laporan yang belum ter-assign ke fase manapun.)

## Peta File

**✏️ Ubah**
- `react_frontend/src/modules/reports/constants/reportCategories.ts` — isi kategori `reconciliation` yang kosong; betulkan path/entri yang mismatch.
- `react_frontend/src/router/moduleConfig.ts` — hanya bila audit menemukan kategori hilang/salah di ribbon grup `reports`.
- `react_frontend/src/modules/reports/routes.tsx` — hanya bila ada path katalog tanpa route (kemungkinan tidak).
- `react_frontend/docs/struktur_frontend.md` — bila membuat `adapterHelpers.ts` (opsional).

**➕ Tambah**
- `react_frontend/src/modules/reports/services/adapterHelpers.ts` — **(kondisional/opsional)** hanya bila memutuskan mengekstrak helper `num/str/asArray/asRecord`. Default: TIDAK dibuat.

**🗑️ Hapus**
- Tidak ada.

## T0.4 — Hasil Mapping Laporan design-I2 → Fase

> Tabel ini dibuat saat Fase 0 dijalankan (2026-07-09). Status kolom Finlite diambil dari design-I2 §3–4.

| Domain | Laporan (representatif) | Status Finlite | Fase yang Menangani |
|---|---|---|---|
| **Keuangan** | Neraca, Laba Rugi, Arus Kas, Ringkasan | ✅ ada | — (sudah selesai) |
| **Keuangan** | Laba Ditahan, Ekuitas, Arus Kas Langsung | ❌ belum | Fase 9 |
| **Keuangan** | Neraca/L&R Multi Periode & Perbandingan | ❌ belum | Fase 10 |
| **Buku Besar** | Buku Besar (ringkasan per akun) | ✅ ada | — |
| **Buku Besar** | Buku Besar per Akun (drill-down) | ✅ ada | — |
| **Buku Besar** | Neraca Saldo | ✅ ada | — |
| **Buku Besar** | Semua Jurnal / Jurnal per Modul / Jurnal Transaksi | ❌ belum | Fase 7 |
| **Penjualan** | Ringkasan Penjualan per Periode | ❌ belum | Fase 3 (BE) → Fase 4 (FE) |
| **Penjualan** | Penjualan per Pelanggan | ❌ belum | Fase 3 (BE) → Fase 4 (FE) |
| **Penjualan** | Penjualan per Barang | ❌ belum | Fase 3 (BE) → Fase 4 (FE) |
| **Pembelian** | Ringkasan Pembelian per Periode | ❌ belum | Fase 5 (BE) → Fase 6 (FE) |
| **Pembelian** | Pembelian per Supplier | ❌ belum | Fase 5 (BE) → Fase 6 (FE) |
| **Pembelian** | Pembelian per Barang | ❌ belum | Fase 5 (BE) → Fase 6 (FE) |
| **AR / Piutang** | AR Aging | ✅ ada | — |
| **AR / Piutang** | Faktur Belum Lunas, Subledger Agregat | ❌ belum | Fase 2 |
| **AP / Hutang** | AP Aging | ✅ ada | — |
| **AP / Hutang** | Hutang Belum Lunas, Subledger Agregat | ❌ belum | Fase 2 |
| **Rekonsiliasi** | Rekonsiliasi AR/AP/Inventory/GRNI/Deposit | ✅ ada (6 tab di ReconciliationPage) | — (halaman sudah ada, katalog diisi Fase 0) |
| **Persediaan** | Laporan Stok, Analisis Inventori | ✅ ada | — |
| **Persediaan** | Umur Persediaan, Jurnal Persediaan, Kertas Kerja Opname | ❌ belum | Fase 8 |
| **Aktiva Tetap** | Register, Penyusutan, Pelepasan, Rekonsiliasi | ✅ ada (4 halaman) | — (Fase 1 verifikasi) |
| **Kas & Bank** | Mutasi Rekening | ✅ ada | — |
| **Pajak** | PPN Masukan / PPN Keluaran | ❌ belum | Fase 11 (BE+FE) |
| **E-Faktur** | Export E-Faktur DJP CSV | ❌ belum | Fase 12 |
| **Laporan Tersimpan** | Saved Reports (user custom) | ❌ belum | Fase 13 |
| **Modal Parameter** | Floating modal filter + column selection | ❌ belum | Fase 14 |

**Audit temuan lain (2026-07-09):**
- Kategori `reconciliation` di `REPORT_DOMAINS` sebelumnya `reports: []` → diisi 1 entri menunjuk `/reports/reconciliation` (ReconciliationPage sudah ada dengan 6 tab).
- Semua `path` non-`comingSoon` di katalog sudah punya route di `routes.tsx` ✅
- Ribbon `reports` di `moduleConfig.ts`: 10 kategori, sesuai dengan 10 domain di `REPORT_DOMAINS` ✅
- FA 4 entri sudah ada di routes dan halaman ✅; tidak ada `comingSoon` pada FA ✅
- Route `/reports/budget/comparison` ada di `routes.tsx` tapi tidak di `REPORT_DOMAINS` — ini disengaja, budget comparison diakses dari modul Budget, bukan dari katalog Reports.
- Helper `num/str/asArray/asRecord` ada di `reportsApi.ts` sebagai fungsi lokal (tidak diekspor) — sesuai keputusan T0.3 konservatif, dibiarkan lokal.

## Checklist Verifikasi

- [ ] `npm run build` 0 error, `npm run lint` 0 error.
- [ ] Tidak ada `ReportEntry.path` yang menunjuk route tak terdaftar tanpa `comingSoon`.
- [ ] Kategori `reconciliation` tidak lagi kosong (atau keputusan didokumentasikan).
- [ ] Setiap laporan target design-I2 §4 sudah ter-assign ke sebuah fase di ledger.
- [ ] `docs/struktur_frontend.md` di-update bila ada file baru (mis. `adapterHelpers.ts`).

## Git Checkpoint

- Branch frontend baru bila di default (mis. `feat/reports-expansion`).
- Commit: `chore(reports): audit & align nav catalog with design-I2 (phase 0)`.
- Update ledger `README.md` Fase 0 → ✅ + commit hash, commit di repo `Finlite_Knowladge`.
