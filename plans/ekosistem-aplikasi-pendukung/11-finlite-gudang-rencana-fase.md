# 11 — Finlite Gudang: rencana pembuatan per fase

> **STATUS: USULAN, BELUM DISETUJUI, BELUM ADA KODE.** Dibuat 14 November 2026.
> Dasar kebutuhan dan fitur: [10-finlite-gudang-riset-kebutuhan-dan-fitur.md](10-finlite-gudang-riset-kebutuhan-dan-fitur.md).
> Pola kerja mengikuti [08-finlite-pos-rencana-fase.md](08-finlite-pos-rencana-fase.md), yang sudah terbukti
> untuk Kasir. Ukuran usaha memakai S/M/L (kecil/sedang/besar), **bukan jadwal**.

## Prinsip

1. **Lengkap tanpa produk lain.** Gudang boleh dipakai tanpa Accounting dan tanpa Kasir. Integrasi opsional dan datang belakangan.
2. **Satu pemilik per angka.** Kuantitas fisik gudang dimiliki Gudang; nilai dan jurnal dimiliki Accounting; stok outlet dimiliki Kasir. Barang pindah antar pemilik hanya lewat transfer.
3. **Bin dan alur terarah opsional.** Gudang tanpa lokasi tetap jalan; konsep zona dan wave tidak boleh memaksa gudang kecil.
4. **Setiap perubahan stok punya dokumen.** Tidak ada tombol "ubah stok" tanpa alasan dan jejak.
5. **Mobile-first, online-only.** Kamera HP untuk scan; antrean ulang singkat saat sinyal putus, bukan mode offline penuh (usulan, perlu dikonfirmasi wawancara).
6. **Pakai ulang fondasi yang ada:** dimensi produk (paket, langganan, tenant, izin), pola jembatan idempoten, log aktivitas, pemantauan error, PWA.
7. **Uji di data nyata sejak awal**, termasuk gudang milik pemilik produk.

Tiap fase ditutup dengan: tes backend (CI), E2E Playwright di ukuran HP, dokumentasi
status, dan satu uji manual oleh pemilik produk.

## Ringkasan fase

| Fase | Isi | Ukuran | Syarat masuk |
| --- | --- | --- | --- |
| 0 | Penemuan dan fondasi: wawancara, keputusan terbuka, produk `gudang` di platform | M | Dokumen ini disetujui |
| 1 | MVP inventaris gudang: master, penerimaan, pengeluaran, transfer, kartu stok | L | Fase 0 selesai |
| 2 | Kendali: opname dan cycle count, batch dan kedaluwarsa, label, saran pembelian | L | Fase 1 dipakai uji |
| 3 | Operasi keluar terarah: reservasi, pick list, packing, retur, multi-satuan | L | Fase 2; wawancara membenarkan |
| 4 | Jembatan opsional ke Kasir dan Accounting | M | Fase 1-2; Kasir dan Accounting sudah ada |
| 5 | Skala dan saluran: pemindai Bluetooth, serial, marketplace, API (atas permintaan) | L | Permintaan pelanggan nyata |
| 6 | Komersial dan rilis | M | Fase 1-4 stabil |

Fase 3 dan 5 sengaja bersyarat: dikerjakan hanya bila wawancara dan pilot
menunjukkan kebutuhannya.

---

## Fase 0 — Penemuan dan fondasi

**Tujuan:** memastikan kita membangun yang dibutuhkan, dan menyiapkan Gudang
sebagai produk ketiga di platform.

Penemuan (tanpa kode):
- Wawancara 5-8 gudang dengan daftar pertanyaan di dokumen 10 bagian 8, termasuk gudang pemilik produk.
- Kumpulkan contoh dokumen nyata (surat jalan, DO, form opname) dan data barang untuk uji. Data nyata **tidak** masuk repositori; anonimkan.
- Putuskan 8 keputusan terbuka di dokumen 10 bagian 9, terutama: batch di MVP atau Fase 2, online-only, dan pemilik angka stok bila tersambung.
- Tulis "definisi siap dibangun" untuk Fase 1: pemilik domain, user story, matriks izin, diagram status dokumen, skenario gagal, tes penerimaan (dokumen 04).

Fondasi (kode kecil):
- Tambah `gudang` sebagai produk: paket, langganan, tenant, dan izin per produk (pola yang dipakai untuk `pos`).
- Tenant schema `gudang` per perusahaan saat diaktifkan, dengan migrasi terpisah (`tenant_gudang`).
- Paket awal: Gudang Gratis (satu gudang, batas barang) dan Gudang (batas pengguna), dengan masa coba dan mode hanya-baca saat habis, sama seperti Kasir.
- Kerangka aplikasi: repositori frontend baru (React, Vite, TypeScript, Tailwind, TanStack Query) dari kerangka Kasir, PWA, halaman masuk, pilih perusahaan.

