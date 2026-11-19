# 11 — Finlite Gudang: rencana pembuatan per fase

> **Status per 19 November 2026.** Implementasi Fase 1 dan Fase 2 sudah digabung ke repositori backend dan frontend. Pengujian penerimaan dijadwalkan pada Fase 6 dengan simulasi, mengikuti [rencana uji simulasi](13-finlite-gudang-rencana-uji-simulasi.md); belum ada hasil penerimaan Fase 2. Tahap implementasi berikutnya Fase 3. Pilot fisik dijadwalkan saat gudang tersedia.
> Dasar kebutuhan dan fitur: [10-finlite-gudang-riset-kebutuhan-dan-fitur.md](10-finlite-gudang-riset-kebutuhan-dan-fitur.md).
> Pola kerja mengikuti [08-finlite-pos-rencana-fase.md](08-finlite-pos-rencana-fase.md), yang sudah terbukti
> untuk Kasir. Ukuran usaha memakai S/M/L (kecil/sedang/besar), **bukan jadwal**.

## Prinsip

1. **Lengkap tanpa produk lain.** Gudang boleh dipakai tanpa Accounting dan tanpa Kasir. Integrasi opsional dan datang belakangan.
2. **Satu pemilik per angka.** Kuantitas fisik gudang dimiliki Gudang; nilai dan jurnal dimiliki Accounting; stok outlet dimiliki Kasir. Barang pindah antar pemilik hanya lewat transfer.
3. **Bin dan alur terarah opsional.** Gudang tanpa lokasi tetap jalan; konsep zona dan wave tidak boleh memaksa gudang kecil.
4. **Setiap perubahan stok punya dokumen.** Tidak ada tombol "ubah stok" tanpa alasan dan jejak.
5. **Mobile-first, online-only.** Kamera HP untuk scan dan antrean ulang singkat saat sinyal putus. Simulasi kehilangan koneksi dan kamera dijalankan pada Fase 6.
6. **Pakai ulang fondasi yang ada:** dimensi produk (paket, langganan, tenant, izin), pola jembatan idempoten, log aktivitas, pemantauan error, PWA.
7. **Data simulasi untuk pengembangan dan pengujian program.** Semua akun, perusahaan, barang, transaksi, hasil hitung dan berkas uji dibuat sintetis. AI sub-agent dan Playwright menjalankan rencana pengujian pada fase akhir.

Fase 0–5 menghasilkan implementasi, dokumentasi kontrak, daftar skenario dan status pekerjaan. Seluruh eksekusi pengujian program, termasuk CI backend, Playwright, keamanan, beban dan rekonsiliasi, dikumpulkan pada Fase 6 sesuai keputusan pemilik. Hasil CI yang sudah ada disimpan sebagai bukti historis versi yang diuji. Penerimaan program menggunakan hasil simulasi pada versi final. Pilot lapangan dijadwalkan tersendiri saat gudang tersedia.

## Ringkasan fase

| Fase | Isi | Ukuran | Syarat masuk |
| --- | --- | --- | --- |
| 0 | Penemuan dan fondasi: wawancara, keputusan terbuka, produk `gudang` di platform | M | Dokumen ini disetujui |
| 1 | MVP inventaris gudang: master, penerimaan, pengeluaran, transfer, kartu stok | L | Fase 0 selesai |
| 2 | Kendali: retur, multi-satuan, opname, batch dan kedaluwarsa, label, saran pembelian | L | Implementasi Fase 1 tersedia |
| 3 | Operasi keluar terarah: reservasi, pick list, packing | L | Fase 2; alur pesanan keluar dipilih pemilik |
| 4 | Jembatan opsional ke Kasir, Accounting dan Project | M | Fase 1-2; kontrak integrasi dan aplikasi tujuan tersedia |
| 5 | Skala dan saluran: pemindai Bluetooth, serial, marketplace, API (atas permintaan) | L | Pilihan kebutuhan oleh pemilik |
| 6 | Pengujian simulasi menyeluruh, kesiapan komersial dan rilis | L | Implementasi fase yang dipilih selesai |

Fase 3 dan 5 mengikuti pilihan kebutuhan pemilik. Fitur yang dipilih dicantumkan dalam cakupan versi sebelum kampanye pengujian Fase 6.

