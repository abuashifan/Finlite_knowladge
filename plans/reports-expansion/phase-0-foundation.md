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
