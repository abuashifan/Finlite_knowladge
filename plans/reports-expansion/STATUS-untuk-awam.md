# Status Fitur Laporan — Penjelasan untuk Non-Teknis

> Dokumen ini menjelaskan kondisi fitur **Laporan** di aplikasi Finlite dengan
> bahasa sehari-hari, tanpa istilah pemrograman. Terakhir diperbarui: 12 Juli 2026,
> setelah semua tahap pengerjaan (Tahap 0 sampai 14) selesai.

---

## Gambaran singkat

Bayangkan aplikasi Finlite seperti sebuah **kantor akuntan digital**. Salah satu
ruangannya adalah **ruang Laporan** — tempat kamu bisa mencetak berbagai laporan
keuangan: neraca, laba rugi, arus kas, daftar utang-piutang, laporan pajak, dan
sebagainya.

Pekerjaan besar kemarin adalah **melengkapi isi ruang Laporan itu**: dari yang
tadinya cuma punya sedikit laporan, sekarang sudah punya puluhan jenis laporan
lengkap, plus beberapa fitur tambahan yang mempermudah pemakaian.

**Kabar baik: seluruh 15 tahap rencana (Tahap 0–14) sudah SELESAI.** Fitur inti
sudah bisa dipakai. Yang tersisa di bawah ini adalah **penyempurnaan**, **catatan
keterbatasan**, dan **hal yang memang sengaja tidak dibuat** — bukan pekerjaan
pokok yang belum jadi.

---

## A. Penyempurnaan yang masih bisa dilanjutkan (opsional, cepat)

Di tahap terakhir kami memasang dua "kenyamanan" baru di ruang Laporan. Keduanya
sudah **berfungsi**, tapi baru dipasang di **sebagian** laporan — sisanya tinggal
dipasangi dengan pola yang sama (seperti memasang saklar lampu yang sudah terbukti
menyala, tinggal dipasang di ruangan lain).

**1. Memilih kolom yang ingin ditampilkan**
Bayangkan sebuah tabel laporan punya banyak kolom (Kode, Nama Akun, Debit, Kredit,
Saldo, dst). Fitur ini membiarkan pengguna **mencentang kolom mana saja yang mau
dilihat**, biar tampilan lebih ringkas.
- Sudah terpasang di: **Buku Besar** dan **Neraca Saldo**.
- Belum terpasang di: Buku Besar per Akun, Laba Rugi, Neraca, Arus Kas, Umur
  Piutang, Umur Utang, Mutasi Rekening.

**2. Menyaring data langsung dari filter (mis. per pelanggan / per pemasok)**
Selain menyaring berdasarkan tanggal, pengguna bisa menyaring laporan untuk satu
pelanggan atau satu pemasok tertentu.
- Sudah terpasang & benar-benar berfungsi di: **Umur Piutang (per pelanggan)** dan
  **Umur Utang (per pemasok)**.
- Belum terpasang di: Mutasi Rekening (per rekening), Laporan Stok & Analisis
  Inventori (per produk).

**3. Tampilan ringkas nama filter**
Setelah laporan dijalankan, di bagian atas muncul ringkasan filter. Saat ini masih
menulis keterangan umum seperti *"Pelanggan difilter"*, belum menampilkan **nama
pelanggannya langsung**. Ini sekadar poles tampilan.

> Intinya: pondasinya sudah jadi dan terbukti jalan. Melengkapi sisanya tinggal
> "menyalin pola" ke laporan lain — pekerjaan cepat, risiko kecil.

### Apa maksud "sengaja di-defer"?

"Di-defer" artinya **sengaja ditunda, bukan gagal atau rusak**. Ini keputusan
sadar: kami pasang dulu dua kenyamanan itu di **beberapa laporan sebagai contoh
yang sudah terbukti benar**, lalu sisanya menyusul belakangan. Ibarat tukang yang
memasang model saklar baru di 2 ruangan dulu untuk memastikan menyala sempurna,
sebelum memasang model yang sama ke seluruh ruangan. Ditunda supaya perubahan
tetap aman dan bisa dipakai, bukan karena sulit.

### Dampaknya ke aplikasi apa?

**Yang PENTING: tidak ada dampak buruk ke kebenaran data.** Semua laporan — baik
yang sudah maupun belum dapat kenyamanan ini — tetap menampilkan **angka yang benar
dan lengkap**. Tidak ada laporan yang jadi salah, kurang, atau tidak bisa dibuka.

Yang berbeda hanya soal **kenyamanan** dan **konsistensi rasa pakai**:

