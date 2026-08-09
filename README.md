# Finlite Knowledge

Dokumentasi perencanaan dan knowledge base untuk project Finlite ERP.

## Struktur

```
Finlite_knowladge/
  reference/      ← Pengetahuan lengkap aplikasi — MULAI DI SINI
  plans/          ← Dokumen perencanaan implementasi + riwayat keputusan
  reviews/        ← Catatan review
```

## Reference — mulai di sini

**[reference/](reference/README.md)** berisi pengetahuan lengkap backend + frontend,
disusun supaya **agent AI baru tidak perlu memindai seluruh folder project**.

| File | Isi |
|---|---|
| `00-mulai-di-sini.md` | orientasi, angka kunci, aturan yang paling sering dilanggar, cara menjalankan |
| `01-arsitektur.md` | multi-tenancy (satu database per perusahaan), kontrak API, siklus dokumen |
| `02-backend.md` | 18 modul, 429 endpoint, `app/Shared/`, konvensi service & test |
| `03-frontend.md` | 15 modul, 145 halaman, memory router, shell tab, state, form |
| `04-komponen-reusable.md` | katalog 37 komponen bersama + pola halaman standar |
| `05-role-permission-guard.md` | 8 role, 240 permission, guard rute & UI |

Plus mirror peta direktori (`backend-directory-tree.md`, `struktur_frontend.md`) —
**mirror, bukan sumber kebenaran**; sumbernya di `laravel_backend/docs/` &
`frontend/docs/`. Aturan sinkronisasi ada di `reference/README.md`.

## Plans

- **[Laravel Modularization](plans/laravel-modularization/README.md)** — Rencana detail refactoring backend Laravel ke arsitektur modular (`app/Shared/` + `app/Modules/`), 9 fase (0–8), mapping file eksplisit per fase, dirancang untuk dieksekusi lintas sesi. ✅ SELESAI 2026-07-08. **Mulai dari `plans/laravel-modularization/README.md` (index + progress ledger).**
  - `plans/laravel-modularization-plan.md` — versi ringkas lama (deprecated, digantikan folder di atas).
- **[List Query Pushdown](plans/list-query-pushdown/README.md)** — Memindahkan search/filter/sort/paginate dari memori PHP ke query builder untuk **32 endpoint daftar**. ✅ SELESAI 2026-08-07, 8 fase (0–7). Sebelumnya tiap request daftar menghidrasi seluruh tabel lalu memotong satu halaman di PHP; pada 3000 jurnal itu 723 ms dan 20 MB **untuk setiap permintaan**, termasuk yang cuma minta satu halaman. Sesudahnya satu halaman 25 baris berbiaya 17 ms dan 0 MB tambahan — ~42× lebih cepat, dan memorinya tidak lagi tumbuh mengikuti besar tabel. Ikut memperbaiki empat bug filter yang ditemukan di jalan (`customer_id`/`vendor_id` diabaikan, pencarian relasi tidak pernah jalan, filter status void, status comma-separated). **Lanjutannya:** [List Filters Frontend](plans/list-filters-frontend/README.md). **Mulai dari `plans/list-query-pushdown/README.md`.**
- **[List Filters Frontend](plans/list-filters-frontend/README.md)** — Membuat filter halaman daftar berlaku ke **seluruh data**, bukan hanya 25 baris yang sedang tampil. Lanjutan langsung dari List Query Pushdown: backend sudah menerima `status`/`date_from`/`date_to`, frontend belum mengirimnya. Audit 2026-08-07 memetakan 22 halaman jadi tiga kelompok — 5 sudah benar, 8 belum punya UI filter tanggal, dan **9 menyaring di browser** sehingga mencentang "Posted" tidak menampilkan dokumen posted di halaman lain. ✅ SELESAI 2026-08-08, 5 fase (0–4), murni frontend, tanpa perubahan backend. Fase 4 menyeragamkan fitur **Aktif/Nonaktif** di 9 halaman master data ke format `KontakListPage` — audit menemukan sembilan bentuk berbeda, dan Produk bahkan tidak bisa mengubah status sama sekali dari daftar. Ikut membawa temuan lain: `CoaListPage` diam-diam membatasi diri ke 100 akun tanpa UI paginasi. **Mulai dari `plans/list-filters-frontend/README.md`.**
- **[Budget Module](plans/budget-module/README.md)** — Menghidupkan modul anggaran yang sudah ada, bukan membangunnya dari nol. Backend lengkap dan teruji (16 endpoint, `BudgetFlowTest` 6 lulus), dan peringatan over-budget di form jurnal sudah berfungsi — tapi frontend-nya tidak pernah dijalankan dengan data nyata. Empat cacat terverifikasi: `budgetApi` satu-satunya service yang meng-unwrap respons dua kali sehingga **seluruh layar anggaran selalu kosong**; modul tidak punya entri menu sama sekali sehingga tidak bisa dijangkau user; tombol "Ajukan Anggaran" menuju rute yang tidak ada; dan catatan penolakan tidak pernah tampil karena frontend menunggu status `rejected` yang tidak pernah ditulis backend. ✅ SELESAI 2026-08-09, 4 fase (0–3), hampir seluruhnya frontend — satu-satunya perubahan backend adalah melebarkan permission tolak jadi `budgets.approve_head|budgets.approve_finance`, dikunci test baru yang terbukti gagal tanpa perbaikannya. **Keputusan terbuka:** scoping "dept hanya melihat pengajuan sendiri" (gap-12 §5) tidak bisa dikerjakan — tidak ada kolom yang menghubungkan user ke departemen. **Belum diverifikasi manual di browser** (backend tidak berjalan saat pengerjaan). **Mulai dari `plans/budget-module/README.md`.**
- **[Reports Expansion](plans/reports-expansion/README.md)** — Implementasi visi laporan `design-I2` (nav shell sudah ada; mengisi ~91 laporan yang belum ada sesuai Prioritas A→B→C), 14 fase (0–13) dengan fase backend disertakan, dirancang untuk dieksekusi lintas sesi per fase. **Mulai dari `plans/reports-expansion/README.md` (index + progress ledger), lalu `00-conventions.md`.**
