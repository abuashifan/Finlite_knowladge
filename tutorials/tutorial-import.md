# Tutorial Import Data

> Panduan langkah-demi-langkah untuk mengimpor data ke Finlite ERP.
> **Berlaku mulai:** Basic (master data), Pro (transaksi).

---

## Daftar Isi

1. [Sebelum Mulai](#1-sebelum-mulai)
2. [Unduh Template](#2-unduh-template)
3. [Isi Berkas](#3-isi-berkas)
4. [Unggah & Petakan Kolom](#4-unggah--petakan-kolom)
5. [Periksa Pratinjau](#5-periksa-pratinjau)
6. [Commit & Posting](#6-commit--posting)
7. [Impor Master Data](#7-impor-master-data)
8. [Impor Faktur Penjualan](#8-impor-faktur-penjualan)
9. [Impor Pembelian](#9-impor-pembelian)
10. [Impor Jurnal Umum](#10-impor-jurnal-umum)
11. [Membatalkan Batch](#11-membatalkan-batch)
12. [Pertanyaan Umum](#12-pertanyaan-umum)

---

## 1. Sebelum Mulai

### Siapa yang bisa mengimpor?

| Jenis Impor | Tier Minimum | Izin Diperlukan |
|---|---|---|
| Master data (kontak, produk, COA) | **Basic** | `masterdata.import` |
| Transaksi (faktur, pembelian, jurnal) | **Pro** | `transactions.import` |

> 💡 Pastikan role kamu memiliki izin di atas. Buka **Access → Roles** untuk memeriksa.

### Aturan penting

- **Maksimal 1.000 baris per berkas.** Lebih dari itu ditolak saat unggah.
- **Satu batch aktif per perusahaan.** Selesaikan atau batalkan batch yang sedang berjalan sebelum mengunggah yang baru.
- **Hasil impor SELALU berupa draft.** Tidak ada dokumen yang otomatis terposting — kamu memeriksa hasilnya dulu, lalu posting manual lewat aksi bulk.
- **Kolom `Ref` wajib diisi.** Ini kunci supaya impor tidak menghasilkan dokumen ganda. Isinya bisa nomor dari sistem lama, atau format `{JENIS}-{TANGGAL}-{URUT}` (contoh: `INV-20260812-001`).

### Format berkas yang didukung

- **`.xlsx`** (Excel)
- **`.csv`** (Comma-Separated Values)

---

## 2. Unduh Template

Cara termudah adalah mengunduh template yang sudah disediakan:

1. Buka halaman **Import** di sidebar
2. Klik tombol **"Unduh Template"**
3. Pilih profil yang ingin diimpor (misal: `sales_invoice`, `contact`, `journal_entry`)
4. Template akan terunduh dengan header kolom yang sudah benar

> 💡 **Simpan pemetaan kolom** setelah pertama kali memetakan — template dari sistem lain bisa dipetakan sekali dan dipakai ulang setiap hari.

---

## 3. Isi Berkas

### Untuk master data (satu baris = satu record)

| Kolom | Wajib? | Keterangan |
|---|---|---|
| `Ref` | ✅ | Kunci idempoten — nomor unik dari sistem asal |
| Kolom data lainnya | Sesuai template | Ikuti petunjuk di baris contoh template |

### Untuk transaksi (beberapa baris = satu dokumen)

Satu faktur bisa punya banyak baris barang. Gunakan **`Ref` yang sama** untuk baris-baris yang membentuk satu dokumen:

| Ref | Tanggal | Pelanggan | Produk | Qty | Harga |
|---|---|---|---|---|---|
| `INV-001` | 2026-08-12 | PT Alfa | Barang A | 2 | 50.000 |
| `INV-001` | 2026-08-12 | PT Alfa | Barang B | 1 | 75.000 |
| `INV-002` | 2026-08-12 | PT Beta | Barang A | 5 | 50.000 |

> Dua baris pertama dengan `Ref` `INV-001` akan jadi **satu faktur** dengan **dua baris barang**.

---

## 4. Unggah & Petakan Kolom

### Langkah 1: Unggah berkas

1. Buka halaman **Import**
2. Klik tombol **"Unggah Berkas"**
3. Pilih berkas `.xlsx` atau `.csv` dari komputer kamu
4. Sistem akan membaca header kolom dari berkas kamu

> ⚠️ Kalau berkas yang sama sudah pernah diunggah sebelumnya, sistem akan memberi **peringatan** — ini mencegah unggahan ganda yang tidak disengaja.

### Langkah 2: Petakan kolom

Kalau header berkas kamu **tidak persis sama** dengan nama field Finlite:

1. Sistem menampilkan dua kolom berdampingan: **Kolom di Berkas** di kiri, **Field Finlite** di kanan
2. Cocokkan setiap kolom dengan field yang sesuai
3. Klik **"Simpan Pemetaan"** — sistem akan menjalankan validasi

> 💡 Pemetaan yang sudah disimpan bisa dipakai lagi untuk impor berikutnya. Cocok untuk impor harian dari sistem yang sama.

---

## 5. Periksa Pratinjau

Setelah pemetaan disimpan, sistem otomatis memvalidasi setiap baris. Layar pratinjau menampilkan:

| Bagian | Isi |
|---|---|
| **Ringkasan** | Total baris, jumlah valid, jumlah gagal |
| **Tabel galat** | Baris yang bermasalah + pesan kesalahan per kolom |
| **Pratinjau data** | Data yang sudah dinormalisasi, dikelompokkan per dokumen (untuk transaksi) |

### Kesalahan yang diperiksa di pratinjau

| Pemeriksaan | Contoh pesan |
|---|---|
| `Ref` sudah pernah dipakai | "Ref INV-001 sudah dipakai di batch #14 (2026-08-10)" |
| Pelanggan tidak dikenal | "Pelanggan 'PT XYZ' tidak ditemukan" |
| Produk tidak dikenal | "Produk 'Barang Z' tidak ditemukan" |
| Tanggal di periode terkunci | "Tanggal 2026-01-15 berada di periode yang sudah ditutup" |
| Kolom wajib kosong | "Kolom 'tanggal' wajib diisi" |
| Format angka salah | "Nilai 'abc' bukan angka yang valid" |

### Yang harus kamu lakukan di layar ini

- **Periksa baris bergalat** — perbaiki di berkas asal dan unggah ulang, atau abaikan baris yang salah
- **Tombol "Commit" hanya aktif** kalau minimal ada satu baris valid
- Kalau semua baris gagal → perbaiki berkas dan unggah ulang

> ⚠️ **Jangan commit sebelum yakin.** Apa yang sudah di-commit akan menjadi draft dokumen. Walaupun draft bisa dihapus, lebih baik periksa dulu.

---

## 6. Commit & Posting

### Commit (membuat draft)

1. Di layar pratinjau, klik **"Commit"**
2. Sistem akan membuat dokumen **draft** untuk setiap baris/kelompok yang valid
3. Baris yang gagal **tidak** dibuatkan dokumen — bisa diperbaiki di batch terpisah

### Posting (memposting draft)

Karena semua hasil impor adalah **draft**, kamu perlu mempostingnya setelah memeriksa:

1. Buka daftar dokumen (misal: **Penjualan → Faktur Penjualan**)
2. Filter status: **Draft**
3. Pilih dokumen yang ingin diposting (bisa pilih semua)
4. Klik **"Posting Massal"** (`POST /sales/invoices/bulk-post`)

> 💡 **Posting massal bisa dipakai di luar impor juga** — memposting banyak draft sekaligus yang sebelumnya harus dilakukan satu per satu.

### Kenapa tidak auto-post?

Keputusan ini sengaja: kalau ada kesalahan di berkas, memperbaikinya cukup **hapus draft** — tidak perlu void jurnal, tidak perlu jurnal balik, tidak ada yang masuk buku besar. Jauh lebih aman untuk operasi harian.

---

## 7. Impor Master Data

> **Tier:** Basic ke atas

### Profil yang tersedia

| Profil | Template | Catatan |
|---|---|---|
| **Kontak** (pelanggan/pemasok) | `contact` | Nama, tipe, alamat, NPWP, telepon |
| **Produk** | `product` | Nama, satuan, harga, akun penjualan/pembelian |
| **Chart of Account** | `coa` | Kode akun, nama, tipe, kategori |

### Alur

1. Unduh template profil yang diinginkan
2. Isi data — ikuti baris contoh di template
3. Unggah → petakan kolom → periksa pratinjau → commit
4. Data langsung tersedia (master data tidak perlu posting)

---

## 8. Impor Faktur Penjualan

> **Tier:** Pro ke atas

### Template

Template faktur penjualan mencakup:

| Kolom | Wajib | Keterangan |
|---|---|---|
| `Ref` | ✅ | Nomor referensi — kunci pengelompokan + idempoten |
| `Tanggal` | ✅ | Format: `YYYY-MM-DD` |
| `Pelanggan` | ✅ | Nama pelanggan (harus sudah ada di master data) |
| `Produk` | ✅ | Nama produk (harus sudah ada di master data) |
| `Kuantitas` | ✅ | Angka bulat atau desimal |
| `Harga` | ✅ | Harga satuan |
| `Termin` | — | Nama termin pembayaran (contoh: `NET30`) |
| `Gudang` | — | Nama gudang (kalau kosong, pakai gudang utama) |

### Yang terjadi setelah commit

- Satu `Ref` dengan beberapa baris → **satu faktur** dengan beberapa baris barang
- Setiap faktur disimpan sebagai **draft** dengan nomor faktur otomatis
- Piutang dan jurnal **belum** terbentuk — baru terbentuk saat diposting

### Yang terjadi saat posting massal

- `TransactionDateGuardService` memeriksa apakah tanggal faktur di periode yang masih terbuka
- Stok berkurang sesuai kuantitas
- Jurnal otomatis terbit (Piutang Usaha di debit, Penjualan di kredit)
- Nomor faktur diberikan oleh `DocumentNumberService`

---

## 9. Impor Pembelian

> **Tier:** Pro ke atas

Alur sama dengan faktur penjualan, menggunakan `VendorBillService`:

| Kolom | Wajib | Keterangan |
|---|---|---|
| `Ref` | ✅ | Nomor referensi |
| `Tanggal` | ✅ | Format: `YYYY-MM-DD` |
| `Pemasok` | ✅ | Nama pemasok (harus sudah ada di master data) |
| `Produk` | ✅ | Nama produk |
| `Kuantitas` | ✅ | Angka |
| `Harga` | ✅ | Harga satuan |
| `Termin` | — | Nama termin pembayaran |

---

## 10. Impor Jurnal Umum

> **Tier:** Pro ke atas

### Template

| Kolom | Wajib | Keterangan |
|---|---|---|
| `Ref` | ✅ | Nomor referensi |
| `Tanggal` | ✅ | Format: `YYYY-MM-DD` |
| `Deskripsi` | ✅ | Keterangan jurnal |
| `Akun` | ✅ | Kode atau nama akun (harus sudah ada di COA) |
| `Debit` | — | Nilai debit (biarkan kosong kalau kredit) |
| `Kredit` | — | Nilai kredit (biarkan kosong kalau debit) |

> ⚠️ **Debit dan Kredit tidak boleh sama-sama kosong atau sama-sama diisi** untuk satu baris.

### Validasi tambahan

Selain validasi standar, pratinjau jurnal juga memeriksa:

- **Keseimbangan per kelompok `Ref`**: total debit = total kredit
- Setiap akun dikenal di Chart of Account
- Akun tidak terkunci/dinonaktifkan

---

## 11. Membatalkan Batch

Kalau seluruh batch perlu dibatalkan:

1. Buka halaman **Import**
2. Temukan batch yang sedang berjalan
3. Klik **"Batalkan"** (DELETE `/imports/{uuid}`)

Yang terjadi:

- **Semua draft yang sudah terlanjur dibuat ikut terhapus**
- Berkas unggahan dihapus dari server
- `Ref` yang sudah dipakai di batch ini bisa dipakai ulang di batch baru

> 💡 Tidak perlu membatalkan batch kalau hanya beberapa baris yang salah — baris gagal tidak dibuatkan dokumen, dan baris yang sudah jadi draft bisa dihapus satu per satu dari daftar dokumen.

---

## 12. Pertanyaan Umum

### Q: Berapa lama berkas impor disimpan?

Berkas disimpan 30 hari setelah batch selesai, supaya masih bisa ditelusuri saat rekonsiliasi. Setelah itu otomatis dihapus.

### Q: Apa yang terjadi kalau saya unggah berkas yang sama dua kali?

Sistem mendeteksi `file_hash` yang sama dan memberi peringatan: *"Berkas ini sudah pernah diunggah tanggal …, lanjutkan?"* Ini mencegah kecelakaan, tapi tidak memblokir — kamu tetap bisa lanjut kalau memang sengaja.

### Q: Bisakah saya mengimpor ke periode yang sudah ditutup?

**Pratinjau akan menolaknya.** Tanggal di periode tertutup ditandai sebagai galat sebelum satu pun dokumen dibuat. Ini diperiksa oleh `TransactionDateGuardService` yang sama dengan form manual.

### Q: Bagaimana kalau impor saya lebih dari 1.000 baris?

Pecah menjadi beberapa berkas. Unggah satu per satu — selesaikan batch pertama dulu sebelum mengunggah yang kedua (satu batch aktif per perusahaan).

### Q: Apakah nomor faktur dari impor bentrok dengan nomor dari form manual?

Tidak. Keduanya melewati `DocumentNumberService` yang sama — tidak ada jalur pintas. Nomor urut tetap berurutan.

### Q: Apa yang terjadi kalau kuota penyimpanan saya terlampaui?

Sistem akan menolak unggahan dengan kode `STORAGE_QUOTA_EXCEEDED`. Bersihkan berkas impor lama atau hubungi admin untuk naik tier.

| Tier | Kuota Penyimpanan |
|---|---|
| Basic | 1 GB |
| Pro | 2 GB |
| Enterprise | 5 GB |
| Custom | Manual |
