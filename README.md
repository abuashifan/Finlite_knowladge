# Finlite Knowledge

Dokumentasi perencanaan dan knowledge base untuk project Finlite ERP.

## Struktur

```
Finlite_Knowladge/
  plans/          ← Dokumen perencanaan implementasi
  reference/      ← Peta direktori backend & frontend (mirror; jaga sinkron)
  architecture/   ← (future) Diagram dan keputusan arsitektur
  decisions/      ← (future) Architecture Decision Records (ADR)
```

## Reference

- **[reference/](reference/README.md)** — Salinan peta direktori (`backend-directory-tree.md`, `struktur_frontend.md`) supaya agent bisa menavigasi struktur project dari knowledge base. **Mirror, bukan sumber kebenaran** — sumber ada di `laravel_backend/docs/` & `react_frontend/docs/`. Lihat `reference/README.md` untuk aturan sinkronisasi.

## Plans

- **[Laravel Modularization](plans/laravel-modularization/README.md)** — Rencana detail refactoring backend Laravel ke arsitektur modular (`app/Shared/` + `app/Modules/`), 9 fase (0–8), mapping file eksplisit per fase, dirancang untuk dieksekusi lintas sesi. ✅ SELESAI 2026-07-08. **Mulai dari `plans/laravel-modularization/README.md` (index + progress ledger).**
  - `plans/laravel-modularization-plan.md` — versi ringkas lama (deprecated, digantikan folder di atas).
- **[List Query Pushdown](plans/list-query-pushdown/README.md)** — Memindahkan search/filter/sort/paginate dari memori PHP ke query builder untuk **32 endpoint daftar**. ✅ SELESAI 2026-08-07, 8 fase (0–7). Sebelumnya tiap request daftar menghidrasi seluruh tabel lalu memotong satu halaman di PHP; pada 3000 jurnal itu 723 ms dan 20 MB **untuk setiap permintaan**, termasuk yang cuma minta satu halaman. Sesudahnya satu halaman 25 baris berbiaya 17 ms dan 0 MB tambahan — ~42× lebih cepat, dan memorinya tidak lagi tumbuh mengikuti besar tabel. Ikut memperbaiki empat bug filter yang ditemukan di jalan (`customer_id`/`vendor_id` diabaikan, pencarian relasi tidak pernah jalan, filter status void, status comma-separated). **Lanjutannya:** [List Filters Frontend](plans/list-filters-frontend/README.md). **Mulai dari `plans/list-query-pushdown/README.md`.**
- **[List Filters Frontend](plans/list-filters-frontend/README.md)** — Membuat filter halaman daftar berlaku ke **seluruh data**, bukan hanya 25 baris yang sedang tampil. Lanjutan langsung dari List Query Pushdown: backend sudah menerima `status`/`date_from`/`date_to`, frontend belum mengirimnya. Audit 2026-08-07 memetakan 22 halaman jadi tiga kelompok — 5 sudah benar, 8 belum punya UI filter tanggal, dan **9 menyaring di browser** sehingga mencentang "Posted" tidak menampilkan dokumen posted di halaman lain. 4 fase (0–3), murni frontend, tanpa perubahan backend. Ikut membawa temuan lain: `CoaListPage` diam-diam membatasi diri ke 100 akun tanpa UI paginasi. **Mulai dari `plans/list-filters-frontend/README.md`.**
- **[Reports Expansion](plans/reports-expansion/README.md)** — Implementasi visi laporan `design-I2` (nav shell sudah ada; mengisi ~91 laporan yang belum ada sesuai Prioritas A→B→C), 14 fase (0–13) dengan fase backend disertakan, dirancang untuk dieksekusi lintas sesi per fase. **Mulai dari `plans/reports-expansion/README.md` (index + progress ledger), lalu `00-conventions.md`.**
