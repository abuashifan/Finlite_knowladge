# 10 — Finlite Gudang: riset kebutuhan dan fitur

> **STATUS: RISET DAN USULAN, BELUM DISETUJUI.** Dibuat 14 November 2026. Nama
> "Finlite Gudang" sementara (di dokumen lama disebut WMS). Rencana kerja per fase
> ada di [11-finlite-gudang-rencana-fase.md](11-finlite-gudang-rencana-fase.md).

## 1. Cara membaca riset ini

Riset dilakukan lewat pencarian web (14 November 2026) dan membaca kode Finlite
yang ada. **Hampir semua sumber adalah blog vendor perangkat lunak**, jadi
klaimnya dipakai sebagai gambaran pola fitur, bukan bukti. Tidak ditemukan data
pasar independen untuk gudang UKM Indonesia, harga paket vendor lokal, maupun
patokan angka kesalahan picking yang bisa dipercaya. Hal-hal itu harus dicari
lewat wawancara (bagian 8), bukan dari internet.

## 2. Apa yang sudah ada di Finlite

| Sudah ada | Di mana | Catatan untuk Gudang |
| --- | --- | --- |
| Multi-gudang, mutasi stok, penyesuaian, opname, nilai persediaan (rata-rata), laporan stok | Modul Inventory di Finlite Accounting | Hanya tingkat gudang. **Tidak ada** bin/rak, batch/lot, tanggal kedaluwarsa, serial, putaway, picking, reservasi, atau transfer dua langkah |
| Stok satu outlet, stok masuk, opname, modal rata-rata | Finlite Kasir (tenant `pos`) | Stok Kasir berdiri sendiri, tidak tahu gudang |
| Dimensi produk pada paket, langganan, tenant, izin; pola jembatan idempoten ke Accounting | Fondasi Fase 0, 5 Kasir | **Bisa dipakai ulang** untuk produk ketiga |
| Pola mobile-first, PWA, scan barcode kamera, impor Excel, log aktivitas, pemantauan error | Finlite Kasir | Bisa disalin sebagai kerangka |

Artinya: Finlite Gudang bukan membangun inventaris dari nol. Nilainya ada di
**lapisan fisik** yang belum dimiliki: lokasi, kedaluwarsa, alur kerja
penerimaan dan pengeluaran dengan scan, serta kendali selisih.

## 3. Inventaris vs WMS: kapan UKM butuh gudang

Pembeda yang konsisten di sumber: sistem inventaris menjawab "berapa stok dan
berapa nilainya", WMS menjawab "barangnya di mana dan siapa harus mengambil apa".
Lokasi di dalam gudang (zona, rak, bin) dan alur terarah (penerimaan, putaway,
picking) adalah ciri WMS.

