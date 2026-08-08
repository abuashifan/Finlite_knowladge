# Mulai Di Sini — Orientasi Finlite ERP untuk AI Agent

> **Tujuan file ini:** membuat agent baru bisa bekerja tanpa memindai seluruh folder project.
> Baca berurutan `00` → `05`. Setelah itu Anda tahu di mana segala sesuatu berada dan
> aturan apa yang berlaku, tinggal membuka file yang benar-benar relevan dengan tugas.
>
> Disusun 2026-08-08 dengan membaca kode nyata, bukan dari ingatan. Angka-angka di sini
> hasil hitung, bukan perkiraan. Cara memverifikasi ulang ada di §7.

---

## 1. Produk

**Finlite ERP** (nama internal lama: *Seaside Escape ERP*) — aplikasi akuntansi &
operasional untuk UKM, **multi-perusahaan**, satu akun user bisa memegang banyak
perusahaan.

Cakupan modul: Master Data, Buku Besar/Jurnal, Kas & Bank, Penjualan, Pembelian,
Persediaan, Aset Tetap, Anggaran, Saldo Awal, Laporan, Pengaturan & Hak Akses.

## 2. Dua repo, satu produk

| | Backend | Frontend |
|---|---|---|
| Path | `/workspace/laravel_backend/` | `/workspace/frontend/` |
| Stack | PHP 8.3, Laravel 13, Sanctum | React 19, Vite, TypeScript |
| Bentuk | REST API **saja** (tanpa Blade untuk aplikasi) | SPA, terpisah penuh |
| Database | SQLite (central + satu file per tenant) | — |
| Autentikasi | Bearer token (Sanctum) | Token disimpan di localStorage |

Repo ketiga: `/workspace/Finlite_knowladge/` — knowledge base ini
(`plans/`, `reference/`, `reviews/`). Bukan kode.

> ⚠️ `CLAUDE.md` dan `AGENTS.md` frontend menyebut **React 18**. `package.json`
> sebenarnya **React 19.2** dan **Vite 8**. Percayai `package.json`.

## 3. Angka kunci (hasil hitung 2026-08-08)

**Backend**
- 18 modul di `app/Modules/`, 16 subsistem bersama di `app/Shared/`
- **429 endpoint API** — terbanyak: Sales 85, Purchase 72, MasterData 59, Inventory 38, Reports 35
- 77 tabel tenant, 27 tabel central
- 147 file test, 25 migrasi central + 87 migrasi tenant
- 240 permission, 8 role

**Frontend**
- 15 modul di `src/modules/`, **145 halaman**, 464 file TS/TSX
- 180 route (169 di modul + 11 di router utama) — terbanyak: Reports 42, Sales 31, Purchase 28
- 37 komponen bersama, 15 hook global, 4 store Zustand

## 4. Peta dokumen reference ini

| File | Isi | Baca kalau… |
|------|-----|-------------|
| `00-mulai-di-sini.md` | file ini — orientasi & angka kunci | selalu, pertama |
| `01-arsitektur.md` | multi-tenant, kontrak API, siklus dokumen, penomoran | menyentuh apa pun yang lintas modul |
| `02-backend.md` | modul, `app/Shared/`, konvensi service & test | mengubah backend |
| `03-frontend.md` | modul, router, shell tab, state, alur data | mengubah frontend |
| `04-komponen-reusable.md` | katalog 37 komponen bersama + kapan dipakai | membangun halaman/form/tabel |
| `05-role-permission-guard.md` | 8 role, 240 permission, guard rute & UI | apa pun yang menyangkut hak akses |

Mirror struktur direktori (dijaga sinkron, bukan sumber kebenaran):
`backend-directory-tree.md`, `struktur_frontend.md`.

## 5. Dokumen di luar reference yang wajib dibaca lebih dulu

Aturan project mewajibkan ini, dan **mengalahkan** apa pun di file reference:

