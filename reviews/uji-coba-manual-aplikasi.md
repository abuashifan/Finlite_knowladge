# Checklist Uji Coba Manual Aplikasi Finlite

> Dokumen ini untuk **kamu coba sendiri di browser**, klik satu-satu tiap fitur dan coba transaksi sungguhan (data uji coba, bukan data asli). Tujuannya: menemukan bug, alur yang aneh, atau fitur yang belum jalan — sebelum dipakai untuk kerja beneran.
>
> **Cara pakai**:
> 1. Kerjakan modul per modul, urut dari atas ke bawah (urutannya sengaja ikut alur bisnis: Master Data dulu, baru transaksi).
> 2. Centang `[x]` setiap langkah yang sudah dicoba dan hasilnya benar.
> 3. Kalau ada yang aneh/error/tidak sesuai — **jangan pusing mikirin kenapa**, langsung catat di tabel **Log Temuan/Bug** di bagian paling bawah. Cukup: apa yang kamu lakukan, apa yang seharusnya terjadi, apa yang beneran terjadi.
> 4. Boleh berhenti dan lanjut kapan saja — isi kolom Status di ringkasan progress supaya tahu sudah sampai mana.

## Ringkasan Progress per Modul

| # | Modul | Sudah Dites? | Ada Bug? |
|---|-------|---------------|----------|
| 1 | Master Data | ⬜ | |
| 2 | Onboarding / Setup Awal | ⬜ | |
| 3 | Penjualan (Sales) | ⬜ | |
| 4 | Pembelian (Purchase) | ⬜ | |
| 5 | Persediaan (Inventory) | ⬜ | |
| 6 | Kas & Bank | ⬜ | |
| 7 | Akuntansi / Jurnal Umum | ⬜ | |
| 8 | Aset Tetap (Fixed Assets) | ⬜ | |
| 9 | Anggaran (Budget) | ⬜ | |
| 10 | Laporan (Reports) | ⬜ | |
| 11 | Pengaturan (Settings) | ⬜ | |
| 12 | Dashboard | ⬜ | |
| 13 | Skenario Gabungan (End-to-End) | ⬜ | |

> Isi kolom "Sudah Dites?" dengan ⬜ Belum / 🔄 Sedang / ✅ Selesai.

---

## 1. Master Data

Data dasar yang dipakai semua modul lain. Kalau ini salah, semua transaksi ikut salah — cek teliti.

- [✅] **Kontak (Customer & Vendor)**: tambah kontak baru sebagai Customer, isi semua field (alamat, NPWP, termin bayar) → simpan → muncul di daftar dengan data lengkap.
- [✅] Tambah kontak baru sebagai Vendor → simpan → cek muncul di dropdown pemilihan vendor saat nanti buat Purchase Order.
- [✅] Edit kontak yang sudah ada → ubah salah satu field → simpan → cek perubahan benar-benar tersimpan (reload halaman untuk pastikan).
- [✅] Coba nonaktifkan/hapus kontak yang **sudah pernah dipakai** di transaksi (kalau ada) — pastikan sistem kasih peringatan, bukan malah data transaksi lama jadi rusak.
- [ ] **Produk**: tambah produk baru (barang & jasa kalau ada bedanya), isi satuan, kategori, harga jual/beli → simpan → muncul di daftar.
- [ ] Edit stok minimum / harga produk → cek berubah di halaman lain yang menampilkan produk itu (misal form Sales Order).
- [ ] **Chart of Account (COA)**: buka daftar akun, coba tambah akun baru dengan tipe yang benar (Aset/Liabilitas/Modal/Pendapatan/Beban) → simpan → cek muncul di dropdown akun saat buat Jurnal Manual.
- [ ] **Pemetaan Akun (Account Mapping)**: cek tiap kategori transaksi (penjualan, pembelian, persediaan, dst) sudah terhubung ke akun COA yang benar. Coba ubah satu mapping → simpan → cek tersimpan.
- [ ] **Data pelengkap**: coba tambah 1 data baru di masing-masing: Kategori Produk, Satuan, Gudang, Departemen, Proyek, Termin Pembayaran (Payment Terms) — pastikan semuanya bisa simpan dan muncul di daftar.

## 2. Onboarding / Setup Awal Perusahaan

