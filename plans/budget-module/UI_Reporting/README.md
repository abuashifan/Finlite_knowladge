# UI & Reporting Anggaran — Rencana Induk

**Dibuat**: 2026-08-15
**Prasyarat**: `../New_Fitures/` fase 0–8 selesai (mesin anggaran multidimensi sudah jalan)
**Ruang lingkup**: halaman list, form input, dan katalog laporan. **Bukan** mesin baru.

---

## Premis

Mesin anggaran sudah selesai dan teruji (87 test, 22 view terlayani). Yang belum
ada adalah **jalan bagi pengguna untuk sampai ke sana**. Nyaris seluruh pekerjaan
di rencana ini adalah navigasi, halaman daftar, dan preset — bukan logika bisnis.

Satu prinsip yang diwarisi dari rencana sebelumnya dan tidak boleh dilanggar:

> **ONE BUDGET ENGINE → MULTIPLE DIMENSIONS → MULTIPLE VIEWS.**
> Halaman baru adalah *preset* di atas `BudgetAnalysisService`. Kalau sebuah
> halaman butuh query agregasi sendiri, itu tanda desainnya salah — bukan tanda
> mesinnya kurang.

Konsekuensi praktis: dari 22 view yang diminta, **21 sudah punya endpoint**.
Rencana ini hampir seluruhnya frontend. Satu-satunya endpoint backend baru ada
di fase 2, dan itu pun hanya daftar — bukan agregasi.

---

## Temuan yang memicu rencana ini

Saat memverifikasi "apakah tab Anggaran di form Proyek terhubung ke modul Budget
yang baru", ditemukan **tiga cacat di `ProyekFormPage.tsx`**, dua di antaranya
membuat halaman itu tidak berfungsi sama sekali. Rinciannya di
[`phase-0-temuan-dan-aturan.md`](phase-0-temuan-dan-aturan.md).

Ringkas:

| # | Cacat | Dampak |
|---|---|---|
| T1 | Tab "Anggaran" adalah mockup mati — `budgetLines` tidak pernah masuk payload | Pengguna mengisi anggaran, menekan Simpan, data hilang tanpa pesan error |
| T2 | `code` wajib di backend, tidak ada di form | **Buat Proyek selalu gagal 422** |
| T3 | Mode edit tidak pernah memuat data proyek | Buka proyek yang ada → form kosong; menyimpan akan menimpa nama dengan string kosong |

T2 dan T3 adalah bug produksi yang berdiri sendiri, tidak berkaitan dengan
anggaran. Keduanya diperbaiki lebih dulu (fase 1) sebelum halaman baru dibangun.

---

## Keputusan yang sudah diambil

| # | Pertanyaan | Keputusan | Alasan |
|---|---|---|---|
| K1 | Tab "Anggaran" di form Proyek mau diapakan? | **Read-only + tautan ke modul Budget** | Menulis `budget_lines` dari sini akan jadi pintu tulis kedua yang melewati periode, approval, dan versioning. Tab tetap ada sebagai konteks, sumbernya `/budget/projects/{id}/summary`. |
| K2 | Objek utama grup "Budget" di menu | **Submission**, bukan Period | Approval dan versioning hidup di submission. "Detail" dan "Revision" di menu hanya masuk akal kalau objeknya submission. Period turun jadi master data pendukung. |

---

## Peta view → status

Nomor mengikuti daftar 22 view yang disepakati.

### Sudah ada endpoint DAN halaman

| # | View | Halaman |
|---|---|---|
| 1 | Budget by Account | `BudgetAnalysisPage` (preset) |
| 2 | Budget by Period | `BudgetAnalysisPage` (preset) |
| 5 | Budget by Cost Center | `BudgetAnalysisPage` (preset) |
| 6 | Budget by Project | `BudgetAnalysisPage` (preset) |
| 7 | Multi-dimensional | `BudgetAnalysisPage` (group_by bebas) |
| 8 | Budget vs Actual | `BudgetAnalysisPage` / `BudgetComparisonPage` |
| 9 | Variance Analysis | `BudgetAnalysisPage` (mode=variance) |
| 10 | Budget Utilization | `BudgetAnalysisPage` (preset) |
| 18 | Project Profitability | `ProjectFinancialSummaryPage` |
| 19 | Project Margin | idem |
| 21 | Project Transactions | tabel di `ProjectFinancialSummaryPage` |
| 22 | Cash Budget | `CashBudgetPage` |

### Sudah ada endpoint, BELUM ada halaman/preset sendiri → ✅ ditutup 2026-08-15

| # | View | Endpoint | Fase | Cara dijangkau sekarang |
|---|---|---|---|---|
| 3 | Budget Allocation | param `allocation` | 4 | Toggle "Alokasi" (aktif saat `group_by` memuat `period`) |
| 4 | Budget Revision | `/budget-submissions/{id}/versions` + `/revise` | 3 | Tombol di halaman detail + breadcrumb |
| 11 | Remaining Budget | field `variance` | 4 | Kolom "Sisa Anggaran" saat `direction=expense` |
| 12 | Summary & Drill-down | `/budget/summary` | 4 | `?preset=summary` + drill-down 4 level |
| 13 | Revenue Budget | `direction=revenue` | 4 | Filter Arah |
| 14 | Expense Budget | `direction=expense` | 4 | Filter Arah |
| 15 | Project Budget | `/budget/projects/{id}/summary` → `budget` | 5 | `?tab=budget` |
| 16 | Project Actual | idem → `actual` | 5 | `?tab=actual` |
| 17 | Project Budget vs Actual | idem, berdampingan | 5 | `?tab=profitability` |
| 20 | Project Cash Flow | `/budget/projects/{id}/cash-flow` | 5 | `?tab=cash-flow` |

