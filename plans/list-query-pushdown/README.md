# List Query Pushdown — Index & Progress Ledger

> **Agent: baca file ini PERTAMA setiap sesi.** Ia menentukan fase mana yang sedang berjalan.
>
> Rencana ini memindahkan **search / filter / sort / paginate** dari memori PHP
> ke query builder untuk **32 endpoint daftar**. Saat ini setiap request daftar
> memuat **seluruh tabel** ke memori, menyaring & mengurutkannya di sana, baru
> memotong satu halaman untuk dikirim.

## Masalah yang diselesaikan

`ApiResponse::listResponse()` (`app/Shared/Api/ApiResponse.php`) menerima
`Collection` yang sudah berisi **semua** baris, lalu:

1. `applyListSearch` — memindai **setiap field skalar** tiap record (`toArray()`)
2. `applyListStatus`, `applyListDateRange`, `applyListSort` — semuanya in-memory
3. `$collection->slice(...)` — baru di sini halaman dipotong

Service-nya memang mengembalikan semua baris, mis.
`SalesInvoiceService::list()` → `$query->orderByDesc('invoice_date')->orderByDesc('id')->get()`
lengkap dengan `with('customer', 'paymentTerm')`.

**Bukti terukur** (33 jurnal, 2026-08-06):

| Permintaan | Waktu | Baris dikirim |
|---|---|---|
| `per_page=1` | 0,052 dtk | 1 |
| `per_page=25` | 0,044 dtk | 25 |
| tanpa paginasi | 0,041 dtk | 33 |

Minta 1 baris **tidak lebih murah** daripada minta semuanya — server melakukan
kerja identik apa pun yang diminta. Inilah tanda paginasi tidak terjadi di SQL.

**Dampak saat data tumbuh:** biaya sebenarnya bukan JSON, melainkan hidrasi
model Eloquent + relasi eager-loaded (±10× ukuran JSON di memori), **per request**.
Gejala akhirnya bukan "lambat" melainkan `Allowed memory size exhausted` → 500.

**Di luar scope:** endpoint `/{resource}/adjacent` (navigasi Prev/Next form) tidak
lewat `listResponse` — sudah `LIMIT 1` sejak commit `57fc710`. Tidak perlu disentuh.

## Cara pakai (alur tiap sesi)

1. Baca **`README.md`** ini → temukan fase pertama yang `⬜ Belum` di ledger.
2. Baca **`00-conventions.md`** → pola trait, kontrak `listResponse` dua-bentuk,
   aturan kolom pencarian, definition-of-done, perintah verifikasi. **Wajib.**
3. Buka **`phase-N-*.md`** untuk fase itu.
4. Jalankan bagian **Prasyarat** di file fase.
5. Kerjakan daftar tugas eksplisit di file fase.
6. Jalankan **Checklist Verifikasi** fase.
7. Commit sesuai **Git Checkpoint** fase.
8. **Update ledger di bawah** lalu commit README. **Ini wajib** — inilah memori lintas sesi.

## Progress Ledger

| Fase | Judul | File | Endpoint | Status | Commit |
|------|-------|------|----------|--------|--------|
| 0 | Fondasi: trait + kontrak dua-bentuk + index tanggal | `phase-0-foundation.md` | — | ⬜ Belum | — |
| 1 | Pilot: Jurnal Umum | `phase-1-journal.md` | 1 | ⬜ Belum | — |
| 2 | Sales | `phase-2-sales.md` | 8 | ⬜ Belum | — |
| 3 | Purchase | `phase-3-purchase.md` | 7 | ⬜ Belum | — |
| 4 | Kas & Bank | `phase-4-cash-bank.md` | 4 | ⬜ Belum | — |
| 5 | Persediaan | `phase-5-inventory.md` | 3 | ⬜ Belum | — |
| 6 | Master Data | `phase-6-master-data.md` | 9 | ⬜ Belum | — |
| 7 | Pembersihan: buang jalur in-memory | `phase-7-cleanup.md` | — | ⬜ Belum | — |

> Status yang boleh: `⬜ Belum`, `🔄 Berjalan`, `✅ Selesai`.
> Kalau `🔄 Berjalan` tertinggal dari sesi sebelumnya, jalankan Prasyarat fase itu
> untuk menentukan seberapa jauh sudah dikerjakan sebelum melanjutkan.

## Prinsip desain

- **Non-blocking / bertahap.** `listResponse` menerima **dua bentuk** selama transisi:
  `Collection` (lama, in-memory) dan `LengthAwarePaginator` (baru, SQL). Modul bisa
  dipindah satu per satu; aplikasi tetap hijau di antara fase.
- **Kontrak API tidak berubah.** Bentuk response (`data`, `current_page`, `per_page`,
  `total`, `last_page`, `from`, `to`) wajib identik byte-per-byte dengan sekarang.
  Frontend tidak boleh perlu diubah sama sekali. Ini guardrail utama fase 1–6.
- **Satu trait, bukan 32 salinan.** Logika filter tinggal di
  `app/Shared/Api/AppliesListQuery.php`; tiap service hanya mendeklarasikan
  kolom mana yang boleh dicari, kolom tanggal, dan kolom sort default.
  Mengikuti pola `ResolvesAdjacentRecords` (commit `57fc710`).
- **Pilot dulu.** Fase 1 menyentuh **satu** modul supaya perubahan perilaku
  pencarian bisa dinilai user sebelum 31 endpoint sisanya ikut.
- **Tidak ada `LIMIT` diam-diam.** Daftar yang terpotong tanpa pemberitahuan lebih
  berbahaya daripada daftar yang lambat di sistem akuntansi. Paginasi harus jujur
  (`total` benar), bukan pemotongan senyap.

## ⚠️ Keputusan produk yang dibutuhkan sebelum Fase 1

**Cakupan pencarian akan berubah, dan ini terlihat oleh pengguna.**

Sekarang kotak pencarian mencocokkan **setiap field** tiap record — termasuk id,
`metadata`, alamat, catatan, dan semua tanggal. Mengetik `2026` bisa memunculkan
dokumen yang tidak dimaksud karena angka itu ada di kolom tanggal.

Setelah pushdown, tiap modul harus menyebut kolom mana yang dicari. Hasilnya lebih
tepat, tapi siapa pun yang terbiasa mencari lewat kolom di luar daftar akan merasa
fiturnya hilang.

**Usulan daftar kolom ada di `00-conventions.md` §4 dan harus disetujui pemilik
produk sebelum Fase 1 dieksekusi.** Agent tidak boleh menebak sendiri.

## Referensi

- Kode saat ini: `app/Shared/Api/ApiResponse.php` (`listResponse` + 5 helper privat)
- Pola trait yang ditiru: `app/Shared/Api/ResolvesAdjacentRecords.php`
- Aturan backend: `/workspace/laravel_backend/AGENTS.md`
- Peta modul: `Finlite_knowladge/reference/backend-directory-tree.md`
