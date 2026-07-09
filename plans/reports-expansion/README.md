# Reports Expansion — Index & Progress Ledger

> **Agent: baca file ini PERTAMA setiap sesi.** Ia menentukan fase mana yang sedang berjalan.
>
> Rencana ini mengimplementasikan visi laporan dari
> `react_frontend/docs/design_docs/design-I2-reports-navigation-structure.md`
> (design-I2). **Nav shell (design-I2 §8) SUDAH terbangun** — ribbon = kategori
> domain, tiap kategori = 1 halaman (`ReportCategoryPage` + `ReportDomainPanel`,
> data-driven dari `reportCategories.ts`). Yang tersisa = **mengisi konten
> laporan aktual**: dari 125 laporan referensi in-scope, Finlite baru cover ~11
> penuh + ~15 sebagian; ~91 belum ada. Rencana ini menutup gap itu sesuai
> Prioritas A → B → C (design-I2 §7), termasuk **fase backend** untuk laporan
> yang butuh endpoint baru.

Rencana ini memecah pekerjaan menjadi **fase-fase berdiri sendiri**. Tiap fase
dirancang bisa dikerjakan di **sesi terpisah (cold start)** oleh agent yang
berbeda — agent tidak perlu mengingat pekerjaan fase sebelumnya, cukup membaca
ledger ini + `00-conventions.md` + file fase yang relevan.

## Cara pakai (alur tiap sesi)

1. Baca **`README.md`** ini → lihat tabel ledger di bawah, temukan fase pertama yang `⬜ Belum`.
2. Baca **`00-conventions.md`** → pola halaman laporan, pola adapter API, pola backend service+request+route, permission, aturan verifikasi, definition-of-done per jenis laporan. **Wajib.**
3. Buka **`phase-N-*.md`** untuk fase itu.
4. Jalankan bagian **Prasyarat** di file fase → verifikasi repo memang ada di titik awal yang benar (endpoint yang dibutuhkan sudah ada / entri katalog belum ada / dst).
5. Kerjakan daftar tugas eksplisit di file fase (per laporan: backend dulu bila perlu, lalu frontend, lalu daftarkan di katalog).
6. Jalankan **Checklist Verifikasi** fase.
7. Commit sesuai **Git Checkpoint** fase.
8. **Update ledger di bawah** (`⬜ Belum` → `✅ Selesai` + isi kolom Commit) lalu commit README. **Ini wajib** — inilah memori lintas sesi.

## Progress Ledger

| Fase | Judul | File | Prioritas | Status | Commit |
|------|-------|------|-----------|--------|--------|
| 0 | Fondasi & Audit Nav Shell | `phase-0-foundation.md` | — | ✅ Selesai | 256a476 |
| 1 | Quick Wins Frontend-Only (backend siap) | `phase-1-quick-wins-frontend.md` | A | ✅ Selesai | 64f6264 |
| 2 | AR/AP Outstanding + Subledger Agregat | `phase-2-ar-ap-outstanding.md` | A/B | ✅ Selesai | bc07c7a |
| 3 | Backend Agregasi Penjualan | `phase-3-backend-sales-aggregation.md` | B | ✅ Selesai | — |
| 4 | Frontend Laporan Penjualan | `phase-4-frontend-sales-reports.md` | B | ✅ Selesai | a3150e9 |
| 5 | Backend Agregasi Pembelian | `phase-5-backend-purchase-aggregation.md` | B | ⬜ Belum | — |
| 6 | Frontend Laporan Pembelian | `phase-6-frontend-purchase-reports.md` | B | ⬜ Belum | — |
| 7 | Buku Besar: Pisah Ringkasan/Rincian + Jurnal per Modul | `phase-7-gl-detail-journals.md` | B | ⬜ Belum | — |
| 8 | Inventory: Umur Persediaan, Jurnal Persediaan, Kertas Kerja Opname | `phase-8-inventory-reports.md` | B | ⬜ Belum | — |
| 9 | Laporan Keuangan Lanjutan (Laba Ditahan, Ekuitas, Arus Kas Langsung) | `phase-9-advanced-financial.md` | C | ⬜ Belum | — |
| 10 | Multi-Periode (Neraca/L&R Perbandingan) | `phase-10-multi-period.md` | C | ⬜ Belum | — |
| 11 | Laporan Pajak PPN (Masukan/Keluaran) | `phase-11-tax-ppn.md` | C | ⬜ Belum | — |
| 12 | Ekspor E-Faktur DJP (CSV) | `phase-12-efaktur-export.md` | C | ⬜ Belum | — |
| 13 | Laporan Tersimpan (Saved Reports) | `phase-13-saved-reports.md` | C | ⬜ Belum | — |
| 14 | Modal Parameter Laporan (Filter Data + Column Selection) | `phase-14-report-parameter-modal.md` | B | ⬜ Belum | — |