### Belum ada sama sekali → ✅ ditutup 2026-08-15

| Kebutuhan | Fase | Hasil |
|---|---|---|
| Daftar submission lintas periode (backend + halaman) | 2, 3 | `GET /budget-submissions` + `/budget/submissions` |

**Seluruh 22 view kini terjangkau dari UI.** Yang tersisa adalah verifikasi
manual (fase 7) dan keterbatasan G11 yang bukan milik rencana ini.

---

## Fase

| Fase | Judul | Sisi | Status |
|---|---|---|---|
| 0 | [Temuan & aturan](phase-0-temuan-dan-aturan.md) | — | ✅ Selesai |
| 1 | [Perbaikan form Proyek](phase-1-perbaikan-form-proyek.md) | FE | ✅ Selesai |
| 2 | [Endpoint daftar submission](phase-2-endpoint-daftar-submission.md) | BE | ✅ Selesai |
| 3 | [Halaman Budget: daftar, buat, detail, revisi](phase-3-halaman-budget.md) | FE | ✅ Selesai |
| 4 | [Monitoring & preset laporan](phase-4-monitoring.md) | FE | ✅ Selesai |
| 5 | [Halaman Project](phase-5-halaman-project.md) | FE | ✅ Selesai |
| 6 | [Navigasi ANGGARAN & katalog LAPORAN](phase-6-navigasi-dan-katalog.md) | FE | ✅ Selesai |
| 7 | [Test & dokumentasi](phase-7-test-dan-dokumentasi.md) | — | 🔄 Berjalan — 48 langkah verifikasi manual belum dijalankan |

Urutan bukan selera: fase 1 memperbaiki bug yang sudah menyala di produksi,
fase 2 membuka data yang dibutuhkan fase 3, dan fase 6 baru masuk akal setelah
semua halaman yang mau ditautkan sudah ada.

---

---

## Penyimpangan dari rencana — 2026-08-15

Ditulis di sini, bukan hanya di dokumen fase, karena inilah yang berguna dibaca
enam minggu lagi.

| # | Rencana | Yang terjadi | Alasan |
|---|---|---|---|
| P1 | Ribbon ANGGARAN pakai grup bertingkat | Grup ditandai **garis pemisah vertikal**, bukan submenu | `RibbonPanel` adalah strip horizontal `fixed` setinggi 64px berisi tombol ikon, bukan menu bertingkat. Menambah tingkat berarti mendesain ulang layout bersama yang dipakai 9 modul lain. Field `group?` ditambahkan **opsional**, jadi modul lain tidak tersentuh. |
| P2 | Domain laporan "Cash & Bank" baru | Dipakai domain `cash-bank` yang **sudah ada** | Domainnya sudah ada berisi "Mutasi Rekening". Membuat domain kedua bernama sama akan memecah menu tanpa alasan. |
| P3 | `is_active` divalidasi `boolean` | Divalidasi `in:true,false,1,0` | Aturan `boolean` Laravel menolak string `"true"`/`"false"`, dan query string tidak punya tipe boolean — `?is_active=false` selalu tiba sebagai string. Ketahuan dari test yang gagal 422, bukan dari review. |
| P4 | Fase 3 §4 menambah tombol Riwayat Versi & Revisi | **Sudah ada** sejak fase 5 rencana sebelumnya | Yang benar-benar kurang hanya breadcrumb. Verifikasi lebih dulu menghemat pekerjaan yang tidak perlu. |
| P5 | — (tidak direncanakan) | `key` remount pada `BudgetAnalysisPage` & `ProjectFinancialSummaryPage` | Semua entri Monitoring mendarat di rute yang sama dan hanya berbeda `?preset=`. React Router tidak me-remount saat query berubah, jadi tanpa `key` berpindah menu akan mengubah URL tapi membiarkan filter milik preset sebelumnya. Pola `key` yang sama sudah dipakai form record modul lain. |
| P6 | — (tidak direncanakan) | `ProyekStatus` + `on_hold` memaksa perbaikan `ProyekPage` | `STATUS_LABELS`/`STATUS_COLORS` di sana bertipe `Record<ProyekStatus, string>`; menambah satu nilai enum membuat keduanya gagal kompilasi. Ini justru bukti tipenya bekerja. |
| P7 | Fase 4 menambah kontrol `mode` | `mode` ternyata **tidak pernah** terekspos di UI sebelumnya | `BudgetAnalysisParams.mode` sudah ada di tipe dan didukung backend, tapi tidak ada kontrolnya — preset Variance tidak akan berfungsi tanpa itu. Ditambahkan sekalian. |
| P8 | `backend-directory-tree.md` diperbarui | **Tidak disentuh** | Dokumen itu hanya mendaftar direktori, dan rencana ini tidak menambah satu pun direktori backend. Memperbarui tanggalnya tanpa perubahan struktural hanya menambah noise. |

## Yang TIDAK dikerjakan di rencana ini

- ❌ Mesin agregasi baru — semua angka dari `BudgetAnalysisService`
- ❌ Tabel baru — tidak ada migration di rencana ini kecuali fase 1 (kolom form)
- ❌ Menutup G11 (dimensi bocor di Sales Return, Purchase, Stock, Fixed Asset).
      Itu milik `../New_Fitures/project-dimension-budgeting-readiness-plan.md`.
      Selama G11 terbuka, angka **Actual** proyek bisa lebih kecil dari kenyataan —
      peringatan ini wajib tetap tampil di UI.
- ❌ Export PDF/Excel per laporan anggaran — permission `budgets.export` sudah
      ada, implementasinya di luar cakupan