1. **Di laporan yang belum bisa "pilih kolom":**
   Semua kolom selalu tampil. Kalau kolomnya banyak, tabel terasa penuh dan lebar,
   sehingga perlu digeser ke samping (scroll). Pengguna belum bisa menyembunyikan
   kolom yang tidak dibutuhkan agar tampilan lebih ringkas.
   → *Dampak: tampilan kurang rapi, bukan datanya salah.*

2. **Di laporan yang belum bisa "filter per pelanggan/pemasok/produk":**
   Untuk melihat data satu pelanggan (atau satu produk) saja, pengguna harus
   membuka seluruh daftar lalu mencari manual, atau mengekspor ke Excel dan
   menyaring di sana. Belum bisa langsung menyaring dari dalam aplikasi.
   → *Dampak: butuh langkah ekstra untuk fokus ke satu pihak, bukan datanya salah.*

3. **Rasa yang belum seragam:**
   Karena fitur baru ada di sebagian laporan, pengalaman terasa tidak konsisten —
   pengguna bisa bertanya *"kok di Buku Besar bisa pilih kolom, tapi di Laba Rugi
   tidak?"*. Ini wajar selama masa peralihan dan hilang begitu semua laporan
   dilengkapi.

**Ringkas:** ini soal kepraktisan dan kerapian, **bukan** soal benar/salahnya
laporan. Aplikasi tetap aman dipakai apa adanya; melengkapi sisanya sekadar
membuat semua laporan sama nyamannya.

---

## B. Hal yang perlu kamu ketahui (keterbatasan saat ini)

**1. Ekspor E-Faktur (pajak)**
Fitur mengunduh file E-Faktur untuk pajak sudah ada. Tapi:
- Formatnya versi **sederhana** (satu baris per faktur), belum format lengkap
  aplikasi e-Faktur resmi DJP yang lebih rumit.
- **Nomor Faktur Pajak (16 digit) dikosongkan** karena aplikasi belum menyimpan
  nomor itu. Untuk sekarang, nomor tersebut perlu **diisi manual** setelah file
  dibuka. Kalau nanti mau otomatis, perlu penambahan kolom penyimpanan.

**2. Laporan Tersimpan**
Fitur "menyimpan kombinasi filter laporan" (biar tidak perlu setel ulang tiap kali)
sudah jalan, termasuk **berbagi ke rekan kerja**. Tapi tombol "Simpan Laporan" baru
dipasang di **4 laporan** paling sering dipakai (Buku Besar, Neraca Saldo, Laba
Rugi, Neraca). Laporan lain belum ada tombolnya — tinggal ditambah bila diperlukan.

---

## C. Yang SENGAJA tidak dibuat (keputusan desain, bukan pekerjaan tertunda)

Beberapa hal memang diputuskan **tidak dikerjakan** sejak awal, sesuai kesepakatan.
Ini **bukan** daftar tugas yang belum selesai — jangan dianggap kurang. Kalau suatu
saat dibutuhkan, itu keputusan baru yang harus dibahas dulu:

- **Pelacakan nomor seri / batch barang** (misalnya melacak tiap unit barang lewat
  nomor seri).
- **Laporan khusus per Cabang / Departemen / Proyek** sebagai laporan tersendiri.
  (Menyaring laporan berdasarkan departemen/proyek **sudah bisa** — yang tidak
  dibuat adalah laporan terpisah khusus untuk itu.)
- **Metode penilaian stok FIFO** (cara hitung nilai persediaan tertentu).
- **Format untuk impor data** dari luar.

---

## D. Yang belum diperiksa

Kami sudah memastikan program **tidak error** lewat pemeriksaan otomatis (semacam
"cek mesin" internal — semuanya lolos). Tapi belum ada **uji coba manual di layar**
seperti pengguna sungguhan: membuka tiap laporan satu per satu, benar-benar
mengunduh file E-Faktur lalu membukanya di Excel, dan mengecek tampilan di layar
tablet (iPad). Disarankan ada sesi uji coba tampilan sebelum dipakai luas.

---

## E. Catatan teknis (untuk tim IT)

Semua hasil pekerjaan Tahap 11–14 **masih tersimpan di komputer kerja lokal dan
belum "dikirim" ke server pusat** (dalam istilah teknis: belum di-*push*). Artinya
perubahan sudah jadi, tapi belum dibagikan ke repositori bersama. Perlu satu
langkah "kirim" agar rekan tim lain bisa melihat/memakainya.

---

## Ringkasan satu kalimat

**Fitur Laporan sudah lengkap dan berfungsi; yang tersisa hanyalah menyempurnakan
kenyamanan di sebagian laporan, beberapa catatan keterbatasan (E-Faktur & tombol
simpan), hal-hal yang memang sengaja tidak dibuat, serta langkah "kirim ke server"
dan uji coba tampilan.**