**Kriteria selesai:** keputusan terbuka terjawab dan tercatat; wawancara menghasilkan daftar prioritas fitur yang menggantikan tebakan di dokumen 10; pemilik dapat mendaftar, mengaktifkan produk Gudang, dan melihat halaman kosong yang terkunci langganan.

**Status (15 November 2026):** Fase 0 dimulai. Fondasi backend selesai (laravel_backend#30: produk `gudang`, paket, izin, aktivasi). Panduan wawancara, daftar keputusan, dan draf spesifikasi Fase 1 ada di [12](12-finlite-gudang-fase0-wawancara-dan-spesifikasi-awal.md). Menunggu: wawancara, keputusan pemilik, dan repositori frontend baru.

**Risiko:** wawancara menunjukkan pasar utama bukan yang diasumsikan. Mitigasi: fase 1 baru dimulai setelah wawancara, dan rencana ini direvisi.

---

## Fase 1 — MVP inventaris gudang

**Tujuan:** gudang kecil-menengah berhenti mencatat di kertas dan Excel; semua barang masuk, keluar, dan pindah punya dokumen, dan stok per gudang/lokasi bisa dipercaya.

Backend (tenant `gudang`):
- Master: barang (SKU, banyak barcode, kategori, satuan dasar, foto), pemasok, tujuan/pelanggan, gudang, lokasi hierarki opsional (zona > rak > bin) dengan jenis lokasi (simpan, terima, karantina, rusak).
- Buku stok sebagai sumber kebenaran: setiap perubahan lewat satu layanan yang menulis mutasi, saldo per (barang, lokasi), dan log aktivitas dalam satu transaksi. Tidak ada jalan lain mengubah saldo. Saldo tidak boleh negatif kecuali pengaturan mengizinkan.
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

**Kriteria selesai:** satu gudang uji menjalankan satu minggu dengan semua barang masuk, keluar, dan transfer lewat aplikasi, tanpa catatan di luar aplikasi; stok fisik hasil hitung acak cocok dengan sistem untuk barang yang disentuh minggu itu; tes beban satu gudang 5.000 barang dan 500 mutasi per hari (usulan, sesuaikan hasil wawancara) di bawah 250 ms untuk baca.

**Risiko:** buku stok yang bisa diakali; mitigasi: satu pintu tulis dan tes yang mencoba saldo negatif, transaksi serentak, dan simpan ganda (pelajaran nomor kembar di Kasir).

---

## Fase 2 — Kendali stok

**Tujuan:** mengurangi selisih dan barang kedaluwarsa, dan membuat opname tidak menghentikan operasi.

Backend:
- Opname penuh dan cycle count: sesi hitung per gudang/zona/kelas, hitung buta (penghitung tidak melihat angka sistem), hitung ulang untuk selisih besar, persetujuan sebelum penyesuaian; jadwal cycle count berdasar kelas ABC (A paling sering).
- Klasifikasi ABC dari pergerakan 90 hari, dihitung otomatis dan bisa ditimpa.
- Batch/lot dan tanggal kedaluwarsa per barang (opsional per barang): dicatat saat terima, saldo per batch, FEFO saat keluar (kedaluwarsa terdekat disarankan lebih dulu), peringatan N hari sebelum kedaluwarsa, karantina batch, telusur batch maju-mundur untuk recall.
- Stok minimum/maksimum dan titik pesan per barang atau gudang; daftar saran pembelian (permintaan selama lead time + stok pengaman) yang ditandai kapan terakhir diperbarui supaya tidak basi.
- Laporan: barang akan kedaluwarsa, kedaluwarsa, barang lambat dan stok mati, akurasi stok (hasil cycle count), selisih per penghitung dan per lokasi.
- Cetak label barcode barang dan bin (PDF ukuran label) dengan kode yang bisa dipindai kamera; opsional GS1-128 untuk lot dan kedaluwarsa bila wawancara menuntut.

Frontend:
- Layar hitung (scan lokasi, scan barang, isi jumlah), daftar tugas hitung hari ini.
- Layar peringatan: kedaluwarsa dan stok menipis di beranda.
- Cetak label dari daftar barang dan lokasi.

**Kriteria selesai:** satu siklus opname di gudang uji selesai tanpa menutup gudang; selisih tiap lokasi bisa ditelusuri ke dokumen; barang berkedaluwarsa tidak pernah disarankan keluar sebelum yang lebih dekat; uji label dengan barcode nyata terbaca kamera HP dari jarak kerja biasa.

**Risiko:** UI batch yang membingungkan. Mitigasi: batch hanya muncul untuk barang yang diaktifkan batch; uji dengan staf gudang sungguhan.

---

## Fase 3 — Operasi keluar terarah (bersyarat)

**Tujuan:** untuk gudang dengan banyak pesanan keluar per hari: kurangi salah ambil dan percepat pengeluaran.

Dikerjakan hanya bila wawancara dan pilot Fase 1-2 menunjukkan pengeluaran sebagai titik sakit.

- Pesanan keluar (permintaan barang): reservasi stok sehingga tersedia = di tangan - dipesan.
- Pick list berurutan menurut lokasi; pick dengan scan dan verifikasi jumlah; kekurangan stok dicatat sebagai short pick.
- Strategi picking: per pesanan lebih dulu; batch dan per zona hanya bila diminta.
- Packing sederhana: daftar kemasan, berat, dan catatan; cetak surat jalan dan label kirim; status kirim.
- Retur masuk (dari pelanggan) dan retur ke pemasok dengan penempatan ke lokasi karantina atau rusak.
- Multi-satuan (dus, pak, pcs) dengan konversi, di semua dokumen dan label.
- Usulan putaway otomatis (kategori, ruang kosong, barang sama di bin).

**Kriteria selesai:** satu hari pesanan nyata melewati pick-pack-kirim tanpa kertas; tingkat salah ambil terukur sebelum dan sesudah (ukuran dari pilot sendiri, bukan patokan internet).

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

**Kriteria selesai:** satu minggu penerimaan, transfer ke Kasir, dan opname menghasilkan jurnal dan stok Kasir yang cocok dengan stok Gudang tanpa duplikat; putus dan sambung ulang tidak menggandakan.

**Risiko:** dua sumber kebenaran atas stok yang sama. Mitigasi: aturan pemilik angka di dokumen 10 bagian 9, dan laporan rekonsiliasi sebagai tes penerimaan.

---

## Fase 5 — Skala dan saluran (bersyarat)

Hanya atas permintaan pelanggan nyata, satu per satu:
- Dukungan pemindai Bluetooth/HID dan uji kecepatan untuk volume tinggi; opsional handheld Android bila ada pelanggan yang membeli.
- Serial number untuk barang elektronik.
- Varian barang (warna, ukuran).
- Integrasi marketplace dan kurir (hanya bila ada pelanggan e-commerce yang menuntut; bergantung API pihak ketiga).
- API publik dan webhook untuk integrasi pelanggan.
- KPI gudang (akurasi stok, waktu terima ke simpan, pesanan tepat waktu) dengan target dari data pilot.

---

## Fase 6 — Komersial dan rilis

Mengikuti Fase 6 Kasir:
- Halaman produk dan harga, syarat layanan, kebijakan privasi (ditinjau ahli hukum), panduan bantuan.
- Penagihan: konfirmasi manual oleh admin lebih dulu; panel admin client memuat tab Gudang.
- Pemantauan error, cadangan harian tenant dan uji pemulihan (Neon: cek retensi dan snapshot sebelum rilis), PWA.
- Rencana pengujian menyeluruh (format dokumen 09): alur, jembatan, beban, keamanan, pilot.
- **Uji coba terbatas** di 2-3 gudang selama satu bulan.

**Kriteria selesai:** gudang pilot membayar langganan dan memakai Gudang tanpa pendampingan selama satu bulan, dengan stok fisik cocok pada hitung acak.

---

## Urutan dan ketergantungan

```
Fase 0 -> Fase 1 -> Fase 2 -> (Fase 3 bila terbukti perlu) -> Fase 6
                       \-> Fase 4 (bisa sejajar setelah Fase 1-2 stabil) -/
Fase 5: lepas, hanya atas permintaan.
```

Posisi terhadap rencana lain: urutan di dokumen 07 menaruh WMS sebagai "4+" setelah
POS dan Workspace dengan syarat "ditentukan setelah pelajaran dari POS dan
Workspace". Rencana ini **tidak mengubah urutan itu**: Fase 0 (wawancara dan
keputusan) boleh jalan kapan saja karena murah, sedangkan Fase 1 sebaiknya
menunggu Kasir lolos pilot, supaya fondasi dan pelajaran tidak terbagi dua.

## Kriteria "siap dibangun" Fase 1 (dari dokumen 04)

Sebelum kode dimulai harus ada: pemilik domain, user story, matriks izin, diagram
status (penerimaan, pengeluaran, transfer, penyesuaian), kontrak API, aturan
akuntansi (kosong di Fase 1, mulai Fase 4), skenario gagal dan kirim ulang, migrasi
data (impor barang dan saldo awal), dan tes penerimaan.

## Yang dibutuhkan darimu sekarang

1. Setuju atau ubah **8 keputusan terbuka** di dokumen 10 bagian 9.
2. Siapa 5-8 gudang untuk wawancara (satu bisa gudang milikmu sendiri).
3. Apakah Fase 0 (wawancara dan keputusan) dimulai sekarang, sementara Kasir masih menunggu pengujian, atau menunggu pilot Kasir selesai.