---

## Revisi prioritas, 18 November 2026

**Keputusan pemilik.** Revisi roadmap dan rencana pengujian disetujui untuk disusun. Pengujian memakai simulasi dan dijalankan pada fase akhir. Perbandingan dengan [riset audit ekosistem Gudang](https://chatgpt.com/s/t_6afd86cec344819183704db0bf9e9bc2) dipakai untuk menentukan kendali dasar dan urutan fitur. Finlite masih dalam pengembangan dan memakai PostgreSQL Neon.

Urutan pengembangan setelah implementasi Fase 1:

1. **Lengkapi kendali dasar Fase 1.** Jenis lokasi karantina/rusak diikuti pembatasan pengeluaran dan pemindahan dengan otorisasi yang jelas. Koreksi dokumen terposting memakai dokumen balik yang merujuk dokumen awal, alasan, aktor dan idempotensi. Catat ketersediaan setiap kemampuan berdasarkan kode dan kontrak. Pengujian penerimaannya masuk kampanye Fase 6.
2. **Kerjakan retur dan multi-satuan di awal Fase 2.** Retur pelanggan/pemasok merujuk dokumen asal dan kondisi barang. Konversi satuan menyimpan jumlah input, faktor konversi pada dokumen, dan jumlah dasar agar perubahan master dapat ditelusuri. Sesudahnya kerjakan opname, kendali batch, label dan kebutuhan stok lainnya.
3. **Rinci kontrak ekosistem sebelum membangun jembatan Fase 4.** Catat pemilik kuantitas, nilai dan biaya proyek, pemetaan barang, identitas sumber dokumen, idempotensi, koreksi, serta rekonsiliasi. Alur Project membedakan permintaan, pengiriman, penerimaan, pemakaian dan pengembalian material. Accounting menggunakan rata-rata sesuai rencana. FIFO memerlukan keputusan metode biaya tersendiri.
4. **Jalankan kampanye simulasi pada Fase 6.** Pasangkan versi backend dan frontend, siapkan akun pemilik/staf/pemberi persetujuan, lalu jalankan seluruh urutan dari data awal sampai ekspor laporan melalui AI sub-agent dan Playwright. Bukti delapan skenario CI yang sudah tersedia menjadi referensi awal. Cakupan lengkap, angka pembanding, pembagian agen dan kriteria kelulusan mengikuti dokumen 13.

Pilot fisik tujuh hari ditunda sampai gudang tersedia. Penyelesaian pengembangan dan penerimaan program mengikuti simulasi Fase 6. Pengujian pemulihan memakai database uji atau branch Neon khusus dengan data sintetis.

---

## Fase 0 — Penemuan dan fondasi

**Tujuan:** memastikan kita membangun yang dibutuhkan, dan menyiapkan Gudang
sebagai produk ketiga di platform.

Penemuan (tanpa kode):
- **Tanpa wawancara** (tidak ada gudang yang bisa diwawancarai): riset meja Indonesia selesai (dokumen 10 bagian 2b). Skenario dokumen dan peran agen AI disiapkan untuk simulasi Fase 6.
- Susun contoh dokumen (surat jalan, DO, bukti penerimaan, form opname) dan data barang rekaan untuk uji. Data nyata **tidak** masuk repositori.
- Putuskan 8 keputusan terbuka di dokumen 10 bagian 9, terutama: batch di MVP atau Fase 2, online-only, dan pemilik angka stok bila tersambung.
- Tulis "definisi siap dibangun" untuk Fase 1: pemilik domain, user story, matriks izin, diagram status dokumen, skenario gagal, tes penerimaan (dokumen 04).

Fondasi (kode kecil):
- Tambah `gudang` sebagai produk: paket, langganan, tenant, dan izin per produk (pola yang dipakai untuk `pos`).
- Tenant schema `gudang` per perusahaan saat diaktifkan, dengan migrasi terpisah (`tenant_gudang`).
- Paket awal: Gudang Gratis (satu gudang, batas barang) dan Gudang (batas pengguna), dengan masa coba dan mode hanya-baca saat habis, sama seperti Kasir.
- Kerangka aplikasi: repositori frontend baru (React, Vite, TypeScript, Tailwind, TanStack Query) dari kerangka Kasir, PWA, halaman masuk, pilih perusahaan.

**Kriteria selesai:** keputusan terbuka terjawab dan tercatat (usulan bawaan dipakai); riset meja selesai dan celahnya didaftar; pemilik dapat mendaftar, mengaktifkan produk Gudang, dan melihat halaman kosong yang terkunci langganan.

**Status (15 November 2026):** Fase 0 dimulai. Fondasi backend selesai (laravel_backend#30: produk `gudang`, paket, izin, aktivasi). Panduan wawancara, daftar keputusan, dan draf spesifikasi Fase 1 ada di [12](12-finlite-gudang-fase0-wawancara-dan-spesifikasi-awal.md). Wawancara **dibatalkan** (15 November 2026); diganti riset meja dan pilot. Frontend tersedia di repo `finlite-gudang` sejak 17 November. Harga final dan calon pengguna pilot masih terbuka.

**Risiko:** kesesuaian dengan pasar masih perlu dipelajari saat pengguna nyata tersedia. Pengembangan saat ini mengikuti keputusan pemilik, riset meja dan skenario sintetis yang terdokumentasi.

---

## Fase 1 — MVP inventaris gudang

**Implementasi Fase 1 selesai pada 18 November 2026.** Fondasi inventaris tersedia melalui backend #33 dan aplikasi #1. Pelengkap kondisi dan koreksi sudah digabung melalui [backend #34](https://github.com/abuashifan/laravel_backend/pull/34) dan [aplikasi #2](https://github.com/abuashifan/finlite-gudang/pull/2). Pengeluaran normal menegakkan kondisi lokasi. Dokumen PLS melepas barang dari karantina/rusak dengan alasan, izin persetujuan dan akses kedua lokasi. Dokumen KOR membalik mutasi bersih aktual, menyimpan referensi serta alasan dan membuka kembali sisa penerimaan bertahap bila bukti kirimannya dikoreksi. Laporan lokasi dan pergerakan memuat kondisi barang. Eksekusi tes program untuk pelengkap ini dijadwalkan pada Fase 6. Commit pelengkap memakai penanda penundaan CI sesuai keputusan pemilik.

**Bukti CI historis, 18 November 2026, sebelum revisi jadwal pengujian.** [CI backend](https://github.com/abuashifan/laravel_backend/actions/runs/44238190640) lulus pada commit `2a4660633cd401525cf0bc169f440af1d1e64fbf`, termasuk PostgreSQL, pengeluaran bersamaan, serta beban 5.000 barang dan 3.500 mutasi sintetis. Waktu baca tertinggi pada endpoint yang diukur adalah 50,4 ms di runner CI. [CI aplikasi](https://github.com/abuashifan/finlite-gudang/actions/runs/44292130240) lulus pada commit `c1029cef517194ac60fe4636641afcf0084c5afd` dengan lint, build, dan delapan skenario Playwright ukuran HP. Skenario mencakup penerimaan ulang setelah respons hilang, impor saldo awal, surat jalan, penerimaan bertahap, saldo transfer setelah penyelesaian selisih, putaway, persetujuan penyesuaian, dan scan kamera simulasi. Pengujian browser memakai akun pemilik. Izin staf diuji di backend. Kampanye penerimaan versi final dijadwalkan pada Fase 6 dengan simulasi. Evaluasi kamera fisik mengikuti ketersediaan perangkat dan gudang pada tahap penggunaan nyata.

**Implementasi, 18 November 2026.** PR Fase 1 mencakup master barang, foto/barcode, mitra, banyak gudang dan lokasi, penerimaan langsung atau bertahap dengan bukti tiap kiriman, surat jalan, putaway, transfer dua langkah, penyelesaian selisih, serta persetujuan penyesuaian. Aplikasi menyediakan scan kamera, akses per gudang, pencarian, laporan, log aktivitas, ekspor dan pratinjau impor Excel/CSV, pendaftaran dan masa coba. Status pengiriman mengikuti [PR backend #33](https://github.com/abuashifan/laravel_backend/pull/33) dan [PR aplikasi #1](https://github.com/abuashifan/finlite-gudang/pull/1).

**Hubungan dengan Finlite Project.** Permintaan atau pemakaian material proyek kelak dapat merujuk dokumen fisik lewat perusahaan, produk, jenis dokumen, dan UUID. Gudang memiliki kuantitas fisik. Penerimaan barang sendiri belum membuktikan material dipakai proyek. Pembebanan proyek dan jurnal mengikuti dokumen pemakaian serta kontrak integrasi antaraplikasi. Identitas proyek, otorisasi, dan pemetaan dokumen disepakati saat alur itu dibangun.

**Tujuan:** gudang kecil-menengah berhenti mencatat di kertas dan Excel; semua barang masuk, keluar, dan pindah punya dokumen, dan stok per gudang/lokasi bisa dipercaya.

Backend (tenant `gudang`):
- Master: barang (SKU, banyak barcode, kategori, satuan dasar, foto), pemasok, tujuan/pelanggan, gudang, lokasi hierarki opsional (zona > rak > bin) dengan jenis lokasi (simpan, terima, karantina, rusak).
- Buku stok sebagai sumber kebenaran: setiap perubahan lewat satu layanan yang menulis mutasi, saldo per (barang, lokasi), dan log aktivitas dalam satu transaksi. Tidak ada jalan lain mengubah saldo. Saldo tidak boleh negatif kecuali pengaturan mengizinkan.
- Kendali kondisi dan koreksi yang ditambahkan pada revisi 18 November. Barang di karantina/rusak dibatasi dari pengeluaran normal. Perpindahan kondisi memakai tindakan berizin dan jejak audit. Koreksi dokumen terposting merujuk dokumen awal melalui dokumen balik dengan alasan dan pencegahan posting ganda. Implementasi tambahannya dicatat tersendiri dari bukti CI historis di atas.
- Penerimaan: dengan atau tanpa PO sederhana; jumlah diterima vs dokumen, penerimaan sebagian; ke lokasi terima lalu putaway ke bin (manual).
- Pengeluaran: dokumen pengeluaran/surat jalan bernomor, tujuan, daftar barang, status (draf, dikeluarkan, dibatalkan).
- Transfer dua langkah antar gudang/lokasi: kirim, dalam perjalanan, terima; selisih saat terima dicatat dan menunggu keputusan.
- Penyesuaian stok dengan alasan wajib dan persetujuan oleh izin khusus.
- Kartu stok per barang dan per lokasi; laporan stok per gudang, per lokasi, pergerakan, stok menipis (batas minimum per barang); ekspor Excel.
- Impor barang dari Excel dengan pratinjau; impor saldo awal sebagai penerimaan awal.
- Izin per fitur dan per gudang; log aktivitas; kunci idempoten untuk simpan ulang saat sinyal putus; nomor dokumen atomik.

Frontend (HP lebih dulu, tablet/laptop untuk backoffice):
- Beranda tugas: yang perlu diterima, dikeluarkan, transfer menunggu.
- Layar terima, keluarkan, transfer, putaway dengan scan kamera barang dan lokasi.
- Pencarian stok cepat (scan atau ketik) menampilkan "barang ini ada di mana".
- Halaman Bantuan, harga, syarat, privasi (salin dari Kasir).

**Penerimaan program.** Pengujian Fase 1 dijalankan bersama kampanye simulasi pada Fase 6. Rentang tujuh tanggal bisnis dibuat sebagai data sintetis dan dieksekusi dalam satu kampanye. Pilot fisik dijadwalkan saat gudang tersedia.

**Kriteria implementasi selesai:** master, dokumen, izin, buku stok, kendali kondisi dan koreksi tersedia beserta kontrak serta skenario penerimaannya. Pada Fase 6, saldo skenario simulasi harus cocok di dokumen, mutasi, laporan dan ekspor. Target beban tetap satu gudang 5.000 barang dan 500 mutasi per tanggal bisnis selama tujuh tanggal, dengan baca di bawah 250 ms pada kondisi runner yang dicatat.

**Risiko:** buku stok yang bisa diakali; mitigasi: satu pintu tulis dan tes yang mencoba saldo negatif, transaksi serentak, dan simpan ganda (pelajaran nomor kembar di Kasir).

---

## Fase 2 — Kendali stok

**Tujuan:** mengurangi selisih dan barang kedaluwarsa, dan membuat opname tidak menghentikan operasi.

**Implementasi Fase 2 selesai dan digabung pada 19 November 2026:** [backend #35](https://github.com/abuashifan/laravel_backend/pull/35) dan [aplikasi #3](https://github.com/abuashifan/finlite-gudang/pull/3). Backend kontrak `66582bba24436b7e5e7ed12f1b47c9762b04a15b` dipasangkan dalam konfigurasi CI frontend; perubahan aplikasi `abc3e7e58056009f8e94d6c1577d74696d868d66`. Pemeriksaan saat implementasi terbatas pada pembacaan kode, perapihan format dan pemeriksaan whitespace. Belum ada hasil pengujian atau penerimaan Fase 2. Seluruh lint, build, suite backend, Playwright dan PostgreSQL dijalankan pada Fase 6; commit serta merge memakai `[skip ci]` mengikuti keputusan pemilik. Status merge bukan bukti kelulusan atau verifikasi deployment. Pilot fisik menunggu gudang tersedia.

Backend dan frontend:
- Retur pelanggan dan pemasok mendukung sebagian, merujuk dokumen asal dan membatasi kuota tersisa, termasuk batch asal; kondisi dan alasan tercatat. Permintaan ulang idempoten menghasilkan satu efek.
- Multi-satuan memakai jumlah dasar tepat sampai 3 desimal. Dokumen menyimpan snapshot jumlah input, satuan, faktor dan jumlah dasar yang tidak berubah saat master berubah; retry idempoten tidak menggandakan posting.
- Batch dan kedaluwarsa opsional per barang: saldo per batch, alokasi FEFO, karantina dan telusur maju-mundur. Saat pelacakan diaktifkan untuk barang dengan histori, saldo dan mutasi lama dipetakan ke batch `HIST-<id barang>` sebagai karantina untuk ditinjau. Migrasi skema sendiri tidak mengaktifkan pelacakan.
- Opname buta memakai snapshot pada cutoff: input hitung mewakili kondisi pada cutoff dan mutasi setelah cutoff tetap dipertahankan. Selisih lebih dari maksimum 1 satuan atau 10% memerlukan hitung ulang oleh penghitung kedua. Tersedia persetujuan, pembatalan, histori dan dokumen balik.
- ABC dihitung dari volume keluar 90 hari, dapat ditimpa; jadwal A setiap 7 hari, B 30 hari dan C 90 hari.
- Minimum, maksimum dan titik pesan per barang per gudang; saran pembelian memperhitungkan lead time (bawaan 7 hari) dan stok pengaman, dengan waktu perhitungan.
- Laporan kedaluwarsa 30 hari, barang lambat 30 hari, stok mati 90 hari dan akurasi opname; ekspor XLSX lengkap.
- Label barang dan lokasi menghasilkan PDF Code128B ASCII berbasis vektor asli, ukuran dapat diatur 30–150 × 20–100 mm (bawaan 60 × 35 mm); nama ditransliterasi ke ASCII. GS1-128 tetap pilihan kebutuhan berikutnya.
- Aplikasi menyediakan alur retur, satuan, opname, batch, saran, laporan dan label. Perusahaan dan pengguna bersama memakai produk `gudang`. Jembatan Accounting dan Project belum tersedia; referensi lintas produk mendatang memakai UUID dokumen stabil.

**Kriteria implementasi selesai:** kontrak retur, satuan, opname, batch dan layar terkait tersedia. Pada Fase 6, simulasi membuktikan konversi dan retur konsisten, opname dengan transaksi bersamaan memakai snapshot/cut-off yang terdokumentasi, selisih terlacak dan FEFO benar. Gambar barcode sintetis serta kamera simulasi dipakai untuk menguji pembacaan dan penanganan kegagalan.

**Risiko:** UI batch yang membingungkan. Mitigasi melalui tampilan batch untuk barang yang mengaktifkannya dan simulasi peran staf pada Fase 6.

---

## Fase 3 — Operasi keluar terarah (bersyarat)

**Tujuan:** untuk gudang dengan banyak pesanan keluar per hari: kurangi salah ambil dan percepat pengeluaran.

Dikerjakan bila pemilik memilih kebutuhan pesanan keluar. Cakupan yang dipilih masuk matriks pengujian Fase 6.

- Pesanan keluar (permintaan barang): reservasi stok sehingga tersedia = di tangan - dipesan.
- Pick list berurutan menurut lokasi; pick dengan scan dan verifikasi jumlah; kekurangan stok dicatat sebagai short pick.
- Strategi picking: per pesanan lebih dulu; batch dan per zona hanya bila diminta.
- Packing sederhana: daftar kemasan, berat, dan catatan; cetak surat jalan dan label kirim; status kirim.
- Usulan putaway otomatis (kategori, ruang kosong, barang sama di bin).

**Kriteria implementasi selesai:** reservasi, picking dan packing yang dipilih tersedia beserta aturan status dan sisa pesanan. Pada Fase 6, pesanan sintetis melewati pick-pack-kirim, pengiriman sebagian, pembatalan dan pelepasan reservasi dengan saldo yang sesuai.

---

## Fase 4 — Jembatan opsional

**Tujuan:** pelanggan yang memakai lebih dari satu produk Finlite tidak mencatat dua kali. Pola dan aturan sama dengan jembatan Kasir ke Accounting (Fase 5 Kasir): arus satu arah, pesan idempoten, status kiriman, kirim ulang, periode terkunci ditahan.

**4a. Gudang ke Kasir** (nilai terbesar bagi pemilik Kasir):
- Transfer dari gudang ke outlet menjadi stok masuk di Kasir (barang, jumlah, modal) lewat pesan idempoten.
- Pemetaan barang Gudang ke produk Kasir lewat SKU/barcode; impor produk Kasir dari Gudang sekali jalan (pola "ambil produk dari Akuntansi").
- Aturan pemilik angka: gudang memiliki stok gudang, Kasir memiliki stok outlet; selisih saat terima dilaporkan balik sebagai exception, tidak mengubah stok pihak lain diam-diam.

**4b. Gudang ke Accounting:**
- Jurnal penerimaan (persediaan lawan hutang atau barang diterima belum ditagih), selisih opname (persediaan lawan selisih persediaan), dan transfer antar entitas. Transfer di dalam satu entitas tidak dijurnal.
- Pemetaan akun dengan usulan dari kode template; opsi kirim nilai; tombol kirim ulang; rekonsiliasi nilai persediaan Accounting vs stok Gudang x modal.
- Aturan nilai: Accounting memegang valuation (rata-rata); Gudang mengirim kuantitas dan harga terima.

**4c. Gudang dan Finlite Project:**
- Permintaan material proyek merujuk perusahaan, proyek, barang dan dokumen sumber. Pisahkan jumlah diminta, dikirim, diterima, dipakai dan dikembalikan.
- Perpindahan material dan pemakaian memakai UUID dokumen stabil, pemetaan barang serta izin lintas produk yang eksplisit. Project memiliki catatan kebutuhan/pemakaian dan biaya proyek. Gudang memiliki mutasi fisik. Accounting memiliki valuasi dan jurnal.
- Tetapkan waktu pengakuan biaya proyek, lokasi penyimpanan material proyek, pengembalian sisa dan perlakuan selisih. Perubahan status atau pengiriman ulang pesan menghasilkan dampak yang dapat direkonsiliasi.
- Kontrak dan pemetaan disiapkan sebelum implementasi jembatan. Pengaktifan integrasi mengikuti ketersediaan modul Project dan cakupan versi yang dipilih pemilik.

**Kriteria implementasi selesai:** kontrak, pemetaan, kirim ulang, koreksi dan status integrasi yang dipilih tersedia. Pada Fase 6, tujuh tanggal transaksi sintetis menghasilkan kuantitas Kasir, biaya Project, valuasi dan jurnal Accounting yang dapat direkonsiliasi. Simulasi kegagalan dan pengiriman ulang menghasilkan satu dampak per peristiwa sumber.

**Risiko:** dua sumber kebenaran atas stok yang sama. Mitigasi: aturan pemilik angka di dokumen 10 bagian 9, dan laporan rekonsiliasi sebagai tes penerimaan.

---

## Fase 5 — Skala dan saluran (bersyarat)

Fitur berikut dipilih pemilik sesuai kebutuhan, satu per satu:
- Dukungan pemindai Bluetooth/HID dan uji kecepatan untuk volume tinggi; opsional handheld Android bila ada pelanggan yang membeli.
- Serial number untuk barang elektronik.
- Varian barang (warna, ukuran).
- Integrasi marketplace dan kurir (hanya bila ada pelanggan e-commerce yang menuntut; bergantung API pihak ketiga).
- API publik dan webhook untuk integrasi pelanggan.
- KPI gudang (akurasi stok, waktu terima ke simpan, pesanan tepat waktu) dengan definisi dan target simulasi yang dicatat. Target bisnis dapat dievaluasi saat data pemakaian tersedia.

---

## Fase 6 — Pengujian simulasi menyeluruh, komersial dan rilis

Mengikuti Fase 6 Kasir:
- Halaman produk dan harga, syarat layanan, kebijakan privasi (ditinjau ahli hukum), panduan bantuan.
- Penagihan: konfirmasi manual oleh admin lebih dulu; panel admin client memuat tab Gudang.
- Pemantauan error, cadangan harian tenant dan uji pemulihan (Neon: cek retensi dan snapshot sebelum rilis), PWA.
- Eksekusi [rencana uji simulasi Gudang](13-finlite-gudang-rencana-uji-simulasi.md) oleh AI sub-agent dan Playwright di GitHub CI, memakai akun dan database sintetis. Cakupan meliputi pengaturan awal, saldo awal, masuk, keluar, transfer, retur, opname, integrasi yang dipilih, keamanan, beban, pemulihan dan ekspor.
- Catat commit backend/frontend, identitas deployment uji, data masukan, angka pembanding independen, hasil tiap skenario dan bukti. Perbaiki kegagalan dan jalankan regresi terkait hingga seluruh cakupan versi lulus.
- Pilot gudang fisik dan uji komersial pengguna nyata dijadwalkan kemudian saat tersedia.

**Kriteria penerimaan program:** seluruh skenario wajib untuk cakupan versi final lulus, saldo serta ekspor cocok dengan perhitungan independen, izin dan isolasi tenant terjaga, pengulangan serta transaksi bersamaan aman, dan bukti CI/deployment sesuai versi final tersedia. Skenario fitur yang dipilih tetapi belum tersedia dicatat sebagai pekerjaan tersisa. Kesiapan teknis rilis mengikuti pemeriksaan cadangan dan pemulihan yang berlaku. Validasi pasar dan pembayaran pelanggan dicatat saat penggunaan nyata tersedia.

---

## Urutan dan ketergantungan

```
Fase 0 -> Fase 1 -> Fase 2 -> (Fase 3 bila dipilih) -> Fase 6
                       \-> Fase 4 (sesuai kesiapan aplikasi tujuan) -/
Fase 5 mengikuti pilihan pemilik sebelum cakupan Fase 6 dikunci.
Fase 6 menjalankan seluruh pengujian program menggunakan simulasi.
```

Posisi terhadap rencana lain mengikuti keputusan pemilik pada 18 November 2026. Pengembangan Gudang dilanjutkan berdasarkan riset dan data sintetis. Dependensi teknis ke Kasir, Accounting dan Project dicatat pada kontrak integrasi. Ketersediaan gudang lapangan ditangani pada jadwal pilot tersendiri.

## Kriteria "siap dibangun" Fase 1 (dari dokumen 04)

Sebelum kode dimulai harus ada: pemilik domain, user story, matriks izin, diagram
status (penerimaan, pengeluaran, transfer, penyesuaian), kontrak API, aturan
akuntansi (kosong di Fase 1, mulai Fase 4), skenario gagal dan kirim ulang, migrasi
data (impor barang dan saldo awal), dan tes penerimaan.

## Keputusan dan pekerjaan berikutnya

1. Jadwal pengujian ditetapkan pada Fase 6 dengan simulasi, AI sub-agent dan Playwright. Rencana rinci ada di dokumen 13.
2. Implementasi kendali dasar Fase 1 sudah selesai. Pengembangan berikutnya adalah retur dan multi-satuan pada Fase 2.
3. Harga final dan cakupan integrasi komersial dicatat sebagai keputusan produk saat dibutuhkan. Pilot fisik menunggu ketersediaan gudang.