> Status yang boleh: `⬜ Belum`, `🔄 Berjalan`, `✅ Selesai`. Kalau `🔄 Berjalan` tertinggal dari sesi sebelumnya, jalankan Prasyarat fase itu untuk menentukan seberapa jauh sudah dikerjakan sebelum melanjutkan.

## Prinsip desain

- **Non-blocking / bertahap** — tiap fase menyisakan aplikasi hijau (`npm run build` 0 error; jika backend diubah, test tersempit + Pint hijau). Bisa berhenti kapan saja.
- **Nav shell tidak dibongkar** — Fase 0 hanya mengaudit & merapikan katalog. Fase-fase berikutnya **menambah entri ke `reportCategories.ts`** (mengganti `comingSoon: true` → route nyata), bukan mengubah arsitektur navigasi.
- **Backend sebelum frontend** — laporan yang butuh endpoint baru punya **fase backend tersendiri** (service + FormRequest + route + feature test) yang diselesaikan sebelum fase frontend-nya. Dependency antar-fase dicatat eksplisit di tiap file fase (§Prasyarat).
- **Adapter boundary wajib** — tiap endpoint baru dikonsumsi frontend lewat adapter di `reportsApi.ts` (atau service modul terkait) yang menormalkan response ke shape stabil di `*.types.ts`. Tidak ada page yang membaca `res.data.foo` mentah. (Pelajaran Audit-12 A12-12 / Phase 36.)
- **Cross-module, no duplicate route** — laporan Fixed Assets di-surface ke katalog Reports tapi tetap menunjuk ke route `/reports/fixed-assets/*` yang halamannya sudah ada; tidak menduplikasi halaman.

## Urutan & dependency (ringkas)

```
Fase 0 (fondasi/audit) ─┬─> Fase 1 (quick wins A)
                        ├─> Fase 2 (AR/AP outstanding)
                        ├─> Fase 3 (BE sales) ─> Fase 4 (FE sales)
                        ├─> Fase 5 (BE purchase) ─> Fase 6 (FE purchase)
                        ├─> Fase 7 (GL detail/journals)
                        └─> Fase 8 (inventory)
Fase 9,10,11,12,13 (Prioritas C) — boleh dikerjakan setelah A/B stabil,
  urutan bebas kecuali Fase 12 (E-Faktur) mengandalkan Fase 11 (PPN).
```

## Keputusan yang sudah dikunci (dari design-I2 + sesi review)

1. **Ribbon Reports = kategori domain**, bukan laporan individual. Tiap kategori = route `/reports/:categoryPath` yang merender grid kartu laporan (`ReportDomainPanel`). **Sudah terimplementasi.**
2. **Neraca Saldo** ada di kategori **Buku Besar** (bukan Keuangan) — ikut design-I2 §8. **Sudah sesuai** di `reportCategories.ts`.
3. **Fixed Assets** di-surface di katalog Reports, halaman menunjuk `/reports/fixed-assets/*` (halaman sudah ada). **Sudah sesuai.**
4. **Tidak diimplementasi** (design-I2 §7): serial/batch tracking, laporan per Cabang/Departemen/Proyek sebagai dimensi wajib, Valuasi FIFO, format impor. (Dimensi dept/project sudah ada sebagai *filter opsional* via `ReportFilterParameter`, itu berbeda dari "laporan per departemen".)
5. **Laporan agregasi** Penjualan/Pembelian = rekap per pelanggan/barang/pemasok, **butuh endpoint baru** (bukan sekadar daftar transaksi yang sudah ada di modul sales/purchase).
6. **Cakupan penuh A+B+C** dengan fase backend disertakan (keputusan user 2026-07-08).

## Sumber kebenaran

- Design vision: `react_frontend/docs/design_docs/design-I2-reports-navigation-structure.md`
- Nav shell existing: `react_frontend/src/modules/reports/constants/reportCategories.ts`, `.../pages/ReportCategoryPage.tsx`, `.../components/ReportDomainPanel.tsx`, ribbon di `react_frontend/src/router/moduleConfig.ts`
- Pola halaman & adapter: `react_frontend/src/modules/reports/pages/GeneralLedgerPage.tsx`, `.../services/reportsApi.ts`
- Backend Reports: `laravel_backend/app/Modules/Reports/` (Controllers/Requests/Services/Routes)
- Aturan frontend: `react_frontend/AGENTS.md` + `react_frontend/CLAUDE.md`
- Aturan backend: `laravel_backend/AGENTS.md`
