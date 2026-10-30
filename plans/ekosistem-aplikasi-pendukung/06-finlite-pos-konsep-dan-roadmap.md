# Finlite POS — Konsep Produk dan Roadmap v0.1

> **STATUS: RENCANA PENGEMBANGAN BARU / BELUM DIIMPLEMENTASIKAN**
>
> Keputusan konsep per 2026-10-30. Dokumen ini bukan deskripsi fitur aktif dan bukan spesifikasi teknis final.

## 1. Keputusan yang sudah disepakati

- Finlite POS adalah **produk mandiri**: dapat dibeli dan digunakan tanpa langganan Finlite Accounting.
- Produk dapat dijual standalone, ditambahkan ke langganan organisasi sebagai produk tambahan, atau dijual melalui bundle. Integrasi Accounting/WMS/CRM tetap opsional.
- **Web-first, online-only**: antarmuka kasir dan backoffice melalui browser laptop/tablet. Finalisasi transaksi **memerlukan koneksi ke server**. Tidak ada transaksi offline atau antrean penjualan lokal pada MVP.
- **Finlite Device Bridge wajib masuk MVP sejak awal**, bukan fase lanjutan; digunakan untuk akses printer struk, printer label barcode, dan cash drawer. Scanner mode HID dapat langsung mengisi input browser.
- Sasaran fase awal adalah **retail barang fisik**, **bukan restoran/F&B**. Manajemen meja, kitchen display, resep, split bill restoran, dan workflow dapur tidak termasuk MVP.
- Finlite ID bersama, dengan organisasi, role, scope outlet, dan entitlement aplikasi yang terpisah. Pengguna hanya melihat data yang diizinkan.

## 2. Segmen pasar dan prioritas

| Prioritas | Segmen | Masalah utama | Karakteristik |
| --- | --- | --- | --- |
| P1 | Minimarket lokal / toko kebutuhan harian | Kasir cepat, barcode, stok, shift, laporan | Banyak transaksi dan SKU |
| P1 | Toko ATK, buku, perlengkapan sekolah | Barcode, kategori, stok, supplier, harga | Retail barang standar |
| P1 | Koperasi sekolah/yayasan | Operasional kasir, kontrol petugas, laporan | Potensi integrasi Accounting/Workspace |
| P2 | Toko alat listrik, hardware, bangunan ringan | Multi-satuan, banyak SKU, harga bertingkat | Perlu fitur satuan/konversi |
| P2 | Fashion, sepatu, aksesori | Varian ukuran/warna, retur/exchange | Perlu variant SKU |
| Lanjutan | Apotek atau kategori batch/expired | Lot/expiry, kepatuhan khusus | Di luar MVP |

**ICP awal (hipotesis):** retail 1–3 outlet yang menggunakan barcode atau akan menerapkannya, membutuhkan kontrol stok/shift dan laporan owner. Validasi melalui wawancara/pilot sebelum menetapkan harga dan positioning. Jangan menjanjikan semua segmen siap sejak peluncuran.

## 3. Nilai produk

POS yang sederhana bagi kasir dan kuat untuk kontrol toko: barcode, transaksi cepat, persediaan outlet, shift, pembayaran, struk, retur, dan laporan. Produk tetap mandiri; saat bisnis tumbuh, pemilik dapat menambah Accounting/WMS/CRM tanpa membangun ulang sistem penjualan.

## 4. Komponen produk

1. **POS Cashier (web):** layar transaksi, scan barcode, cart, diskon, checkout, pembayaran, struk, retur sesuai izin.
2. **POS Backoffice (web):** katalog, SKU/barcode, kategori, harga, stok, outlet, register, pegawai, shift, laporan, konfigurasi.
3. **Finlite Device Bridge (local service):** pasangan tepercaya untuk printer/cash drawer, device detection, pairing register, test print, log dan status koneksi.
4. **POS Cloud/API:** transaksi resmi, inventory ledger, pembayaran, shift, permissions, audit, laporan dan API integrasi.
5. **Finlite Platform:** identitas, organisasi, subscription/entitlement, akses produk dan koneksi integrasi; perlu audit kesesuaian dengan backend yang ada.