- [ ] Kalau ada akun/perusahaan baru yang belum di-setup, jalankan wizard onboarding dari awal sampai selesai.
- [ ] Perhatikan step "Pemetaan Akun" (Account Mapping) di wizard — pastikan bisa lanjut ke step berikutnya setelah mapping diisi, dan datanya sinkron dengan halaman Account Mapping di Master Data/Settings.
- [ ] Cek kalau wizard ditinggal di tengah jalan (tutup browser) lalu dibuka lagi — apakah progressnya tersimpan atau harus ulang dari awal?

## 3. Penjualan (Sales) — Simulasikan Siklus Order-to-Cash Penuh

Coba dari Quotation sampai uang masuk, satu alur penuh dengan data uji:

- [ ] Buat **Quotation (Penawaran)** baru untuk 1 customer, minimal 2 baris produk → simpan.
- [ ] Ubah Quotation itu jadi **Sales Order** (kalau ada tombol convert) → cek data ikut ke Sales Order tanpa perlu input ulang.
- [ ] Dari Sales Order, buat **Delivery Order (Surat Jalan)** → cek stok produk otomatis berkurang di halaman Stock Balance (Inventory).
- [ ] Dari Delivery Order / Sales Order, buat **Sales Invoice (Faktur Penjualan)** → cek angka (subtotal, pajak, total) sesuai dengan Sales Order.
- [ ] Buat **Sales Receipt (Terima Pembayaran)** untuk invoice itu — coba bayar penuh, lalu coba juga skenario bayar sebagian (partial payment) di transaksi lain → cek sisa piutang di **AR Aging** / **AR Summary** berubah sesuai.
- [ ] Coba buat **Sales Return (Retur Penjualan)** untuk salah satu invoice → cek stok bertambah lagi, dan saldo piutang customer terkoreksi.
- [ ] Coba **Customer Deposit** (uang muka dari customer) → cek bisa dipakai untuk membayar invoice berikutnya.
- [ ] Coba buat **Proforma Invoice** → cek bedanya dengan Sales Invoice asli (proforma tidak boleh mempengaruhi jurnal/keuangan).
- [ ] Buka **Customer Ledger** dan **Invoice Ledger** untuk customer yang tadi dipakai → cek semua transaksi di atas muncul dengan urutan dan saldo yang benar.
- [ ] Buka **AR Reconciliation** → cek saldo piutang di modul Sales cocok dengan saldo di Buku Besar (GL) akun piutang.
- [ ] Coba hal-hal "nakal": invoice tanpa Sales Order, quantity 0, harga negatif, tanggal mundur (sebelum periode dibuka) — cek sistem menolak/memberi peringatan yang jelas, bukan malah error tanpa pesan atau tersimpan diam-diam dengan data salah.

## 4. Pembelian (Purchase) — Simulasikan Siklus Procure-to-Pay Penuh

- [ ] Buat **Purchase Request (Permintaan Pembelian)** → ajukan.
- [ ] Ubah/convert jadi **Purchase Order** ke vendor → cek data produk & harga terbawa.
- [ ] Dari PO, buat **Goods Receipt (Penerimaan Barang)** → cek stok produk bertambah di Inventory.
- [ ] Dari Goods Receipt / PO, buat **Vendor Bill (Tagihan dari Vendor)** → cek jumlah tagihan sesuai barang yang diterima (coba juga skenario terima sebagian barang saja).
- [ ] Buat **Vendor Payment (Bayar ke Vendor)** — coba bayar penuh dan bayar sebagian → cek sisa utang di **AP Aging** / **AP Summary** sesuai.
- [ ] Coba **Purchase Return (Retur Pembelian)** → cek stok berkurang lagi dan utang ke vendor terkoreksi.
- [ ] Coba **Vendor Deposit** (uang muka ke vendor) → cek bisa dipakai untuk membayar Vendor Bill berikutnya.
- [ ] Buka **Vendor Ledger** dan **Bill Ledger** → cek semua transaksi di atas tercatat dengan benar.
- [ ] Buka **AP Reconciliation** → cek saldo utang di modul Purchase cocok dengan saldo GL akun utang.
- [ ] Coba hal "nakal" yang sama seperti Sales: bill tanpa PO, quantity/harga aneh, dst.

## 5. Persediaan (Inventory)