- Pelacakan lokasi dasar dinilai berguna untuk usaha sekitar 6-50 karyawan;
  fitur gudang penuh jarang perlu untuk usaha mikro ([Finale Inventory](https://www.finaleinventory.com/?p=13232), [Linnworks](https://www.linnworks.com/blog/warehouse-management-inventory-management/)).
- Uji sederhana: **apakah staf harus diarahkan ke bin tertentu** untuk
  menaruh dan mengambil? Kalau barang muat di beberapa rak dan bisa dicari dengan
  mata, inventaris cukup.
- Banyak bisnis yang tumbuh memakai keduanya.

**Implikasi produk:** Finlite Gudang harus berguna di level "inventaris plus
lokasi" (MVP) dan baru tumbuh ke alur terarah. Jangan memaksa gudang kecil
memakai konsep zona dan wave sejak hari pertama.

## 4. Masalah nyata pengguna (gambaran, perlu dikonfirmasi lewat wawancara)

Dari sumber berbahasa Indonesia (artikel vendor dan skripsi): pencatatan manual
di kertas atau Excel rawan salah; data stok terpisah antara tim gudang dan
akuntansi; stok opname manual lama dan butuh banyak tenaga; selisih stok sering
berasal dari **pengeluaran barang tanpa catatan resmi** dan lemahnya disiplin
pencatatan. Satu studi menyebut selisih sampai 11% tanpa barcode
([HashMicro](https://www.hashmicro.com/id/blog/inventory-discrepancy/), [Jurnal.id](https://www.jurnal.id/id/blog/manajemen-stok-gudang/)).
Sumber tidak membahas surat jalan atau transfer antar gudang UKM secara khusus,
jadi bagian itu **hipotesis** dari pengalaman Finlite.

Masalah yang dijawab Finlite Gudang:
1. Barang keluar masuk tanpa dokumen, sehingga stok tidak bisa dipercaya.
2. Tidak tahu barang ada di rak mana, sehingga lama mencari dan salah ambil.
3. Barang kedaluwarsa atau menumpuk tanpa ketahuan (distributor makanan, obat, kosmetik).
4. Transfer antar gudang atau ke toko hilang di jalan tanpa jejak.
5. Opname tahunan yang menghentikan operasi dan hasilnya tidak ditelusuri.
6. Stok gudang dan stok toko/online tidak sinkron.

## 5. Katalog fitur dan prioritas

Prioritas: **W** = wajib untuk produk layak dijual (MVP), **S** = sebaiknya ada
sebelum rilis umum, **N** = nanti, setelah ada permintaan nyata. Pola fitur diambil
dari panduan WMS ([NetSuite](https://www.netsuite.com/portal/products/erp/warehouse-fulfillment/wms.shtml), [Zoho](https://www.zoho.com/inventory/academy/warehouse-management/essential-wms-features.html), [Cleverence](https://www.cleverence.com/amp/articles/business-blogs/what-is-wms-2847/), [Epicor via ERP Research](https://erpresearch.com/erp/epicor-kinetic/warehouse-management)) dan vendor lokal
([Jubelio](https://jubelio.com/en/product/omnichannel/warehouse-system/), [Ginee](https://ginee.com/id/help/fefo-strategy-in-wms/)).

### A. Master data
| Fitur | Prio | Catatan |
| --- | --- | --- |
| Barang: kode/SKU, barcode (banyak per barang), kategori, satuan dasar, foto | W | Impor Excel; pola sama Kasir |
| Gudang dan lokasi hierarki sederhana: gudang > zona > rak > bin | W | Bin opsional; gudang tanpa bin tetap jalan |
| Kapasitas dan jenis lokasi (simpan, terima, karantina, rusak) | S | Lokasi "rusak" dan "karantina" mencegah barang jelek terambil |
| Multi-satuan (dus, pak, pcs) dengan konversi | S | Sering diminta distributor; satuan ganda Kasir masih menunggu uji lapangan |
| Pemasok dan pelanggan/tujuan | W | Ringan: nama, kontak, alamat kirim |
| Varian (warna, ukuran) | N | Tambah setelah ada pengguna yang butuh |

### B. Penerimaan (inbound)
| Fitur | Prio | Catatan |
| --- | --- | --- |
| Penerimaan barang dengan atau tanpa PO, cek jumlah vs dokumen | W | Selisih jumlah dicatat, bukan ditolak |
| Scan barcode saat terima (kamera HP) | W | Lihat bagian 6 |
| Putaway: lokasi tujuan, usulan lokasi | W (manual) / S (usulan) | Usulan berdasar kategori, ruang kosong, atau barang yang sama sudah ada di bin |
| Penerimaan sebagian dan bertahap | W | |
| Batch/lot dan tanggal kedaluwarsa saat terima | S | Lihat bagian D |
| Foto bukti dan catatan kondisi (rusak/kurang) | S | |

### C. Pengeluaran (outbound)
| Fitur | Prio | Catatan |
| --- | --- | --- |
| Dokumen pengeluaran/surat jalan dengan nomor, tujuan, daftar barang | W | Jawaban atas masalah "keluar tanpa catatan" |
| Daftar ambil (pick list) berurutan menurut lokasi | S | Sumber: picking terarah mengurangi salah ambil |
| Pick berbasis scan dan verifikasi jumlah | S | |
| Strategi picking: per pesanan, batch, per zona, wave | N | Hanya untuk volume besar |
| Packing, berat, kemasan, cetak label pengiriman | N | Bergantung kurir dan marketplace |
| Reservasi stok: tersedia = di tangan - dipesan | S | Wajib sebelum ada pesanan keluar dari beberapa sumber |
| Retur masuk dan ke pemasok | S | |

### D. Kendali stok
| Fitur | Prio | Catatan |
| --- | --- | --- |
| Kartu stok per barang/lokasi dengan seluruh mutasi | W | |
| Transfer antar gudang/lokasi dua langkah: kirim, dalam perjalanan, terima | W | Selisih saat terima dicatat; barang tidak "hilang" selama transit |
| Penyesuaian dengan alasan dan persetujuan | W | |
| Opname penuh dan cycle count; jadwal berdasar kelas ABC; hitung buta | S | ABC: kelas A paling sering dihitung ([Cleverence](https://www.cleverence.com/amp/articles/for-business/inventory-management-best-practices-4837/)) |
| Batch/lot, FEFO (kedaluwarsa terdekat keluar dulu), peringatan kedaluwarsa | S | Lazim di platform Indonesia; barcode GS1-128 membawa lot dan tanggal ([Cleverence](https://www.cleverence.com/articles/business-blogs/batch-expiry-tracking-4729/)) |
| Telusur batch maju-mundur (recall) | S | |
| Serial number | N | Untuk elektronik; mahal di UI |
| Stok minimum/maksimum dan saran pembelian | S | Titik pesan = permintaan selama lead time + stok pengaman; pengaturan basi adalah risiko utama |
| Stok mati dan umur stok | S | Sudah ada di Accounting; pakai ulang rumusnya |

### E. Perangkat dan label
| Fitur | Prio | Catatan |
| --- | --- | --- |
| Aplikasi HP: scan kamera, daftar tugas | W | |
| Pemindai Bluetooth/HID | S | Untuk volume tinggi |
| Cetak label barcode barang dan lokasi | S | Jangan menunggu: tanpa label bin, lokasi tidak bisa dipindai |
| Handheld Android khusus | N | Hanya bila pelanggan membeli |

### F. Laporan, kendali, dan keamanan
| Fitur | Prio | Catatan |
| --- | --- | --- |
| Stok per gudang/lokasi/batch, ekspor Excel | W | |
| Pergerakan, barang lambat, barang akan kedaluwarsa | S | |
| KPI: akurasi stok, waktu terima-ke-simpan, pesanan tepat waktu, tingkat salah ambil | N | Daftar KPI umum di sumber; targetnya harus dari data pilot sendiri |
| Izin per fitur dan per gudang (staf gudang A tidak melihat gudang B) | W | Mengikuti keputusan akses Finlite |
| Log aktivitas semua perubahan stok | W | Pola Kasir 4b |

### G. Integrasi (opsional, produk tetap lengkap tanpa produk lain)
| Fitur | Prio | Catatan |
| --- | --- | --- |
| Gudang ke Kasir: transfer ke outlet menjadi stok masuk di Kasir | S | Nilai jual terbesar bagi pelanggan yang sudah memakai Kasir |
| Gudang ke Accounting: jurnal penerimaan, selisih, transfer antar entitas | S | Pola jembatan idempoten Kasir; satu entitas tidak perlu jurnal untuk transfer |
| Marketplace (Shopee, Tokopedia, dan sejenisnya) dan kurir | N | Ketergantungan API pihak ketiga; hanya bila pelanggan e-commerce menuntut |
| API publik | N | |

## 6. Perangkat: kamera HP atau pemindai khusus

Pemindai khusus kelas industri berharga kira-kira US$1.500-2.500 per unit,
pemindai Bluetooth untuk HP US$150-500 menurut sumber vendor
([Cleverence](https://www.cleverence.com/amp/articles/business-blogs/mobile-scanner-for-business-owners-4827/), [Scandit](https://www.scandit.com/considering-replacing-dedicated-scanners-with-mobile-devices/)). Vendor perangkat lunak
kamera mengklaim kamera HP setara; sumber yang lebih skeptis mengingatkan lelah
tangan dan baterai pada ratusan scan per hari
([Netum](https://www.netum.net/de/blogs/technology-explainers/can-phones-replace-a-2d-barcode-scanner), [RFgen](https://rfgen.com/?p=2543)). Tidak ada data independen untuk gudang kecil.

**Keputusan yang diusulkan:** mulai dari **kamera HP** (biaya nol dan pola sudah
ada di Kasir), dukung pemindai Bluetooth/HID sebagai tambahan, dan uji dengan label
asli pelanggan sebelum menjanjikan kecepatan. Handheld khusus bukan target awal.

## 7. Posisi di pasar

Pesaing yang disebut sumber (harga indikatif, wajib dicek di situs vendor): Zoho
Inventory (kuat untuk jual dan kirim, harga per organisasi), Odoo Inventory (bagian
ERP luas; edisi komunitas gratis, edisi online sekitar US$31/pengguna/bulan),
Sortly (sederhana, mobile-first, hanya inventaris), serta vendor lokal Jubelio
dan Ginee (fokus omnichannel/marketplace dengan FEFO dan picking)
([Dupple](https://dupple.com/learn/best-warehouse-management-software), [Ecosire](https://ecosire.com/blog/odoo-inventory-vs-zoho-inventory-2026-comparison), [Jubelio](https://jubelio.com/en/product/omnichannel/warehouse-system/)).

Peluang Finlite yang masuk akal (hipotesis):
- **Sederhana dan bahasa Indonesia untuk gudang kecil-menengah** yang sekarang memakai Excel.
- **Satu keluarga produk:** Kasir untuk toko, Gudang untuk stok pusat, Accounting untuk pembukuan, masing-masing bisa dibeli sendiri.
- **Harga dan alur yang tidak membebani**: sebanding dengan Kasir.

Yang bukan peluang awal: bersaing di omnichannel marketplace melawan vendor yang
sudah mapan, dan WMS otomasi besar (konveyor, AGV).

## 8. Yang harus dikonfirmasi sebelum membangun (wawancara 5-8 gudang)

Pertanyaan untuk gudang nyata, termasuk gudang milik pemilik produk:
1. Berapa SKU, berapa lokasi/rak, berapa orang, berapa transaksi keluar-masuk per hari?
2. Barang apa yang punya kedaluwarsa atau nomor batch? Apakah wajib telusur batch?
3. Siapa yang menerima barang, siapa yang mengeluarkan, siapa yang menyetujui selisih?
4. Dokumen apa yang dipakai hari ini (surat jalan, DO, BAST, faktur pemasok)? Bentuk dan nomornya?
5. Apakah ada transfer antar gudang atau ke toko? Berapa lama barang dalam perjalanan?
6. Seberapa sering opname, dan bagaimana menyelesaikan selisih sekarang?
7. Perangkat: HP Android, iPhone, laptop, pemindai? Sinyal di gudang bagaimana (**online-only cukup?**).
8. Sistem yang dipakai sekarang (Excel, Accurate, Jurnal, lainnya) dan apa yang paling dikeluhkan?
9. Bersedia membayar berapa per bulan dan untuk apa?

Hasil wawancara menentukan prioritas bagian 5, terutama batch/FEFO, picking
terarah, dan multi-satuan.

## 9. Keputusan terbuka untuk pemilik produk

| # | Pertanyaan | Usulan bawaan |
| --- | --- | --- |
| 1 | Nama produk | Finlite Gudang |
| 2 | Segmen awal | Gudang/distributor kecil-menengah dan pemilik Kasir yang punya gudang pusat |
| 3 | Online-only seperti Kasir? | Ya; antrean ulang singkat seperti Kasir, bukan offline penuh |
| 4 | Batch/kedaluwarsa masuk MVP atau Fase 2? | Fase 2, kecuali wawancara menunjukkan sebagian besar target menjual makanan/obat |
| 5 | Siapa pemilik angka stok bila Gudang dan Accounting tersambung? | Gudang untuk kuantitas fisik; Accounting untuk nilai. Satu sumber per angka |
| 6 | Siapa pemilik stok outlet bila Gudang dan Kasir tersambung? | Kasir untuk outlet; Gudang untuk gudang; pindah lewat transfer |
| 7 | Cetak label di MVP? | Fase 2, bersama pemindaian bin |
| 8 | Harga paket | Setelah wawancara, mengikuti pita jumlah pengguna atau gudang |

## 10. Risiko

1. **Terlalu berat untuk gudang kecil.** Mitigasi: bin dan alur terarah opsional.
2. **Dua pihak menguasai angka stok yang sama** saat tersambung ke Kasir/Accounting. Mitigasi: aturan pemilik per angka dan transfer sebagai satu-satunya jalan pindah.
3. **Kecepatan scan kamera** tidak cukup untuk volume tinggi. Mitigasi: uji label asli, dukung pemindai Bluetooth.
4. **Mengejar pesaing omnichannel** menyedot waktu. Mitigasi: integrasi marketplace hanya atas permintaan nyata.
5. **Data pilot nyata tidak boleh masuk repositori ini**; simpan di luar atau anonimkan.

## Sumber

Semua diakses 14 November 2026; sebagian besar blog vendor.
[NetSuite WMS](https://www.netsuite.com/portal/products/erp/warehouse-fulfillment/wms.shtml) ·
[Zoho: fitur WMS](https://www.zoho.com/inventory/academy/warehouse-management/essential-wms-features.html) ·
[Cleverence: apa itu WMS](https://www.cleverence.com/amp/articles/business-blogs/what-is-wms-2847/) ·
[ERP Research: Epicor](https://erpresearch.com/erp/epicor-kinetic/warehouse-management) ·
[Racklify](https://racklify.com/encyclopedia/what-is-a-warehouse-management-system-core-features-and-benefits/) ·
[Jubelio](https://jubelio.com/en/product/omnichannel/warehouse-system/) ·
[Ginee: FEFO](https://ginee.com/id/help/fefo-strategy-in-wms/) ·
[Cleverence: batch dan kedaluwarsa](https://www.cleverence.com/articles/business-blogs/batch-expiry-tracking-4729/) ·
[Finale Inventory](https://www.finaleinventory.com/?p=13232) ·
[Linnworks](https://www.linnworks.com/blog/warehouse-management-inventory-management/) ·
[Cleverence: praktik terbaik inventaris](https://www.cleverence.com/amp/articles/for-business/inventory-management-best-practices-4837/) ·
[Cleverence: pemindai seluler](https://www.cleverence.com/amp/articles/business-blogs/mobile-scanner-for-business-owners-4827/) ·
[Scandit](https://www.scandit.com/considering-replacing-dedicated-scanners-with-mobile-devices/) ·
[RFgen](https://rfgen.com/?p=2543) ·
[Netum](https://www.netum.net/de/blogs/technology-explainers/can-phones-replace-a-2d-barcode-scanner) ·
[HashMicro: selisih stok](https://www.hashmicro.com/id/blog/inventory-discrepancy/) ·
[Jurnal.id: manajemen stok](https://www.jurnal.id/id/blog/manajemen-stok-gudang/) ·
[Dupple](https://dupple.com/learn/best-warehouse-management-software) ·
[Ecosire](https://ecosire.com/blog/odoo-inventory-vs-zoho-inventory-2026-comparison)
