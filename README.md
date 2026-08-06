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
- **[List Query Pushdown](plans/list-query-pushdown/README.md)** — Memindahkan search/filter/sort/paginate dari memori PHP ke query builder untuk **32 endpoint daftar**. Saat ini tiap request daftar memuat seluruh tabel ke memori lalu memotong satu halaman; terukur bahwa minta 1 baris tidak lebih murah daripada minta semuanya. 8 fase (0–7), bertahap per modul dengan `listResponse` menerima dua bentuk selama transisi. ⚠️ **Butuh persetujuan pemilik produk** atas daftar kolom pencarian (`00-conventions.md` §4) sebelum Fase 1 — cakupan pencarian akan berubah dan itu terlihat pengguna. **Mulai dari `plans/list-query-pushdown/README.md`.**
- **[Reports Expansion](plans/reports-expansion/README.md)** — Implementasi visi laporan `design-I2` (nav shell sudah ada; mengisi ~91 laporan yang belum ada sesuai Prioritas A→B→C), 14 fase (0–13) dengan fase backend disertakan, dirancang untuk dieksekusi lintas sesi per fase. **Mulai dari `plans/reports-expansion/README.md` (index + progress ledger), lalu `00-conventions.md`.**
