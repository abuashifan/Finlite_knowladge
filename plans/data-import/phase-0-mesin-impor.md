# Fase 0 — Mesin Impor

**Status: ✅ Selesai backend awal — 2026-08-11.**

Implementasi backend ada di `/workspace/laravel_backend/app/Modules/Imports`.
Fase ini menambahkan endpoint upload, pembacaan CSV/XLSX, penyimpanan batch tenant,
pemetaan kolom, validasi per baris, preview berhalaman, template CSV, dan pembatalan
batch. Endpoint `commit` sudah tersedia sebagai stub aman dan belum menulis dokumen.

Membangun kerangka yang dipakai ulang oleh **semua** profil impor: unggah berkas,
baca `.xlsx`/CSV, petakan kolom, validasi, tampilkan pratinjau. Fase ini
**belum menulis dokumen apa pun** — ia berhenti tepat sebelum commit.

Memisahkannya begini disengaja. Kalau mesin dan profil pertama dibangun
sekaligus, setiap kegagalan jadi ambigu: pembacaan berkasnya salah, atau
pemetaan ke dokumennya?

## Alur

```
unggah  →  baca header  →  petakan kolom  →  validasi per baris  →  pratinjau  →  commit
                                                                        ▲          │
                                                                        └──────────┘
                                                                    Fase 1 ke atas
```

## Pilihan pustaka

`.xlsx` dan CSV keduanya wajib, dan tidak ada pustaka apa pun terpasang hari ini.

**Rekomendasi: `phpoffice/phpspreadsheet` langsung**, bukan `maatwebsite/excel`.

Alasannya: `maatwebsite/excel` adalah pembungkus yang mengandaikan pola
"satu kelas import per entitas" dengan Eloquent di dalamnya — bertabrakan dengan
aturan bahwa importer wajib lewat service dokumen, bukan menulis model. Memakai
PhpSpreadsheet langsung berarti pembacaan berkas dan penulisan dokumen tetap
terpisah bersih.

CSV dibaca lewat `fgetcsv` bawaan PHP, bukan PhpSpreadsheet — lebih ringan dan
mendukung pembacaan bertahap sejak awal. Jadi ada dua pembaca di belakang satu
antarmuka:

```php
interface SpreadsheetReader
{
    public function headers(string $path): array;
    public function rows(string $path): Generator;   // Generator, bukan array
}
```

`Generator` bukan `array` sejak awal: begitu ada client yang mengunggah 5.000
baris, mengubah kontraknya belakangan berarti menyentuh setiap profil.

## Penyimpanan berkas

`FILESYSTEM_DISK=local`, dan belum ada pola penyimpanan unggahan.

Berkas disimpan di bawah lintasan **per perusahaan**:
`imports/{company_id}/{batch_uuid}.{ext}`.

Ini bagian dari isolasi tenant — berkas impor perusahaan A memuat data keuangan
A, jadi ia tidak boleh berada di lintasan yang bisa ditebak lintas perusahaan.
Nama berkas asli **tidak** dipakai sebagai nama simpan; ia hanya dicatat di
kolom.

Berkas dihapus setelah batch selesai dan lewat masa simpan yang ditetapkan
(usul: 30 hari, supaya masih bisa ditelusuri saat rekonsiliasi).

## Tabel

Keduanya di **database tenant**, bukan pusat — isinya data perusahaan.

**`import_batches`**

| Kolom | Catatan |
|---|---|
| `id`, `uuid` | |
| `profile` | `sales_invoice`, `vendor_bill`, `journal_entry`, `contact`, … |
| `original_filename`, `stored_path`, `file_hash` | `file_hash` untuk mendeteksi unggahan berulang |
| `column_map` (JSON) | hasil pemetaan kolom |
| `status` | `draft` → `validating` → `previewed` → `committing` → `completed` / `failed` |
| `total_rows`, `valid_rows`, `failed_rows`, `committed_rows` | |
| `created_by`, timestamps | |

**`import_rows`**

| Kolom | Catatan |
|---|---|
| `import_batch_id`, `row_number` | |
| `raw` (JSON) | isi baris apa adanya, untuk ditampilkan di pratinjau |
| `normalized` (JSON) | hasil pemetaan + penormalan |
| `status` | `pending` / `valid` / `invalid` / `committed` / `failed` |
| `errors` (JSON) | daftar galat per kolom |
| `document_id`, `document_type` | diisi setelah commit — jejak balik ke dokumen |
| `external_ref` | kunci idempoten, lihat di bawah |

`document_id` bukan hiasan: tanpa jejak balik, satu batch salah berarti mencari
ratusan dokumen secara manual untuk di-void.

## Idempotensi — aturan yang ditetapkan

Berkas sama terunggah dua kali = dokumen ganda. Draft-only sudah meredam
akibatnya (draft ganda tinggal dihapus, tidak ada jurnal yang terbentuk), tapi
tetap membuang waktu user untuk memilah mana yang asli.

Aturannya, ditetapkan di sini karena pemilik produk menyerahkannya:

**Kolom `Ref` wajib ada di setiap templat transaksi, dan wajib diisi.**

- Isinya **nomor dokumen dari sistem asal** kalau berkasnya diekspor dari sistem
  lain. Ini yang paling bersih dan paling sering tersedia.
- Kalau berkas dirakit manual, pakai pola `{JENIS}-{YYYYMMDD}-{urut}` —
  misal `INV-20260811-001`. Templat memuat contohnya di baris pertama.
