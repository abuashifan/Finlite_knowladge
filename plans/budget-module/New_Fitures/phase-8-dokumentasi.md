# Phase 8 — Dokumentasi & Verifikasi Menyeluruh

> Prasyarat: fase 7 selesai.

## Objective

Menutup lingkaran: dokumen yang mengklaim sesuatu harus cocok dengan kode. Audit menemukan
setidaknya satu dokumen yang sudah salah selama dua bulan tanpa ketahuan.

---

## Files affected

| File | Perubahan |
|---|---|
| `laravel_backend/docs/backend-directory-tree.md` | Tanggal + tree + hitungan direktori. **Definition of Done** bila ada direktori baru (`app/Modules/Budget/Support/`, `tests/Unit/Budget/`). Perintah regenerasinya ada di dalam file itu. |
| `laravel_backend/docs/backend-missing-modules-audit.md` | Baris 123–138 masih menyatakan *"No tenant tables or API routes exist for budgets"*. **Stale sejak 2026-06-15** — modul Budget dibuat setelahnya. Perbaiki. |
| `frontend/docs/struktur_frontend.md` | Entri budget di baris 399–415 + semua file baru fase 7 |
| `frontend/docs/gap_docs/gap-12-budget-module.md` | Rancangan asli modul, dideklarasikan "sumber kebenaran tunggal". Grain data berubah di fase 1, jadi dokumen ini **wajib** diberi penanda dan tautan ke `New_Fitures/`. Jangan dihapus — ia menjelaskan alur approval yang masih berlaku. |
| `Finlite_knowladge/plans/budget-module/README.md` | Tandai 4 temuan terbuka jadi ✅ selesai dengan tautan ke `New_Fitures/phase-3`; tambahkan tautan ke `New_Fitures/README.md` |
| `Finlite_knowladge/plans/budget-module/New_Fitures/README.md` | Progress ledger: semua fase → ✅ Selesai, catat commit |
| `Finlite_knowladge/reference/02-backend.md` · `03-frontend.md` · `04-komponen-reusable.md` | Hanya bila ada konvensi baru yang muncul dari pekerjaan ini |
| `app/Modules/Budget/README.md` | Perbedaan `revision_number` vs `version_no`, tangga spesifisitas, definisi variance |

### Penyimpangan dari rencana

Bila ada yang dikerjakan berbeda dari rencana — dan biasanya ada — **catat di
`New_Fitures/README.md` beserta alasannya**, mengikuti pola §"Penyimpangan dari rencana" di
`../README.md`. Penyimpangan yang tidak dicatat terbaca sebagai kelalaian oleh pembaca berikutnya.

---

## Verifikasi otomatis

```bash
cd /workspace/laravel_backend
vendor/bin/pint --test
php artisan test tests/Unit/Budget
php artisan test tests/Feature/Budget          # 7 test lama harus tetap lulus
php artisan test tests/Feature/Sales           # regresi dimensi revenue (fase 4)
php artisan test tests/Feature/Journal         # regresi peringatan over-budget (fase 3)
php artisan test tests/Feature/Reports         # P&L / Trial Balance tidak berubah
php artisan test tests/Feature/Architecture    # batas modul

cd /workspace/frontend
npm run build
npm run lint
```

Suite backend penuh ±6 menit — **jalankan hanya di fase ini**, tidak di fase sebelumnya.

Pemeriksaan tambahan:

```bash
grep -rn "strftime" app/Modules/Budget/       # harus kosong (fase 3)
grep -rn "as ModuleKey" ../frontend/src/      # tidak boleh ada untuk 'budget' (fase 7)
```

---

## Edge case yang wajib tercakup test

Dari brief §TESTING PLAN, semuanya harus punya test yang membuktikannya:

| Kategori | Kasus |
|---|---|
| Nominal | Budget 0 · Actual 0 · Actual > Budget · Actual < Budget · Actual = Budget |
| Pendapatan | Revenue > Budget · Revenue < Budget |
| Beban | Expense > Budget · Expense < Budget |
| Proyek | dengan revenue · tanpa revenue · hanya beban · tanpa transaksi sama sekali |
| Cakupan | anggaran tanpa transaksi · transaksi tanpa anggaran |
| Versi | multi versi · revisi setelah approved · reject sebelum approved |
| Koreksi | reversal · refund · credit/debit note · penyesuaian negatif |
| Waktu | periode tertutup · periode parsial · anggaran tahunan vs bulanan |
| Tenancy | isolasi antar perusahaan |

---

