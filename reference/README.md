# Reference — Peta Direktori (Mirror)

Folder ini menyimpan **salinan peta direktori** backend & frontend agar agent yang bekerja dari knowledge base `Finlite_Knowladge` bisa membaca struktur project tanpa membuka repo kode. **Ini mirror, bukan sumber kebenaran.**

| File di sini | Sumber kebenaran (kanonik) | Isi |
|---|---|---|
| `backend-directory-tree.md` | `laravel_backend/docs/backend-directory-tree.md` | Peta direktori backend Laravel (struktur modular DDD: `app/Modules/*` + `app/Shared/*`) |
| `struktur_frontend.md` | `react_frontend/docs/struktur_frontend.md` | Peta file frontend React (`src/modules/*`, `components/`, dll) |

## ⚠️ WAJIB: jaga file ini tetap sinkron

Kedua file ini **mudah basi**. Bila dibiarkan basi, agent akan mencari file di lokasi yang salah. Aturan:

1. **Sumber kebenaran ada di repo kode**, bukan di sini. Edit file kanonik dulu (kolom "Sumber kebenaran" di atas), lalu **salin ulang** ke folder ini:
   ```bash
   cd /home/tiny/Desktop/finlite
   cp laravel_backend/docs/backend-directory-tree.md   Finlite_Knowladge/reference/backend-directory-tree.md
   cp react_frontend/docs/struktur_frontend.md          Finlite_Knowladge/reference/struktur_frontend.md
   ```
   Setelah menyalin, pertahankan (atau perbarui tanggal) banner `MIRROR` di baris atas tiap file.

2. **Kapan meng-update:**
   - **Backend** (`backend-directory-tree.md`): setiap kali ada **direktori** backend yang ditambah/dihapus/dipindah (modul baru, subfolder `Services/`/`Requests/Concerns/`, dll). Ini bagian dari Definition of Done task backend yang mengubah struktur folder. Cara regenerasi ada di dalam file itu (§"WAJIB: jaga file ini tetap terbaru").
   - **Frontend** (`struktur_frontend.md`): setiap kali ada **file baru** (page/service/type/component/hook/schema) — ini sudah jadi hard rule frontend (`react_frontend/AGENTS.md` §10B & `CLAUDE.md`: "WAJIB update docs/struktur_frontend.md jika ada file baru"). Update file kanonik, lalu salin ke sini.

3. **Bila membaca file ini dan ragu apakah sudah basi**, verifikasi cepat terhadap repo (mis. `ls laravel_backend/app/Modules` atau cek beberapa path di `react_frontend/src/modules`) sebelum mengandalkannya. Cek juga tanggal "Terakhir disinkronkan" di banner tiap file.

## Catatan untuk plan reports-expansion

Rencana `plans/reports-expansion/` menambah banyak file baru di `react_frontend/src/modules/reports/` dan `laravel_backend/app/Modules/Reports/`. **Tiap fase** yang membuat file/direktori baru wajib:
- update `struktur_frontend.md` (kanonik) — sudah tercantum di "Peta File" tiap fase, dan
- (bila menambah **direktori** backend, mis. `Services/Sales/`, `Requests/Tax/`) update `backend-directory-tree.md` (kanonik),
lalu **salin ulang keduanya ke `reference/` ini**. Tambahkan langkah salin-ulang ini ke checklist "Git Checkpoint" fase saat mengeksekusi.