1. `/workspace/CLAUDE.md` — aturan RTK (semua perintah shell diawali `rtk`)
2. `/workspace/frontend/CLAUDE.md` + `/workspace/frontend/AGENTS.md` — sebelum kerja frontend
3. `/workspace/laravel_backend/AGENTS.md` — sebelum kerja backend
4. `/workspace/Finlite_knowladge/plans/*/README.md` — riwayat keputusan besar

## 6. Aturan yang paling sering dilanggar agent baru

Diambil dari `CLAUDE.md`/`AGENTS.md` dan dari kesalahan nyata di sesi-sesi sebelumnya:

1. **`npx tsc --noEmit` TIDAK memeriksa apa pun di project ini.** Sudah dibuktikan
   dengan menyisipkan error tipe sengaja — lolos tanpa suara. Hanya
   **`npm run build`** (yang menjalankan `tsc -b` dengan project references) yang
   benar-benar mengetik-cek.
2. **Awali semua perintah shell dengan `rtk`**, termasuk di dalam rantai `&&`.
3. **Jangan pakai `any`** tanpa alasan tertulis; jangan fetch di komponen (pakai
   TanStack Query); jangan simpan data API di Zustand.
4. **Jangan render tombol aksi tanpa cek permission** — lihat `05-role-permission-guard.md`.
5. **Jangan edit `src/components/ui/`** (itu shadcn generated).
6. **Update `frontend/docs/struktur_frontend.md`** setiap menambah file frontend.
7. **Backend: logika bisnis di service, validasi di FormRequest, write wajib
   transaction-safe, perubahan schema wajib lewat migration.** Jangan sunting file
   SQLite langsung untuk data bisnis.
8. **Jalankan test tersempit yang relevan**, bukan seluruh suite. Suite penuh
   backend ±6 menit; pemilik produk pernah menolak itu untuk perubahan sempit.
   Contoh: `rtk php artisan test tests/Feature/MasterData`.
9. **grep membuktikan ketiadaan di kode, bukan ketiadaan di layar.** Pernah terjadi:
   grep bersih tapi teks lama tetap tampil karena ada salinan kedua sebagai prop.
   Untuk perubahan UI, verifikasi di browser.

## 7. Cara memverifikasi ulang angka di dokumen ini

Kalau ragu dokumen ini sudah basi, jalankan ini — semua angka di §3 berasal dari sini:

```bash
# backend
ls /workspace/laravel_backend/app/Modules/ | wc -l
for f in /workspace/laravel_backend/app/Modules/*/Routes/api.php; do \
  grep -cE "Route::(get|post|put|patch|delete)" $f; done | paste -sd+ | bc
find /workspace/laravel_backend/tests -name '*Test.php' | wc -l

# frontend
find /workspace/frontend/src/modules -name '*Page.tsx' | wc -l
find /workspace/frontend/src -name '*.ts' -o -name '*.tsx' | wc -l
```

## 8. Menjalankan aplikasi secara lokal

```bash
# backend  -> http://127.0.0.1:8000
cd /workspace/laravel_backend && rtk php artisan serve --host=127.0.0.1 --port=8000

# frontend -> http://localhost:5173  (Vite mem-proxy /api ke 127.0.0.1:8000)
cd /workspace/frontend && rtk npm run dev
```

Kredensial demo: `admin@example.com` / `password`. User ini memegang dua perusahaan
(`PT Maju Jaya` id 1, `PT Nusantara Dagang Sejahtera` id 2), jadi setelah login akan
muncul halaman pemilih perusahaan.

Deployment audit (dari `frontend/AGENTS.md`): <https://app.finlite.my.id/>, kredensial sama.

## 9. Perintah verifikasi wajib sebelum menyatakan selesai

| Perubahan | Perintah |
|---|---|
| Frontend | `rtk npm run build` (**wajib**), `rtk lint` |
| Backend | `rtk php artisan test tests/Feature/<Modul>`, `rtk vendor/bin/pint --test` |
| UI yang terlihat user | verifikasi di browser (Playwright tersedia di frontend) |