## Verifikasi manual

Butuh backend hidup. Prosedur 9 langkah di `../README.md` **belum pernah dijalankan** karena
backend mati saat rencana sebelumnya dikerjakan — jalankan yang itu **dan** yang ini.

1. Buat periode anggaran → daftar menampilkannya
2. Buat pengajuan untuk sebuah cost center; isi baris **lintas dimensi** — akun + cost center +
   proyek + bulan, beberapa baris dengan kombinasi berbeda dalam satu pengajuan
3. Ajukan → setujui sebagai Kepala → setujui sebagai Finance
4. **Revisi** anggaran yang sudah approved → versi 2 muncul sebagai draft, versi 1 jadi
   `superseded` dan **masih terbaca** dengan nominal aslinya
5. Post jurnal yang melampaui anggaran → toast peringatan muncul (regresi jalur lama)
6. Post jurnal **tanpa** departemen → **tidak** memicu peringatan anggaran departemen mana pun
7. Buat sales invoice bertanda proyek → periksa `journal_entry_lines.project_id` **terisi**
8. Halaman Analisis: drill-down Total → Cost Center → Proyek → Akun; angka konsisten tiap level
9. Cash Budget: `Beginning + Inflow − Outflow = Ending`; catatan asumsi akrual tampil
10. Project Financial Summary: Revenue, Cost, Profit, Margin terisi; catatan keterbatasan
    invoice lama tampil
11. Riwayat Versi: v1, v2, v3 terbaca dengan alasan revisi masing-masing
12. Anggaran akun **pendapatan** yang melampaui target ditampilkan **hijau** (favorable),
    bukan merah

**Bersihkan data uji setelah selesai** — `budget_periods` harus kembali 0 di kedua tenant.

---

## Dependencies

Fase 7 (dan karenanya seluruh fase sebelumnya).

---

## Risks

| Risiko | Mitigasi |
|---|---|
| Verifikasi manual dilewati lagi karena backend mati | Jangan tandai fase ini selesai sebelum 12 langkah dijalankan. Kalau backend tidak bisa dinyalakan, tandai `🔄 Berjalan` dan catat apa yang belum diuji — persis seperti yang jujur dilakukan rencana sebelumnya. |
| Data uji tertinggal di tenant demo | Langkah pembersihan di atas; verifikasi `budget_periods` = 0. |
| Dokumen diperbarui setengah-setengah | Daftar di §Files affected adalah checklist. Coret satu per satu. |

---

## Hasil implementasi — 2026-08-14

Status: **🔄 Berjalan** — dokumentasi selesai, verifikasi manual belum.

### Checklist §Files affected

| File | Status |
|---|---|
| `laravel_backend/docs/backend-directory-tree.md` | ✅ tanggal + `Modules/Budget/Support` + 220 → 221 direktori |
| `laravel_backend/docs/backend-missing-modules-audit.md` | ✅ §6 dikoreksi — klaim *"No tenant tables or API routes exist for budgets"* **salah sejak 2026-06-29**; isi lama dipertahankan di dalam `<details>` sebagai catatan sejarah |
| `frontend/docs/struktur_frontend.md` | ✅ 5 halaman + `hooks/` + `schemas/` |
| `frontend/docs/gap_docs/gap-12-budget-module.md` | ✅ diberi penanda SUPERSEDED + tabel "dulu vs sekarang"; tidak dihapus karena alur approval-nya masih berlaku |
| `Finlite_knowladge/plans/budget-module/README.md` | ✅ 4 temuan → selesai + tautan ke fase 3; header menunjuk ke `New_Fitures/` |
| `New_Fitures/README.md` | ✅ progress ledger + 8 penyimpangan tercatat |
| `reference/02-backend.md` · `03-frontend.md` · `04-komponen-reusable.md` | ⬜ tidak diubah — tidak ada konvensi baru yang muncul (`LineItemsTable.footer` sudah dicatat di fase 0.1) |
| `app/Modules/Budget/README.md` | ✅ dibuat di fase 1 |

### Verifikasi otomatis

```
php artisan test                              → 1388 lulus, 5 skipped, 0 gagal (1393 total)
vendor/bin/pint --test <file yang diubah>     → bersih
grep -rn "strftime" app/Modules/Budget/       → nol pemakaian (hanya komentar)
grep -rn "journal_entry_lines" app/Modules/Budget/ → nol query (hanya README)
grep -rn "as ModuleKey" ../frontend/src/      → 1 hasil generik di Topbar.tsx, bukan khusus 'budget'
npm run build / npm run lint                  → hijau, 0 error
```

