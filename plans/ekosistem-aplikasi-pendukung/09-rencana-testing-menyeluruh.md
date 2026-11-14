# 09 — Rencana testing menyeluruh Finlite Kasir dan jembatan Akuntansi

Dibuat 14 November 2026, setelah kode Fase 0-6 selesai di `main`. Tujuan: yakin
produk siap dipakai toko sungguhan, bukan hanya lulus tes otomatis.

## Yang sudah otomatis (jangan diulang manual)

| Lapisan | Cakupan | Status 14 Nov 2026 |
| --- | --- | --- |
| Tes backend (CI `Tests`, SQLite + job Postgres) | Semua modul, POS 56 tes di folder `tests/Feature/Pos` | Hijau di `main` |
| Tes Postgres lokal (`TenantPgsql`) | Query laporan, uji beban 60.000 nota | Lulus lokal; bukan bagian CI |
| E2E Playwright aplikasi kasir (ukuran HP) | Alur kasir, retur, stok, kendali, jembatan, rilis | 29/29 lokal (tanpa CI) |

Celah yang tidak tertangkap tes otomatis: perilaku di Neon sungguhan, HP dan
printer nyata, data bertahun-tahun, dan kebiasaan pemakai.

## Tahap 1 — Cek lingkungan (setengah hari)

- [ ] Deploy `main` sehat: Render live di commit terbaru, kedua Vercel READY
      (dicek 14 Nov 2026: Vercel READY; Render menyusul).
- [ ] Cari `pos.client_error` di log Render: tidak ada error tak dikenal.
- [ ] Migrasi tenant jalan tanpa error di log start (baris tenant yatim id 2-9
      "Company tidak ditemukan" dibersihkan dulu).
- [ ] Daftar periksa rilis production (cadangan Neon, retensi, snapshot,
      uji pemulihan) selesai. Lihat bagian itu di `08-finlite-pos-rencana-fase.md`.

## Tahap 2 — Uji alur di production-uji (1-2 hari, dikerjakan pemilik)

Pakai akun uji baru dan toko uji; jangan data lama. Jalankan di HP (Chrome
Android) dan satu iPhone bila ada.

| # | Skenario | Hasil yang diharapkan |
| --- | --- | --- |
| 1 | Daftar, verifikasi email, buat toko | Masa coba 14 hari aktif, contoh produk muncul |
| 2 | Pasang aplikasi di layar utama (Android dan iPhone) | Ikon benar, terbuka tanpa bilah browser |
| 3 | Buka shift, jual tunai, QRIS, transfer, kasbon | Total, kembalian, stok benar; struk terbagi |
| 4 | Diskon per baris, harga grosir, pajak, pembulatan | Angka di keranjang = struk = laporan |
| 5 | Retur sebagian, batalkan transaksi dengan PIN kepala toko | Stok dan kas kembali; tercatat di log |
| 6 | Stok masuk dari pemasok (sebagian hutang), bayar hutang | Modal rata-rata dan saldo hutang benar |
| 7 | Stok opname dengan selisih | Stok menyesuaikan; selisih nilai tercatat |
| 8 | Impor produk dari Excel (templat, pratinjau, simpan) | Baris benar masuk, baris salah dilewati |
| 9 | Scan barcode kamera (Android dan iPhone) | Produk terbaca; gagal terbaca = pesan jelas |
| 10 | Cetak struk Bluetooth | Cetak keluar; bila belum didukung, catat model printer |
| 11 | Undang kasir; kasir tidak bisa lihat laporan/pengaturan | Izin sesuai peran |
| 12 | Tutup shift dengan selisih laci | Selisih tampil di rekap dan laporan per kasir |
| 13 | Matikan sinyal 10 detik saat simpan transaksi | Tersimpan sekali setelah sinyal kembali, tanpa dobel |
| 14 | Langganan habis lalu pakai Kasir Gratis | Mode hanya-baca, data utuh, batas 30 produk |
| 15 | Paksa error (mis. buka halaman tak ada data) | Layar "Ada yang tidak beres", laporan masuk log Render |

## Tahap 3 — Jembatan ke Akuntansi dengan data seminggu (kriteria Fase 5)

Satu toko yang memakai Kasir dan Akuntansi, pemetaan akun lengkap, HPP dikirim.