- [ ] Buka **Stock Balance** — cek saldo stok tiap produk masuk akal dibanding transaksi yang sudah kamu buat di Sales/Purchase sebelumnya.
- [ ] Buka detail satu produk (**Stock Balance Detail**) → cek mutasinya (masuk/keluar) cocok dengan Delivery Order & Goods Receipt yang sudah dibuat.
- [ ] Buat **Stock Adjustment (Penyesuaian Stok)** manual (misal barang rusak/hilang) → cek stok berubah dan ada jejak jurnal otomatis (kalau memang seharusnya ada).
- [ ] Buat **Stock Movement (Perpindahan Stok)** antar gudang (kalau ada lebih dari 1 gudang) → cek stok di gudang asal berkurang, gudang tujuan bertambah.
- [ ] Jalankan **Stock Opname (Perhitungan Fisik)** → input hasil hitung fisik berbeda dari sistem → submit → cek selisihnya otomatis membuat Stock Adjustment.

## 6. Kas & Bank

- [ ] Buat **Cash Payment (Pengeluaran Kas)** untuk keperluan di luar transaksi Purchase (misal beli ATK) → cek saldo kas berkurang.
- [ ] Buat **Cash Receipt (Penerimaan Kas)** di luar transaksi Sales → cek saldo kas bertambah.
- [ ] Buat **Bank Transfer** antar 2 akun bank/kas → cek saldo kedua akun berubah dengan benar (satu berkurang, satu bertambah, jumlahnya sama).
- [ ] Coba **Bank Reconciliation** — cocokkan mutasi di sistem dengan "mutasi rekening koran" (data uji manual) → cek fitur reconcile menandai transaksi cocok/tidak cocok dengan benar.

## 7. Akuntansi / Jurnal Umum

- [ ] Buat **Jurnal Manual (Journal Entry)** — pastikan debit = kredit sebelum bisa disimpan (coba juga input yang sengaja tidak balance, harus ditolak sistem).
- [ ] Kalau ada mapping akun yang belum lengkap, coba posting jurnal dari modul lain (misal Sales Invoice) dan lihat apakah muncul **peringatan (warning)** yang jelas soal akun yang belum di-mapping.
- [ ] Buka **Journal List** → cek semua jurnal (manual maupun otomatis dari transaksi Sales/Purchase/dll di atas) muncul di sini.
- [ ] Cek **Fiscal Year (Tahun Buku)** — pastikan periode yang aktif benar, coba buka detail.
- [ ] Coba **Period Lock (Kunci Periode)** untuk 1 bulan → setelah dikunci, coba buat transaksi baru dengan tanggal di bulan itu → sistem harus menolak.
- [ ] Coba **Period End (Tutup Periode/Bulan)** untuk periode yang datanya sudah kamu isi di atas → ikuti semua langkahnya → cek tidak ada step yang macet, dan setelah ditutup semua laporan periode itu tidak bisa diubah lagi.

## 8. Aset Tetap (Fixed Assets)

- [ ] Buat **Kategori Aset** baru (misal "Kendaraan", umur ekonomis sekian tahun).
- [ ] Buat **Aset Tetap** baru, pakai kategori di atas, isi nilai perolehan & tanggal perolehan → simpan.
- [ ] Cek **Laporan Penyusutan (Depreciation)** — apakah nilai penyusutan aset baru ini muncul dan hitungannya masuk akal sesuai umur ekonomis.
- [ ] Coba **Disposal (Pelepasan Aset)** untuk aset uji itu (jual/hapus buku) → cek nilai buku & jurnalnya benar.
- [ ] Cek **Fixed Asset Register** dan **Reconciliation Report** — datanya konsisten dengan yang barusan kamu input.

## 9. Anggaran (Budget)

- [ ] Buat **Budget Period** baru (misal untuk tahun berjalan).
- [ ] Isi baris anggaran per akun/departemen → **Submit** untuk approval.
- [ ] Coba proses **Approval** (approve/reject) — kalau ada 2 role berbeda, coba login sebagai approver untuk uji ini.
- [ ] Buka **Budget Comparison** → cek anggaran vs realisasi (bandingkan dengan transaksi yang sudah kamu buat di modul lain) — angkanya masuk akal?

## 10. Laporan (Reports)

Buka **satu per satu**, pastikan tidak ada halaman yang blank/error, dan angkanya masuk akal dibanding transaksi uji yang sudah kamu buat di atas:

- [ ] Neraca (Balance Sheet) — termasuk versi Multi-Periode.
- [ ] Laba Rugi (Profit & Loss) — termasuk versi Multi-Periode.
- [ ] Arus Kas (Cash Flow) — termasuk versi Direct Method.
- [ ] Perubahan Ekuitas (Equity Changes), Laba Ditahan (Retained Earnings).
- [ ] Neraca Saldo (Trial Balance), Buku Besar (General Ledger), Rincian per Akun (Account Ledger).
- [ ] Rekonsiliasi (Reconciliation), Ringkasan Keuangan (Financial Summary).
- [ ] Laporan AR: Aging, Outstanding, Summary per Customer.
- [ ] Laporan AP: Aging, Outstanding, Summary per Vendor.
- [ ] Laporan Penjualan: Summary, per Customer, per Produk.
- [ ] Laporan Pembelian: Summary, per Vendor, per Produk.
- [ ] Laporan Persediaan: Stock Report, Inventory Aging, Inventory Analysis, Opname Worksheet.
- [ ] Laporan Pajak: PPN Masukan (Input VAT), PPN Keluaran (Output VAT), Ekspor E-Faktur (coba export filenya, buka hasilnya).
- [ ] Laporan Aset Tetap (lihat bagian 8 di atas juga).
- [ ] **Filter & Export**: di minimal 3 laporan berbeda, coba ganti filter tanggal/periode → cek data ikut berubah. Coba export ke CSV/Excel → buka filenya, cek datanya sesuai dengan yang tampil di layar.
- [ ] **Saved Reports** — coba simpan 1 laporan dengan filter tertentu, buka lagi nanti, cek filternya tersimpan.

## 11. Pengaturan (Settings)

- [ ] **Company Settings** — ubah salah satu data perusahaan (nama, alamat, logo) → simpan → cek muncul di tempat lain (misal header cetakan invoice kalau ada).
- [ ] **Users** — undang user baru (Invitation), cek role-nya bisa diatur, coba nonaktifkan user.
- [ ] **Roles** — cek daftar permission per role, coba buat role baru dengan akses terbatas, login pakai user itu (kalau memungkinkan) untuk cek pembatasan benar-benar berlaku.
- [ ] **Accounting Period** settings — cek pengaturan periode akuntansi aktif.
- [ ] **Transaction Settings** — cek pengaturan nomor otomatis / prefix transaksi, coba ubah dan buat transaksi baru untuk lihat efeknya.
- [ ] **Account Mapping Settings** — sama seperti di Master Data, pastikan konsisten dengan halaman Account Mapping lainnya.
- [ ] **Access Audit** — cek log aktivitas user tercatat (misal setelah kamu edit-edit di atas, apakah muncul di log ini).
- [ ] **My Preferences** — ubah preferensi pribadi (misal bahasa/tampilan) → cek tersimpan setelah logout-login lagi.

## 12. Dashboard

- [ ] Buka Dashboard setelah semua transaksi uji di atas dibuat → cek widget/angka ringkasan (penjualan, piutang, kas, dst) mencerminkan transaksi yang baru dibuat.
- [ ] Coba klik widget/grafik kalau bisa diklik → cek mengarah ke halaman detail yang benar.

## 13. Skenario Gabungan (End-to-End) — Simulasi 1 Bulan Operasional

Ini bagian paling penting: coba jalankan **satu siklus bulan penuh** memakai semua data uji di atas, lalu cek semuanya nyambung:

- [ ] Semua transaksi Sales & Purchase di atas sudah tercatat jurnalnya secara otomatis (cek di Journal List).
- [ ] Saldo kas/bank di Cash & Bank cocok dengan saldo di GL.
- [ ] Saldo piutang (AR) dan utang (AP) di modul masing-masing cocok dengan saldo di Neraca.
- [ ] Nilai stok di Inventory cocok dengan nilai persediaan di Neraca.
- [ ] Tutup periode/bulan uji ini (Period End) → setelah tutup, cek Neraca & Laba Rugi periode itu sudah final dan tidak bisa diubah lagi.
- [ ] Buka periode berikutnya → cek saldo awal (opening balance) periode baru = saldo akhir periode yang baru ditutup.

---

## Log Temuan / Bug

Isi setiap kali menemukan sesuatu yang aneh. Tidak perlu bahasa teknis — tulis apa adanya.

| No | Tanggal | Modul/Halaman | Apa yang Dilakukan | Hasil yang Diharapkan | Hasil yang Terjadi | Tingkat (Ringan/Sedang/Parah) | Status |
|----|---------|----------------|---------------------|-------------------------|----------------------|-------------------------------|--------|
| 1 | | | | | | | Belum Diperbaiki |