`tests/Unit/Budget` **tidak dibuat** — resolver butuh koneksi tenant, jadi test-nya feature
test. Menaruhnya di `tests/Unit/` akan menyesatkan.

### Edge case dari brief §TESTING PLAN

| Kategori | Tercakup? |
|---|---|
| Nominal (budget 0, actual 0, >, <, =) | ✅ `BudgetAnalysisTest` |
| Pendapatan >/< budget | ✅ `BudgetAnalysisTest`, `BudgetWarningTest` |
| Beban >/< budget | ✅ `BudgetAnalysisTest`, `BudgetViewsTest` |
| Proyek: dengan revenue · tanpa revenue · hanya beban · tanpa transaksi | ✅ `BudgetViewsTest` |
| Anggaran tanpa transaksi · transaksi tanpa anggaran | ✅ `BudgetAnalysisTest` |
| Versi: multi versi · revisi setelah approved · reject sebelum approved | ✅ `BudgetVersioningTest` |
| Waktu: periode parsial · tahunan vs bulanan | ✅ `BudgetAnalysisTest`, `BudgetWarningTest` |
| **Koreksi: reversal · refund · credit/debit note · penyesuaian negatif** | ⚠️ **tidak ada test khusus.** Secara desain semuanya jurnal balik ter-post yang otomatis mengurangi actual, dan jurnal `is_obsolete` sudah diuji dikecualikan — tapi jalur reversal end-to-end belum dibuktikan test tersendiri |
| **Periode akuntansi tertutup** | ⚠️ **belum ada test.** `PeriodLockService::isDateReadOnly()` belum disambungkan ke pembuatan/revisi anggaran (§6 business rules menyebutnya, implementasinya belum) |
| **Tenancy: isolasi antar perusahaan** | ⚠️ **belum ada test khusus** di modul ini |

### Verifikasi manual — BELUM DIJALANKAN

Dua belas langkah di §Verifikasi manual **belum satu pun dijalankan** — butuh backend hidup.
Sesuai §Risks, fase ini karenanya ditandai `🔄 Berjalan`, bukan `✅ Selesai`.

Data uji: **tidak ada yang ditambahkan ke tenant demo.** Seluruh test memakai tenant SQLite
sementara yang dibersihkan di `tearDown()`; `budget_periods` di kedua tenant demo tetap 0.

---

## Acceptance criteria

1. Tidak ada dokumen yang mengklaim sesuatu yang tidak benar tentang modul Budget.
2. Seluruh perintah verifikasi otomatis hijau.
3. Dua belas langkah verifikasi manual dijalankan dan hasilnya dicatat.
4. Data uji dibersihkan.
5. Progress ledger di `New_Fitures/README.md` terisi lengkap, termasuk penyimpangan.

---

# FUTURE EXTENSION — bukan MUST HAVE

Desain fase 1–8 tidak menghalangi apa pun berikut, dan **tak satu pun butuh menulis ulang mesin
inti**. Ini yang membedakan desain ini dari menambal.

| Fitur | Jalur penambahan |
|---|---|
| **Forecast** | Kolom `scenario` pada `budget_submissions`; `BudgetAnalysisService` tinggal memfilternya |
| **Rolling Budget** | Periode bergulir = beberapa `budget_periods` bersambung; agregasi sudah lintas-periode |
| **Flexible Budget** | Kolom `driver` + `rate` pada `budget_lines`; nominal jadi turunan volume |
| **Scenario Budget** (best/worst/base) | Sama seperti Forecast — kolom `scenario` sudah cukup |
| **Multi-year Budget** | `budget_periods` sudah menyimpan rentang tanggal bebas, bukan hanya satu tahun |
| **What-if Analysis** | Murni pembacaan di atas `BudgetAnalysisService`, tanpa perubahan skema |
| **Cash timing lewat termin** | `payment_terms` sudah ada; jadi penghalus di `BudgetCashService` |
| **Multi-company consolidation** | **Terhalang arsitektur** — tenancy satu DB per perusahaan. Butuh agregator lintas-DB tersendiri. |
| **Scoping "Dept lihat miliknya"** | Butuh rancangan relasi user↔departemen lebih dulu; lihat `phase-0` §6 |

Alasan semuanya murah: dimensi ada di baris, angka turunan tidak disimpan, dan seluruh view
lahir dari satu service. Menambah dimensi atau skenario berarti menambah kolom dan satu klausa
filter — bukan membangun engine baru.
