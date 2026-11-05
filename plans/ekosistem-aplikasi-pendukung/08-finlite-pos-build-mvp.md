# 08 — Finlite POS: hasil build MVP (fase 1)

Status per 5 November 2026. Dokumen ini mencatat apa yang sudah dibangun,
melengkapi konsep di dokumen 06 dan keputusan platform di dokumen 07.

## Tahap P (fondasi platform) — selesai sebagian

- `tenant_databases.product` (default `accounting`), unik per (company, product).
  Kode lama tetap memakai tenant akuntansi lewat global scope.
- Satu perusahaan bisa punya tenant POS terpisah (`company_000001_pos.sqlite` /
  schema `tenant_000001_pos`), migrasi di `database/migrations/tenant_pos`.
- Middleware `company.access:pos`, izin `pos.*` di matriks hak akses.
- Belum: dimensi produk di paket/langganan, pendaftaran publik khusus POS.

## Backend (`laravel_backend`, modul `app/Modules/Pos`)

Aktivasi oleh pemilik, bootstrap aplikasi, kategori & produk (stok opsional,
barcode), mutasi stok, pelanggan & kasbon, shift kasir dengan rekap laci,
penjualan tunai/transfer/QRIS/kasbon, pembatalan selama shift terbuka, laporan
ringkas, pengaturan toko.

## Frontend (repo privat `finlite_pos`)

React + Vite, mobile-first. Login akun Finlite, pilih toko, kasir dengan scan
barcode, pembayaran dengan nominal cepat, struk WhatsApp/cetak browser,
produk, pelanggan, transaksi, shift, laporan, pengaturan.

## Keputusan bawaan yang diambil

- Stok dilacak per produk (`track_stock`); penjualan ditolak bila stok kurang,
  kecuali pengaturan "jual walau stok habis" dinyalakan.
- Kasbon wajib pelanggan; boleh uang muka tunai.
- Satu kasir satu shift terbuka; transaksi hanya bisa dibatalkan selama shiftnya
  masih terbuka.
- Nomor transaksi `PJ-YYMMDD-0001`, pelunasan kasbon `KB-YYMMDD-0001`.
- Diskon per transaksi (nominal); belum ada pajak, varian, atau multi-satuan.

## Belum dikerjakan

- Cetak langsung ke printer thermal Bluetooth (perlu uji di HP dan printer nyata).
- Retur barang, pembelian/stok masuk dengan pemasok, multi-gudang.
- Jembatan ke Finlite Accounting (jurnal penjualan harian).
- Dimensi produk pada paket langganan dan kuota.