- Ia sekaligus jadi **kolom pengelompokan**: beberapa baris berkas dengan `Ref`
  sama membentuk satu dokumen bermultibaris.

Dua peran itu digabung dengan sengaja. Satu kolom yang harus diisi, bukan dua —
dan karena pengelompokan sudah menuntutnya, idempotensi jadi gratis.

**Penegakan:** baris yang `Ref`-nya sudah pernah dipakai di batch lain ditandai
`invalid` di pratinjau, dengan pesan yang menyebut batch dan tanggal pemakaian
sebelumnya — bukan sekadar "duplikat".

Catatan implementasi 2026-08-11: karena `Ref` juga menjadi kolom pengelompokan
dokumen bermultibaris, unique index langsung `(profile, external_ref)` di
`import_rows` akan memblokir baris kedua dari dokumen yang sama. Untuk Fase 0,
database memakai index pencarian `(profile, external_ref)` dan idempotensi lintas
batch ditegakkan di service validasi. Fase commit boleh memperketat ini di level
dokumen/group bila sudah ada bentuk dokumen impor final.

**Lapis kedua, lunak:** `file_hash` memberi peringatan "berkas ini sudah pernah
diunggah tanggal …, lanjutkan?". Menahan kecelakaan paling umum sebelum user
menunggu validasi selesai.

### Yang masih perlu diperiksa

Apakah `Ref` boleh dipakai ulang setelah batch-nya dihapus? Menurutku **boleh** —
kalau draft-nya sudah dihapus, tidak ada dokumen yang bertabrakan. Berarti unique
index-nya perlu mengabaikan baris milik batch yang dibatalkan, atau baris itu
ikut terhapus saat batch dibatalkan. Yang kedua lebih sederhana.

## Pemetaan kolom

Header berkas jarang cocok persis dengan nama field. Dua jalur:

- **Templat unduhan per profil.** Header sudah benar, pemetaan otomatis.
  Ini jalur yang dipakai 90% waktu dan harus ada sejak Fase 1.
- **Pemetaan manual** di layar, disimpan di `column_map`. Untuk berkas yang
  datang dari sistem lain.

Pemetaan yang sudah dipakai sebaiknya bisa disimpan ulang per profil, supaya
impor harian tidak mengulang langkah yang sama tiap hari. (Boleh ditunda ke
fase berikutnya kalau menambah cakupan terlalu banyak.)

## Validasi & pratinjau

Validasi berjalan **sebelum** apa pun tertulis, dan hasilnya per baris, bukan
per berkas. Layar pratinjau menampilkan:

- ringkasan: berapa baris valid, berapa gagal
- tabel baris bergalat dengan pesan per kolom
- tombol commit yang **nonaktif** kalau tidak ada satu pun baris valid

Untuk data harian, satu kolom salah bisa jadi ratusan jurnal salah yang harus
di-void satu per satu. Pratinjau bukan kenyamanan — ia yang membuat fitur ini
aman dipakai setiap hari.

## Endpoint

Semua di bawah `auth:sanctum` + `company.access`, dengan izin dari Fase 5:

```
POST   /imports                     unggah berkas → batch draft + daftar header
PATCH  /imports/{uuid}/mapping      simpan pemetaan kolom → jalankan validasi
GET    /imports/{uuid}              status + ringkasan
GET    /imports/{uuid}/rows         baris + galat (berhalaman)
POST   /imports/{uuid}/commit       eksekusi (sinkron di Fase 1, antrean sejak Fase 3)
DELETE /imports/{uuid}              batalkan batch + hapus berkas
GET    /imports/templates/{profile} unduh templat
```

## Batas ukuran & kesertaan

Ditetapkan pemilik produk 2026-08-11:

- **1.000 baris per berkas.** Melebihi itu ditolak di unggahan dengan pesan yang
  menyebut jumlah baris yang terbaca, bukan galat memori.
- **Satu batch aktif per perusahaan.** Unggahan kedua ditolak selama masih ada
  batch berstatus `validating` / `previewed` / `committing`. Selain mencegah
  kebingungan, ini ikut meredam penguncian SQLite
  ([Fase 2](phase-2-antrean.md#penguncian-sqlite)).

Batas 1.000 baris membuat pembacaan sekaligus aman di memori — tapi kontrak
`SpreadsheetReader` tetap memakai `Generator`, supaya menaikkan batas nanti tidak
menyentuh setiap profil.

## Test

- Baca `.xlsx` dan CSV, hasil headernya sama
- Berkas rusak / kosong / hanya header → galat yang bisa dibaca, bukan exception
- Pemetaan kolom tersimpan dan dipakai ulang
- Validasi menandai baris, bukan menggagalkan seluruh berkas
- `file_hash` sama → peringatan muncul
- Berkas tersimpan di lintasan per perusahaan; perusahaan lain tidak bisa
  mengambil batch milik perusahaan A (uji dengan `X-Company-ID` berbeda)
- Batch dibatalkan → berkas benar-benar terhapus dari disk

## Risiko

- **Kebocoran lintas tenant lewat berkas.** Ini satu-satunya bagian aplikasi yang
  menyimpan data keuangan **di luar** database tenant. Lintasan per perusahaan
  dan pemeriksaan kepemilikan batch wajib punya test sendiri.
- **Memori.** PhpSpreadsheet memuat seluruh berkas `.xlsx` ke memori. Batas
  ukuran bukan penyempurnaan.