Frontend harus responsif untuk laptop dan tablet; dukungan hardware spesifik memerlukan pengujian per OS/browser/model perangkat.

## 5. MVP operasional

### Master dan setup
- Buat/pilih organisasi, outlet, register, kasir dan supervisor sesuai otorisasi.
- Produk, SKU, barcode, kategori, satuan dasar, harga, status aktif, import awal (bila dibutuhkan pilot).
- Stok awal per outlet dan riwayat perubahan stok.
- Metode pembayaran dan konfigurasi printer/bridge per register.

### Siklus kasir
1. Login → pilih outlet/register → buka shift dengan modal kas.
2. Scan barcode HID atau cari produk → cart → qty/harga/diskon sesuai permission.
3. Checkout online: server memvalidasi stok/harga/status shift dan pembayaran sesuai metode.
4. Finalisasi secara atomik/idempotent: sales, sales items, payment record, dan stock movements konsisten.
5. Cetak struk melalui Device Bridge; cash drawer dapat dibuka sesuai aturan pembayaran tunai.
6. Retur merujuk transaksi asli, dengan kebijakan akses dan audit; jangan menghapus transaksi yang sudah final.
7. Tutup shift: hitung kas fisik, selisih, rekonsiliasi dan laporan harian.

### Laporan minimal
Omzet per hari/outlet/register/kasir, metode pembayaran, transaksi/retur, produk terlaris, stok outlet, laporan shift, dan selisih kas.

### Pembayaran MVP
Tunai, pencatatan pembayaran transfer/kartu/EDC eksternal dan QRIS statis **setelah kasir memverifikasi pembayaran dari kanal merchant resmi**. Integrasi QRIS dinamis dan konfirmasi otomatis hanya melalui penyedia pembayaran resmi pada fase lanjutan; jangan menyamakan pencatatan metode pembayaran dengan konfirmasi otomatis.

## 6. Device Bridge: wajib dalam MVP

| Perangkat | Cakupan awal | Mekanisme |
| --- | --- | --- |
| Scanner barcode USB/Bluetooth HID | Wajib | Input keyboard langsung ke browser; bridge tidak wajib |
| Printer struk thermal 58/80 mm | Wajib | Cetak otomatis via bridge dengan daftar model teruji |
| Cash drawer kompatibel | Wajib | Perintah melalui printer/controller dengan otorisasi |
| Printer label barcode | Wajib | Layout SKU/nama/harga/barcode via bridge |
| Printer jaringan | Uji kompatibilitas | Bergantung model/protokol dan topologi jaringan |
| Timbangan, customer display, EDC otomatis | Tidak dalam MVP | Discovery setelah pilot |

**Fungsi bridge:** instalasi/pairing dengan identitas register, pilih printer, test print, test drawer, kirim job cetak, tampilkan status perangkat, simpan log teknis. Bridge **bukan** server penjualan atau sumber data transaksi; tidak boleh menyimpan transaksi offline untuk kemudian dijual saat koneksi pulih.

**Keamanan bridge:** hanya menerima origin/perintah sah, pairing dan otorisasi register, validasi command payload, pembatasan akses jaringan lokal, proteksi terhadap situs lain, dan audit operasi sensitif. Opsi implementasi pihak ketiga (mis. print bridge) perlu evaluasi lisensi/kompatibilitas sebelum dipilih.

**Referensi perangkat awal:** laptop Windows + scanner USB HID + printer thermal 80 mm + cash drawer. Tablet Android menjadi target uji responsivitas dan bridge melalui perangkat pendamping lokal. Tidak menjamin semua kombinasi tablet/printer kompatibel tanpa pengujian.

## 7. Ketentuan online-only dan penanganan kegagalan

