# 12 — Finlite Gudang, Fase 0: panduan wawancara, keputusan, dan spesifikasi awal Fase 1

> **STATUS:** Fase 0 dimulai 15 November 2026. Fondasi platform di backend selesai
> (laravel_backend#30). Dokumen ini berisi bahan yang dibutuhkan untuk menutup Fase 0:
> panduan wawancara, daftar keputusan, dan **draf** spesifikasi Fase 1 untuk disahkan
> setelah wawancara. Konteks: [10](10-finlite-gudang-riset-kebutuhan-dan-fitur.md) dan
> [11](11-finlite-gudang-rencana-fase.md).

## 1. Status Fase 0

| Pekerjaan | Status |
| --- | --- |
| Produk `gudang` di platform: tenant sendiri, paket Gudang dan Gudang Gratis, izin `gudang.*`, aktivasi, bootstrap, admin perpanjang/buka kunci | Selesai di backend (draf PR, menunggu CI) |
| Wawancara 5-8 gudang | **Menunggu pemilik**: siapa yang diwawancara |
| Keputusan terbuka (bagian 3) | **Menunggu pemilik**; usulan bawaan dipakai sementara |
| Draf spesifikasi Fase 1 (bagian 4) | Draf siap, disahkan setelah wawancara |
| Aplikasi frontend Gudang (repositori baru) | **Perlu repositori baru milik pemilik** (lihat bagian 5) |
| Pendaftaran mandiri dan masa coba Gudang | Ditunda ke awal Fase 1; sementara paket diberikan admin |

## 2. Panduan wawancara gudang (30-45 menit)

**Sebelum:** minta izin merekam/mencatat; katakan bahwa ini untuk memahami cara kerja,
bukan menjual. Jangan memperlihatkan solusi dulu. Jangan minta data sensitif (harga
beli, nama pelanggan) tanpa persetujuan; catatan wawancara disimpan **di luar
repositori ini** atau dianonimkan.

**Bagian A: profil (5 menit)**
1. Apa yang disimpan di gudang ini, dan siapa yang membelinya?
2. Berapa jumlah jenis barang (SKU)? Berapa lokasi/rak? Berapa orang bekerja?
3. Berapa kali barang masuk dan keluar per hari? Hari tersibuk?
4. Ada berapa gudang atau toko yang saling kirim barang?

**Bagian B: alur hari ini (15 menit)** (minta ditunjukkan, bukan diceritakan)
5. Ceritakan **satu barang masuk** dari truk sampai tersimpan. Siapa yang menghitung, mencatat, memberi tempat?
6. Ceritakan **satu barang keluar** dari permintaan sampai berangkat. Siapa yang mengambil, mengecek, membuat surat jalan?
7. Bagaimana mencari barang di gudang? Berapa lama rata-rata? Siapa yang hafal letaknya?
8. Bagaimana kiriman ke gudang atau toko lain dicatat? Apa yang terjadi kalau jumlah tiba berbeda?
9. Barang rusak, retur, dan barang tidak laku diurus bagaimana?
10. Apakah ada barang yang punya tanggal kedaluwarsa atau nomor batch? Apa yang terjadi kalau terlewat?

**Bagian C: kendali (10 menit)**
11. Kapan terakhir stok opname? Berapa lama, siapa yang terlibat, apakah gudang berhenti?
12. Berapa selisih terakhir, dan bagaimana diselesaikan? Siapa yang menyetujui koreksi?
13. Pernahkah stok di sistem dan di rak berbeda sampai merugikan? Ceritakan satu kejadian.
14. Siapa yang boleh mengubah angka stok?

**Bagian D: alat dan sistem (5 menit)**
15. Pencatatan sekarang pakai apa (kertas, Excel, program)? Apa yang paling dikeluhkan?
16. Perangkat apa yang ada: HP (Android/iPhone), laptop, pemindai? Apakah barang sudah berbarcode?
17. Sinyal internet di dalam gudang bagaimana? Pernah putus sampai pekerjaan berhenti?
18. Terhubung ke akuntansi atau kasir? Programnya apa?

**Bagian E: nilai (5 menit)**
19. Kalau satu masalah selesai besok, mana yang paling berarti?
20. Berapa yang wajar dibayar per bulan untuk alat seperti ini? Siapa yang memutuskan membeli?

**Sesudah:** foto (izinkan dulu) form dan dokumen yang dipakai; minta contoh data barang
(tanpa harga bila sensitif); catat tiga kutipan langsung yang paling menggambarkan masalah.

**Lembar rekap per gudang** (isi segera setelah wawancara):

| Isian | Jawaban |
| --- | --- |
| Kode gudang (anonim), jenis usaha | |
| SKU / lokasi / orang / transaksi per hari | |
| Ada batch atau kedaluwarsa? Barang apa | |
| Dokumen yang dipakai dan penomorannya | |
| Alur keluar dan masalah terbesarnya | |
| Opname: frekuensi, lama, selisih terakhir | |
| Perangkat dan sinyal | |
| Sistem sekarang dan keluhan | |
| Fitur yang paling diminta (urut) | |
| Kesediaan membayar | |

Setelah 5 gudang, hitung: berapa yang butuh batch, bin, multi-satuan, picking terarah,
transfer. Angka itu mengunci prioritas Fase 1-3.

## 3. Keputusan terbuka (dari dokumen 10 bagian 9)

Usulan bawaan dipakai untuk membangun fondasi; ubah bila pemilik memutuskan lain.

| # | Keputusan | Usulan bawaan | Status |
| --- | --- | --- | --- |
| 1 | Nama produk | Finlite Gudang | Menunggu |
| 2 | Segmen awal | Gudang/distributor kecil-menengah dan pemilik Kasir dengan gudang pusat | Menunggu |
| 3 | Online-only | Ya, dengan antrean ulang singkat | Menunggu (konfirmasi di wawancara: sinyal gudang) |
| 4 | Batch/kedaluwarsa di MVP? | Fase 2, kecuali wawancara menunjukkan mayoritas menjual makanan/obat | Menunggu data wawancara |
| 5 | Pemilik angka stok bila tersambung ke Accounting | Gudang: kuantitas; Accounting: nilai | Menunggu |
| 6 | Pemilik stok outlet bila tersambung ke Kasir | Kasir: outlet; Gudang: gudang; pindah lewat transfer | Menunggu |
| 7 | Cetak label | Fase 2 | Menunggu |
| 8 | Harga dan batas paket | Setelah wawancara; saat ini harga 0, Gudang Gratis maks 100 barang, Gudang 3 pengguna | Menunggu |

## 4. Draf spesifikasi Fase 1 (disahkan setelah wawancara)

### 4.1 Pemilik domain dan prinsip

- Buku stok (mutasi dan saldo) dimiliki modul Gudang; semua dokumen menulis lewat satu layanan, dalam satu transaksi dengan log aktivitas.
- Saldo per (barang, lokasi). Tidak negatif kecuali pengaturan gudang mengizinkan.
- Nomor dokumen atomik per jenis (pola Kasir). Simpan ulang saat sinyal putus memakai kunci idempoten.

### 4.2 Peran (usulan; hak akses melekat ke orang per fitur, bukan peran bawaan)

| Peran contoh | Izin utama |
| --- | --- |
| Pemilik | Semua, termasuk persetujuan dan pengaturan |
| Kepala gudang | Semua operasi, setujui penyesuaian dan selisih transfer, lihat log |
| Staf gudang | Terima, keluarkan, transfer, putaway, hitung; tanpa penyesuaian |
| Pengamat | Lihat stok dan laporan |

Izin per gudang: staf gudang A tidak melihat gudang B.

### 4.3 User story inti

1. Sebagai staf gudang, saya **menerima** barang dan memindai barcode agar jumlah yang masuk tercatat dan barang punya tempat.
2. Sebagai staf gudang, saya **mengeluarkan** barang dengan surat jalan bernomor agar tidak ada barang keluar tanpa catatan.
3. Sebagai kepala gudang, saya **mentransfer** barang ke gudang lain dan melihat statusnya dalam perjalanan sampai diterima agar tidak hilang di jalan.
4. Sebagai staf gudang, saya mencari **"barang ini di mana"** lewat scan atau ketik agar tidak mencari keliling gudang.
5. Sebagai kepala gudang, saya **menyesuaikan** stok dengan alasan agar setiap koreksi punya jejak.
6. Sebagai pemilik, saya melihat **kartu stok** dan laporan stok per gudang/lokasi dan mengekspornya ke Excel.
7. Sebagai pemilik, saya **mengimpor** barang dan saldo awal dari Excel agar bisa mulai tanpa mengetik ulang.

### 4.4 Diagram status dokumen

```
Penerimaan:   Draf -> Diterima (stok masuk ke lokasi terima) -> [Putaway ke bin] ; Draf -> Dibatalkan
Pengeluaran:  Draf -> Dikeluarkan (stok keluar) ; Draf -> Dibatalkan ; Dikeluarkan -> (batal hanya lewat dokumen retur/penyesuaian)
Transfer:     Draf -> Dikirim (stok keluar dari asal, masuk "dalam perjalanan")
                    -> Diterima (masuk ke tujuan)  | Diterima dengan selisih -> Menunggu keputusan -> Diselesaikan
                    ; Draf -> Dibatalkan
Penyesuaian:  Draf -> Menunggu persetujuan -> Disetujui (stok berubah) | Ditolak
```

Aturan: dokumen yang sudah memengaruhi stok tidak dihapus; koreksi lewat dokumen lawan.

### 4.5 Skenario gagal yang harus lulus tes

- Dua staf mengeluarkan barang terakhir bersamaan: yang kedua ditolak, saldo tidak negatif.
- Simpan dokumen yang sama dua kali (sinyal putus): hanya satu dokumen.
- Transfer diterima dengan jumlah lebih kecil: selisih tercatat, barang tidak hilang dari buku.
- Penyesuaian tanpa alasan atau tanpa izin: ditolak.
- Staf gudang A mengakses gudang B lewat API: ditolak.
- Langganan habis: dokumen baru ditolak (402), data masih bisa dilihat.
- Impor dengan baris salah: baris benar masuk, baris salah dilaporkan per baris.
- Beban: satu gudang 5.000 barang dan 500 mutasi per hari, baca di bawah 250 ms.

### 4.6 Aturan akuntansi

Tidak ada di Fase 1. Jurnal baru muncul lewat jembatan opsional di Fase 4.

### 4.7 Migrasi data

Impor barang (Excel/CSV, pratinjau, produk lama diperbarui lewat SKU/barcode) dan impor
saldo awal sebagai penerimaan awal bertanggal, per lokasi.

### 4.8 Tabel awal tenant Gudang (usulan)

`gudang_items`, `gudang_barcodes`, `gudang_categories`, `gudang_warehouses`,
`gudang_locations` (hierarki zona > rak > bin, jenis lokasi), `gudang_parties`
(pemasok/tujuan), `gudang_receipts` + `_lines`, `gudang_issues` + `_lines`,
`gudang_transfers` + `_lines`, `gudang_adjustments` + `_lines`, `gudang_stock_movements`
(buku stok), `gudang_stock_balances` (saldo per barang per lokasi), `gudang_number_sequences`,
`gudang_audit_logs`, `gudang_settings` (sudah ada).

## 5. Yang dibutuhkan dari pemilik sekarang

1. **Repositori frontend baru**, misalnya `finlite_gudang` (React, Vite, TypeScript, Tailwind), agar saya bisa membuat kerangka aplikasi, PWA, masuk, dan pilih perusahaan. Saya tidak bisa membuat repositori sendiri; setelah repositori ada dan saya diberi akses, kerangkanya saya buat dari Kasir.
2. **Daftar 5-8 gudang** untuk diwawancara dan siapa yang melakukannya (kamu atau saya menyiapkan lembar rekap dan merangkum catatanmu).
3. **Persetujuan atau ubahan** delapan keputusan di bagian 3.
4. Setelah wawancara, saya sahkan draf bagian 4 menjadi spesifikasi Fase 1 dan menyesuaikan prioritas Fase 1-3.
