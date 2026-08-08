# Reference — Pengetahuan Lengkap Finlite ERP

Folder ini dibuat supaya **agent AI mana pun bisa langsung bekerja tanpa memindai
seluruh folder project**. Baca `00` → `05` berurutan, lalu buka file kode yang benar-benar
relevan dengan tugas.

## Urutan baca

| File | Isi | Baca kalau… |
|------|-----|-------------|
| **[00-mulai-di-sini.md](00-mulai-di-sini.md)** | orientasi produk, angka kunci, aturan yang paling sering dilanggar, cara menjalankan & memverifikasi | **selalu, pertama** |
| **[01-arsitektur.md](01-arsitektur.md)** | multi-tenancy (satu DB per perusahaan), kontrak API, siklus hidup dokumen, penomoran, alur sesi | menyentuh apa pun yang lintas modul |
| **[02-backend.md](02-backend.md)** | 18 modul, 429 endpoint, `app/Shared/`, konvensi service & test, database | mengubah backend |
| **[03-frontend.md](03-frontend.md)** | 15 modul, 145 halaman, memory router, shell tab, state, alur data, form | mengubah frontend |
| **[04-komponen-reusable.md](04-komponen-reusable.md)** | katalog 37 komponen bersama + pola halaman daftar & form standar | membangun halaman/tabel/form |
| **[05-role-permission-guard.md](05-role-permission-guard.md)** | 8 role, 240 permission, resolusi override, guard rute & UI | apa pun yang menyangkut hak akses |

## Mirror peta direktori

Dua file berikut adalah **salinan**, bukan sumber kebenaran:

| File di sini | Sumber kebenaran |
|---|---|
| `backend-directory-tree.md` | `/workspace/laravel_backend/docs/backend-directory-tree.md` |
| `struktur_frontend.md` | `/workspace/frontend/docs/struktur_frontend.md` |

Menyalin ulang:

```bash
cd /workspace
cp laravel_backend/docs/backend-directory-tree.md Finlite_knowladge/reference/
cp frontend/docs/struktur_frontend.md             Finlite_knowladge/reference/
```

**Kapan menyalin ulang:**
- **Backend** — setiap ada direktori ditambah/dihapus/dipindah (modul baru, subfolder
  `Services/`, `Requests/Concerns/`, …).
- **Frontend** — setiap ada **file baru** (page/service/type/component/hook/schema).
  Ini sudah jadi hard rule frontend: "WAJIB update `docs/struktur_frontend.md` jika ada
  file baru". Update file kanonik dulu, baru salin ke sini.

## Batas berlaku dokumen ini

Ditulis **2026-08-08** dengan membaca kode nyata. Semua angka hasil hitung, dan perintah
untuk menghitung ulang ada di `00-mulai-di-sini.md` §7.

Kalau ada pertentangan, urutan otoritasnya:

1. **Kode** — selalu menang
2. `CLAUDE.md` / `AGENTS.md` di repo masing-masing — aturan kerja yang mengikat
3. `plans/*/README.md` — riwayat keputusan besar beserta alasannya
4. File reference ini — ringkasan; bisa basi

Sudah ada satu pertentangan yang diketahui: `CLAUDE.md` dan `AGENTS.md` frontend
menyebut **React 18**, sedangkan `package.json` menyatakan **React 19.2**. Percayai
`package.json`.

## Riwayat keputusan besar (di `../plans/`)

| Rencana | Status | Inti |
|---|---|---|
| `laravel-modularization/` | ✅ 2026-07-08 | backend jadi modular monolith (`app/Modules` + `app/Shared`) |
| `list-query-pushdown/` | ✅ 2026-08-07 | search/filter/sort/paginate 32 endpoint pindah ke SQL — 723 ms/20 MB → 17 ms/0 MB |
| `list-filters-frontend/` | ✅ 2026-08-08 | filter halaman daftar berlaku ke seluruh data, bukan 25 baris yang tampil |
| `company-session-layer/` | ✅ 2026-08-08 | Tutup Database vs Keluar, cache query ber-scope perusahaan |
| `reports-expansion/` | berjalan | mengisi ~91 laporan sesuai visi `design-I2` |