- [ ] Seminggu transaksi nyata/uji (minimal 3 shift berbeda, ada retur, kasbon,
      diskon, pajak, stok masuk, bayar hutang, satu opname berselisih).
- [ ] Laba rugi Akuntansi untuk periode itu = laporan POS: penjualan, diskon,
      retur, pajak, HPP. Selisih harus Rp 0.
- [ ] Neraca Saldo seimbang; Persediaan Akuntansi = nilai stok POS (stok x modal)
      setelah stok masuk, HPP, dan opname.
- [ ] Hutang pemasok di Akuntansi = total hutang pemasok di POS.
- [ ] Putus lalu sambung ulang jembatan, tekan "Kirim yang tertunda" dua kali:
      jumlah jurnal tidak bertambah.
- [ ] Kunci periode akuntansi, tutup shift: kiriman "Ditahan"; buka kunci lalu
      kirim ulang: terkirim satu kali.
- [ ] Shift ditutup pukul 00.00-07.00 WIB: tetap terkirim (bukan "transaksi masa depan").
- [ ] Opsi "Ambil produk dari Akuntansi": produk masuk tanpa stok, SKU ganda dilewati.
- [ ] Laporan Neraca Saldo dibuka dan dicetak A4 (Postgres): tidak error, kolom muat.

## Tahap 4 — Beban dan ketahanan

- [ ] Uji beban di Neon (bukan Postgres lokal): satu toko 2.000 transaksi/hari
      selama 30 hari; semua baca < 1 detik. Dibuat di branch Neon sementara
      yang dihapus sesudahnya, jangan di `production`.
- [ ] Dua sampai tiga kasir menyimpan transaksi bersamaan: tidak ada nomor kembar
      atau error 500.
- [ ] Cold start Render (paket gratis): catat waktu buka pertama; putuskan perlu
      paket berbayar atau tidak untuk toko pilot.
- [ ] Pemulihan: buat branch dari snapshot Neon, cek data tenant utuh, catat
      waktu yang dibutuhkan.

## Tahap 5 — Keamanan dan privasi (kecil tapi wajib)

- [ ] Kasir toko A tidak bisa membaca data toko B (coba ganti `X-Company-ID`).
- [ ] Endpoint `/api/pos/client-errors` dibatasi laju (20/menit) dan tidak
      menyimpan data sensitif.
- [ ] Token lama tidak berlaku setelah keluar. Kata sandi lupa/atur ulang jalan.
- [ ] Syarat layanan dan kebijakan privasi sudah ditinjau pemilik/ahli hukum.

## Tahap 6 — Toko pilot (1 bulan)

Kriteria selesai Fase 6: toko pilot membayar langganan dan memakai POS tanpa
pendampingan selama satu bulan.

- [ ] Pilih 2-3 toko (warung, toko kecil, koperasi sekolah).
- [ ] Hari 1: dampingi pasang aplikasi, impor produk, latihan satu shift.
- [ ] Minggu 1-4: pantau log `pos.client_error` tiap hari; catat keluhan di satu
      daftar (tanggal, toko, masalah, tingkat).
- [ ] Akhir minggu 2 dan 4: cocokkan jurnal Akuntansi dengan laporan POS (bila
      jembatan dipakai).
- [ ] Akhir bulan: wawancara singkat (apa yang membingungkan, apa yang kurang);
      hitung berapa kali butuh pendampingan.

## Syarat lulus sebelum dibuka umum

1. Tahap 1-5 selesai tanpa temuan tingkat tinggi yang terbuka.
2. Tahap 3: selisih laporan POS vs Akuntansi = Rp 0.
3. Cadangan Neon aktif dan pemulihan sudah pernah diuji.
4. Pilot sebulan: tidak ada kehilangan data, tidak ada selisih uang yang tak
   terjelaskan, kebutuhan pendampingan menurun ke nol.

## Cara mencatat temuan

Satu baris per temuan di `reviews/` (tanggal, tahap/skenario, apa yang terjadi,
apa yang diharapkan, tingkat: tinggi = data/uang salah atau hilang, sedang =
alur terhambat, rendah = tampilan/teks). Perbaikan temuan tinggi dikerjakan
sebelum tahap berikutnya.
