# Fase 2 — Antrean

**Status: ⬜ Belum dikerjakan. Prasyarat untuk Fase 3–4.**

Impor transaksi tidak bisa sinkron. Ratusan faktur, masing-masing memicu posting
jurnal dan mutasi piutang/stok, akan menabrak `max_execution_time` PHP-FPM jauh
sebelum selesai.

Fase ini membangun **beban asinkron pertama** di aplikasi ini.

## Penguncian SQLite ⚠️ prasyarat, bukan penyempurnaan

Koneksi `tenant` di `config/database.php` **tidak menyebut `journal_mode` maupun
`busy_timeout`** — jadi ia memakai mode `DELETE` bawaan SQLite: penulis memblokir
pembaca, pembaca memblokir penulis, dan akses yang bentrok langsung mendapat
`SQLITE_BUSY` alih-alih menunggu.

Selama ini aman karena semua penulisan datang dari request web yang pendek.
Worker antrean mengubah itu: satu batch impor memegang kunci tulis sementara user
perusahaan yang sama sedang bekerja di browser. Hasilnya "database is locked" —
untuk user, atau untuk worker.

*(Catatan pembeda: `PRAGMA synchronous = OFF` dan `journal_mode = MEMORY` di
`TenantConnectionManager` baris 30–33 **hanya berjalan di environment testing**,
dijaga `app()->environment('testing')`. Produksi tidak menanggung risiko korupsi
itu — masalahnya justru sebaliknya, produksi tidak disetel sama sekali.)*

**Yang harus dikerjakan sebelum Fase 3:**

1. Nyalakan `PRAGMA journal_mode = WAL` untuk koneksi tenant di produksi. Dengan
   WAL, pembaca tidak lagi diblokir penulis — persis pola akses yang muncul saat
   impor berjalan.
2. Setel `busy_timeout` (usul: 5.000 ms) supaya bentrokan menunggu, bukan
   langsung gagal.
3. **Uji beban sebelum Fase 3 dinyalakan**: jalankan impor 1.000 baris sambil
   memakai aplikasi di perusahaan yang sama, dan pastikan tidak ada
   `database is locked`.

Draft-only sudah sangat meringankan beban tulis (tidak ada posting jurnal saat
impor), dan batas 1.000 baris plus satu batch aktif per perusahaan ikut
membatasi lama penguncian. Tapi ketiganya peredam, bukan pengganti WAL.

Kalau ternyata WAL tidak cukup pada beban nyata, itulah sinyal bahwa tenant perlu
pindah dari SQLite — keputusan arsitektur besar yang sebaiknya diambil dengan
data, bukan diantisipasi sekarang.

## Keadaan terverifikasi 2026-08-11

- **`app/Jobs/` tidak ada sama sekali.** Belum ada satu pun pekerjaan latar.
- Tabel antreannya **sudah ada** —
  `database/migrations/0001_01_01_000002_create_jobs_table.php`, di database
  **pusat**.
- `QUEUE_CONNECTION=database` sudah aktif di `.env`, tapi **tidak pernah
  dipakai**.
- **Tidak ada worker yang berjalan di server.**

Poin terakhir bukan urusan kode. Impor transaksi baru berfungsi kalau ada proses
`queue:work` yang hidup terus — lewat supervisor, systemd, atau apa pun yang
dipakai di server. Itu kebutuhan operasional baru untuk aplikasi ini, dan harus
disiapkan **sebelum** Fase 3 dinyalakan, bukan sesudah.

## Ranjau terbesar: koneksi tenant di dalam job

Ini bagian yang paling mudah salah, dan akibatnya paling buruk.

Di jalur HTTP biasa, `EnsureCompanyAccess` membaca header `X-Company-ID` lalu
mengikat koneksi `tenant` ke berkas SQLite perusahaan itu. **Job berjalan di luar
request** — tidak ada header, tidak ada middleware, jadi koneksi `tenant`
**tidak terikat ke apa pun**.

Kalau job menulis dalam keadaan itu, dua kemungkinan: gagal karena koneksi tidak
ada, atau — jauh lebih buruk — menulis ke koneksi tenant yang **tersisa dari job
sebelumnya**, yaitu ke database perusahaan lain.

Yang wajib dilakukan:

1. Job membawa `company_id` di payload-nya, bukan mengandalkan konteks.
2. Job **mengikat koneksi tenant sendiri** di awal `handle()`.
3. Job **memutus koneksi** di blok `finally`. `TenantMigrationService` sudah
   memakai pola ini (`connectionManager->disconnect()` di `finally`) — ikuti.
4. Test yang menjalankan dua job untuk dua perusahaan berbeda secara berurutan,
   lalu membuktikan data tidak tercampur. **Ini test terpenting di fase ini.**

Worker adalah proses yang hidup lama dan memproses job berturut-turut. Kebocoran
koneksi antar-job bukan kemungkinan teoretis — itu mode kegagalan bawaan kalau
tidak diurus.

## Bentuk job

Satu job **per batch**, bukan per baris.

Job per baris terdengar lebih tahan gagal, tapi menghasilkan ratusan job yang
masing-masing harus mengikat dan memutus koneksi tenant sendiri — mahal, dan
memperbesar permukaan ranjau di atas. Job per batch memproses barisnya dalam satu
koneksi, memperbarui `import_rows` sambil jalan.

```
ImportBatchJob
  ├─ ikat koneksi tenant (company_id dari payload)
  ├─ untuk tiap baris valid:
  │     ├─ panggil service dokumen
  │     ├─ tulis document_id / errors ke import_rows
  │     └─ perbarui pencacah di import_batches
  └─ finally: putus koneksi
```

## Progres

`import_batches` sudah punya `total_rows` / `committed_rows` / `failed_rows` dari
Fase 0. Job memperbaruinya berkala (misal tiap 25 baris, bukan tiap baris —
menulis 500 kali ke baris yang sama itu pemborosan).

Frontend melakukan polling ke `GET /imports/{uuid}` yang sudah ada. **Jangan**
tambah websocket; polling tiap beberapa detik sudah memadai untuk pekerjaan yang
selesai dalam hitungan menit.

## Job gagal

- `failed_jobs` sudah ada di migrasi bawaan.
- Batch yang job-nya gagal total → status `failed`, dengan pesan yang bisa dibaca
  client.
- **Jangan `retry` otomatis.** Job impor menulis dokumen keuangan; menjalankan
  ulang job yang setengah selesai menghasilkan dokumen ganda. `$tries = 1`, dan
  pengulangan dilakukan sadar oleh user setelah melihat baris mana yang gagal.

Ini alasan lain kenapa `external_ref` (Fase 0) penting: dengan kunci idempoten,
menjalankan ulang batch yang setengah selesai jadi aman.

## Test

- Job memproses batch dan mengisi `document_id` di tiap baris
- **Dua job untuk dua perusahaan berurutan → data tidak tercampur** ⚠️ terpenting
- Job gagal → batch `failed`, tidak ada dokumen setengah jadi yang menggantung
- `$tries = 1` — job tidak diulang otomatis
- Progres bertambah selama job berjalan

## Risiko

- **Kebocoran koneksi tenant antar-job** — lihat di atas. Ini risiko terbesar di
  seluruh rencana data-import, karena akibatnya adalah data perusahaan A masuk ke
  database perusahaan B, dan itu melanggar janji isolasi yang paling dasar.
- **Worker mati diam-diam.** Kalau tidak ada yang memantau, batch akan terlihat
  "sedang diproses" selamanya. Perlu batas waktu: batch yang `committing` lebih
  dari X menit ditandai `failed`.