- Jika internet/server tidak tersedia, kasir **tidak bisa memfinalisasi transaksi**. UI menampilkan status koneksi.
- Jika respons checkout hilang, query status memakai ID transaksi/request yang sama sebelum retry; cegah double-charge/double-sale.
- Jika transaksi sudah final tetapi printer gagal, transaksi tetap sah dan struk dapat dicetak ulang dari transaksi yang sama.
- Jika bridge tidak tersedia, kebijakan outlet menentukan apakah struk digital/manual diperbolehkan; jangan memfinalisasi pembayaran dua kali.
- Kegagalan membuka cash drawer tidak memengaruhi keabsahan transaksi; tampilkan peringatan dan simpan log.
- Gunakan server-side authorization, nomor penjualan unik, idempotency key, audit log, atomic write, dan metode rekonsiliasi stok.

## 8. Integrasi Finlite lain (opsional)

- **Accounting:** sinkronkan data penjualan dan pembayaran ke domain keuangan; tetapkan mapping company, akun, pajak, SKU, metode pembayaran, retur, HPP. Pilih detail sumber transaksi dengan opsi posting rekap yang dapat direkonsiliasi.
- **WMS:** mapping SKU/lokasi/gudang dan alur stok; hindari dua pihak menjadi authoritative atas quantity yang sama.
- **CRM:** mapping customer/loyalty saat disetujui.
- Membeli dua produk **tidak otomatis** menggabungkan master produk, pelanggan atau stok. Perlu aktivasi, mapping, permission, dan audit.
- Jangan menulis langsung ke database aplikasi lain. Gunakan API/event, idempotency, retries, dan reconciliation.

## 9. Roadmap usulan (belum ada jadwal/komitmen)

- **Fase 0 — Discovery:** wawancara calon toko minimarket, ATK, koperasi; validasi SKU, transaksi, SOP kasir, perangkat, metode bayar.
- **Fase 1 — Fondasi:** organisasi/entitlement, role, outlet/register, katalog, harga, stok dan konvensi transaksi.
- **Fase 2 — Core cashier online:** shift, scan/cart, checkout, pembayaran, retur, ledger stok, audit, laporan dasar.
- **Fase 3 — Device Bridge MVP:** pairing, printer struk, printer label, cash drawer, tes hardware, fallback dan keamanan. Pengerjaan dapat paralel dengan fase 2, tetapi **wajib selesai sebelum MVP dinyatakan siap**.
- **Fase 4 — Pilot toko:** uji 2–3 toko dan perangkat referensi, koreksi workflow, kecepatan, keandalan dan laporan.
- **Fase 5 — Ekspansi:** multi-outlet lanjut, variant/multi-satuan, promo, integrasi Accounting/WMS/CRM dan hardware tambahan menurut validasi.

## 10. Kriteria penerimaan MVP

- Tidak ada transaksi final ganda akibat retry, klik ganda, atau respons jaringan hilang.
- Sale/payment/stock movement selalu dapat diaudit dan direkonsiliasi.
- Checkout online diblokir ketika tidak bisa mendapat konfirmasi server.
- Role kasir tidak dapat mengakses outlet atau diskon di luar izin.
- Shift tunai dan selisih kas dapat dilacak.
- Printer struk, label, dan cash drawer diuji pada daftar hardware referensi.
- Cetak ulang tidak membuat transaksi baru; kegagalan perangkat tidak merusak data transaksi.
- Pengguna POS standalone dapat menyelesaikan siklus toko tanpa Accounting.

## 11. Keputusan terbuka

- Bahasa/stack Device Bridge, lisensi, distribusi/update, dukungan OS dan printer yang disertifikasi.
- Detail tax/discount/rounding, minimum stok dan retur.
- Scope satuan/varian, multi-outlet, procurement stok awal dalam MVP.
- Format penomoran struk dan laporan fiskal sesuai kebutuhan segmen.
- Aturan pembayaran non-tunai manual, verifikasi dan rekonsiliasi.
- Harga paket dan batas register/outlet/seat.
- Pilot, metrik performa, SLA dan target perangkat final.

**Batas eksplisit:** tidak membangun restoran, kitchen, manajemen meja, resep, atau workflow F&B pada fase awal.
