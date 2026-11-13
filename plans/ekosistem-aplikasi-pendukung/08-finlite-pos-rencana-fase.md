# 08 — Finlite POS: rencana per fase (Fase 0 sampai rilis)

Status per 13 November 2026. Melengkapi konsep (dokumen 06) dan keputusan
platform (dokumen 07). Setiap fase berisi tujuan, pekerjaan backend
(`laravel_backend`, modul `app/Modules/Pos`), pekerjaan frontend (repo
`finlite_pos`), dan kriteria selesai.

## Prinsip yang mengikat semua fase

1. **POS berdiri sendiri.** Pembeli POS tidak perlu berlangganan Finlite
   Accounting. Akun, toko, paket, dan datanya bisa ada tanpa tenant akuntansi.
2. **Integrasi itu pilihan.** Kalau perusahaan juga memakai Finlite
   Accounting, pemilik bisa menyalakan "Hubungkan ke Akuntansi". Kalau
   dimatikan atau salah satu produk berhenti, kedua aplikasi tetap jalan.
3. **Satu akun Finlite.** Login, perusahaan, dan pengguna tetap satu identitas
   lintas produk (dokumen 07). Yang terpisah adalah tenant data per produk.
4. **Arus data satu arah dan idempoten.** POS mengirim ringkasan ke Akuntansi;
   Akuntansi tidak mengubah data POS. Kiriman yang sama tidak boleh tercatat
   dua kali.

## Ringkasan status

| Fase | Isi | Status |
| --- | --- | --- |
| 0 | Fondasi platform multi-produk | Selesai (di-merge 6 November 2026) |
| 1 | MVP kasir | Kode + E2E selesai, belum online |
| 2 | Berdiri sendiri: daftar, toko, paket POS | Selesai inti (6 Nov 2026); sisa UI admin & paket berbayar |
| 3 | Operasional toko harian | Belum |
| 4 | Laporan, kendali, dan keamanan | Selesai kode (4a laporan, 4b kendali, 4c beban); belum diuji pemilik toko |
| 5 | Jembatan ke Finlite Accounting (opsional) | 5a selesai (kode): jurnal Rekap Kasir per shift; stok masuk dan sinkron produk belum |
| 6 | Komersial dan rilis | Belum |

Urutan wajib: 0 → 1 → 2. Fase 3 dan 4 boleh berjalan sejajar setelah Fase 2.
Fase 5 boleh dimulai setelah Fase 2 karena hanya bergantung pada fondasi.

---

## Fase 0 — Fondasi platform multi-produk

**Tujuan:** backend bisa melayani lebih dari satu produk per perusahaan tanpa
mencampur data.

Sudah selesai (5 November 2026):
- `tenant_databases.product`, unik per (perusahaan, produk). Kode akuntansi lama
  tetap memakai tenant akuntansi lewat global scope.
- Tenant POS terpisah (`..._pos`), folder migrasi `database/migrations/tenant_pos`.
- Middleware `company.access:pos`, izin `pos.*` di matriks hak akses.
- Purge perusahaan ikut membuang tenant POS.

Selesai di PR laravel_backend#15 (6 November 2026):
- **Koneksi database POS terpisah** (`pos`, bukan `tenant`), jadi satu request
  bisa membuka tenant akuntansi dan tenant POS bersamaan.
- **Produk pada paket dan langganan**: kolom `product` di `plans` dan
  `subscriptions`; `SubscriptionService` per produk; paket `pos` (harga 0,
  tempat). `users.plan_id` tetap berarti paket akuntansi.
- **Perusahaan tanpa tenant akuntansi**: `POST /companies` dengan
  `product=pos`; kuota per produk; toko POS-only tidak memakan kuota akuntansi.
- **Aktivasi produk**: `POST /companies/{id}/products/{product}/activate`,
  hanya pemilik, dan pemilik wajib berlangganan produk itu. Aktivasi POS dari
  aplikasi kasir memakai aturan yang sama.
- **Daftar perusahaan per produk**: `/companies` memuat `products`. Finlite
  Accounting menandai toko "Baru memakai Kasir" dan menawarkan aktivasi;
  aplikasi kasir langsung membuka toko yang sudah punya POS.

Catatan teknis untuk pengembang ada di `laravel_backend/docs/pos-dan-multi-produk.md`.

Belum (dipindah ke Fase 2): login masih dikunci oleh status langganan
akuntansi saja; pemilik toko POS-only dibuatkan akun oleh admin.

Kriteria selesai: perusahaan bisa punya hanya tenant POS, hanya tenant
akuntansi, atau keduanya; test tenant isolation dan izin hijau di CI untuk
ketiga kombinasi.

---

## Fase 1 — MVP kasir

**Tujuan:** satu toko bisa berjualan sehari penuh dari HP.

Sudah selesai (kode, di-merge ke `main`, diuji lokal di browser ukuran HP):
- Backend: aktivasi oleh pemilik, bootstrap, kategori dan produk (stok opsional,
  barcode), mutasi stok, pelanggan dan kasbon, shift dengan rekap laci,
  penjualan tunai/QRIS/transfer/kasbon, pembatalan selama shift terbuka,
  laporan ringkas, pengaturan toko. Test alur di `tests/Feature/Pos/PosFlowTest.php`.
- Frontend: login, pilih toko, kasir dengan scan barcode, pembayaran dengan
  nominal cepat, struk WhatsApp/cetak browser, produk, pelanggan, transaksi,
  shift, laporan, pengaturan.

Selesai 6 November 2026:
- Test E2E Playwright di repo `finlite_pos` (`npm run e2e`, ukuran HP): buka
  shift, jual tunai, kasbon via scan barcode, tolak stok kurang, batal, tutup
  shift cocok. Backend sqlite sementara, toko POS-only tanpa langganan
  akuntansi. 6/6 lulus lokal. (Belum jalan di CI: butuh PHP + repo backend.)

Sisa pekerjaan:
- Deploy frontend ke Vercel (`pos.finlite.my.id`), isi `VITE_API_BASE_URL`,
  tambahkan domain ke `CORS_ALLOWED_ORIGINS` di Render. (Project Vercel sudah
  dibuat pemilik; URL dan env belum dicek.)
- Uji di HP sungguhan (Android Chrome, iOS Safari) dan dengan pemindai barcode USB/Bluetooth.

Kriteria selesai: pemilik uji menjalankan satu hari jualan nyata di HP tanpa
bantuan, angka tutup shift cocok dengan uang laci.

---

## Fase 2 — Berdiri sendiri

**Tujuan:** warung bisa mendaftar dan memakai POS tanpa menyentuh Finlite
Accounting dan tanpa dibuatkan akun oleh admin.

Backend:
- Pendaftaran publik khusus POS: nama, email, kata sandi, nama toko;
  verifikasi email. (Finlite Accounting tetap tanpa pendaftaran publik.)
- Buat toko dari aplikasi kasir: perusahaan + tenant POS saja.
- Paket POS: trial, gratis terbatas, dan berbayar. Kuota per produk: jumlah
  toko, kasir, dan produk. Perilaku saat langganan habis: hanya baca, tidak
  bisa membuat transaksi baru, data tidak dihapus.
- Undang kasir dari aplikasi POS (memakai undangan yang sudah ada) dengan
  templat izin "Kasir" dan "Kepala toko".
- Panel admin: daftar klien POS, perpanjang, ubah paket.

Frontend:
- Halaman daftar, verifikasi email, lupa kata sandi.
- Wizard toko pertama: nama toko, alamat, contoh produk (opsional).
- Halaman pengguna toko: undang kasir, atur izin, nonaktifkan.
- Spanduk masa langganan dan tautan upgrade.

Integrasi dengan Finlite Accounting di fase ini hanya satu hal: kalau pemilik
membuka Finlite Accounting dengan akun yang sama, perusahaan POS tampil dengan
tombol "Aktifkan Akuntansi" yang membuat tenant akuntansi untuk perusahaan itu.

Kriteria selesai: orang baru bisa mendaftar sampai transaksi pertama dalam 5
menit, tanpa admin dan tanpa tenant akuntansi.

Selesai 6 November 2026 (laravel_backend#17, finlite_pos 790d02e):
- Daftar mandiri + verifikasi email. Masa coba Kasir 14 hari dimulai saat
  email terverifikasi; toko baru bisa dibuat setelah itu (email palsu tidak
  bisa membuat tenant). Nama toko diisi di wizard, bukan di form daftar.
- Wizard toko pertama (nama, alamat, HP, contoh produk opsional).
- Langganan habis → toko hanya-baca (lihat data boleh, simpan ditolak).
  Login aplikasi kasir tidak dikunci langganan akuntansi.
- Pengguna toko: undang Kasir / Kepala toko (email + tautan WhatsApp), ubah
  peran, nonaktifkan; jatah pengguna mengikuti paket Kasir pemilik.
- Lupa/atur ulang kata sandi dan terima undangan di aplikasi kasir.
- Spanduk masa coba, jatuh tempo, dan hanya-baca.
- Backend admin: filter klien Kasir, status langganan Kasir, perpanjang dan
  buka kunci per produk.
- E2E `daftar.spec.ts`: daftar → verifikasi → buat toko → undang kasir →
  kasir bergabung dengan izin kasir saja (lulus lokal).

Selesai juga 6 November 2026 (laravel_backend#18, react_frontend#10,
finlite_pos cf48ece):
- Paket **Kasir** (3 pengguna, 1 toko, produk tanpa batas; dipakai masa coba)
  dan **Kasir Gratis** (1 pengguna, 1 toko, 30 produk). Batas produk dan
  pengguna ditegakkan; data lama tidak dihapus saat turun paket.
- Setelah masa coba habis, pemilik bisa mengambil Kasir Gratis sendiri tanpa
  admin, atau berlangganan lewat tombol WhatsApp (pembayaran manual).
- Halaman **Langganan** di aplikasi kasir (paket, masa berlaku, pemakaian);
  spanduk menautkan ke sana.
- Panel admin Finlite Accounting: filter client Kasir, kolom status Kasir,
  tab "Finlite Kasir" untuk mulai/perpanjang/ganti paket dan buka toko.
- E2E: masa coba habis → hanya-baca → pilih Kasir Gratis (11/11 lulus lokal).

Status: **kode Fase 2 selesai.** Tersisa keputusan dan pengaturan pemilik:
- **Harga paket Kasir** masih Rp 0 (ubah di `PlanSeeder` setelah diputuskan).
- Isi env di Render: `MAIL_*` (verifikasi email harus sampai),
  `POS_SALES_WHATSAPP` (nomor WhatsApp penjual), dan `POS_FRONTEND_URL` bila
  domain kasir bukan `pos.finlite.my.id`.
- Pembayaran otomatis (payment gateway) tidak termasuk Fase 2.

---

## Fase 3 — Operasional toko harian

**Tujuan:** kebutuhan rutin warung, toko, dan koperasi sekolah tertutup.

Backend:
- Retur penjualan: sebagian atau penuh, stok kembali, uang kembali atau potong kasbon.
- Pemasok dan stok masuk (pembelian sederhana): harga beli memperbarui harga
  modal rata-rata; hutang ke pemasok opsional.
- Stok opname dengan selisih tercatat.
- Diskon per baris, harga grosir (harga berbeda per jumlah), pembulatan total.
- Pajak opsional per toko (PPN atau tanpa pajak), dihitung per transaksi.
- Impor produk dari Excel; foto produk (penyimpanan berkas dengan kuota).
- Satuan ganda sederhana (mis. dus = 40 pcs) — diputuskan setelah uji lapangan.

Frontend:
- Cetak langsung ke printer thermal Bluetooth: spike dulu di HP dan printer
  nyata (Web Bluetooth di Android Chrome; iOS lewat aplikasi pencetak), lalu
  jadikan pilihan "Cetak" bawaan.
- Scan barcode memakai kamera HP.
- Layar retur, stok masuk, opname, dan impor produk.
- Antrean sementara saat sinyal putus beberapa detik (tombol simpan diulang
  otomatis dengan kunci idempoten, bukan mode offline penuh).

Kriteria selesai: koperasi sekolah uji menjalankan satu minggu, termasuk
barang masuk dan retur, tanpa catatan manual di luar aplikasi.

Progres:
- **3a selesai 6 November 2026** (laravel_backend#19, finlite_pos 812b57e):
  retur penjualan sebagian/penuh (uang kembali tunai/transfer/QRIS atau
  potong kasbon; barang rusak tidak kembali ke stok), pemasok dan barang
  masuk (modal rata-rata, hutang pemasok dan pelunasannya), stok opname
  dengan selisih jumlah dan nilai, serta simpan transaksi yang diulang
  otomatis saat sinyal putus (kunci idempoten). E2E 14/14 lulus.
- **3b selesai 7 November 2026** (laravel_backend#20, finlite_pos f46e8aa):
  harga grosir per produk (maks 5 tingkat), diskon per baris di keranjang,
  pajak per toko (tanpa / ditambahkan / sudah termasuk harga), pembulatan
  total (100/500/1.000; terdekat/bawah/atas), struk memuat pajak dan
  pembulatan. Sekalian diperbaiki: hari toko mengikuti zona waktu toko
  (WIB/WITA/WIT); sebelumnya transaksi tengah malam sampai jam 7 pagi WIB
  masuk tanggal kemarin. E2E 15/15 lulus.
- **3c selesai 7 November 2026** (laravel_backend#21, finlite_pos 748c433):
  impor produk dari Excel/CSV dengan pratinjau (produk lama diperbarui lewat
  SKU/barcode/nama, stoknya tidak diubah), ekspor dan templat Excel, foto
  produk (diperkecil di HP, disimpan di database toko, kuota 50 MB per toko),
  scan barcode dengan kamera HP di layar kasir dan form produk. E2E 16/16 lulus.
- Sisa Fase 3 butuh perangkat nyata: uji scan kamera di Android dan iPhone,
  cetak Bluetooth (spike di HP Android + printer thermal), uji lapangan
  satuan ganda.

---

## Fase 4 — Laporan, kendali, dan keamanan

Backend:
- Laporan per kasir, per shift, per produk (laba per produk), per kategori,
  per jam; stok menipis; umur kasbon.
- Ekspor Excel untuk semua laporan.
- Log audit: pembatalan, ubah harga, ubah stok, buka/tutup shift.
- Batas wewenang: diskon maksimum per kasir, pembatalan butuh PIN kepala toko.
- Ketahanan beban: indeks, uji beban satu toko 2.000 transaksi per hari.

Frontend:
- Dasbor pemilik (penjualan hari ini, perbandingan kemarin, produk terlaris).
- Layar laporan lengkap dengan filter dan ekspor.
- PIN kepala toko untuk aksi sensitif.

Kriteria selesai: pemilik bisa menjawab "berapa laba minggu ini, kasir mana
yang selisih, barang apa yang harus dibeli" dari aplikasi.

Progres (Fase 4 dipecah: 4a laporan & dasbor, 4b log audit & batas wewenang
& PIN, 4c ketahanan beban):
- **4a selesai 7 November 2026** (laravel_backend#22, finlite_pos 4ff1d12):
  dasbor pemilik (hari ini vs kemarin, grafik 7 hari, terlaris, stok
  menipis, shift buka), laporan per kasir (termasuk selisih laci), rekap
  shift, laba per produk, per kategori, per jam, stok menipis dengan saran
  beli (rata-rata jual 14 hari), umur kasbon (0-30/31-60/61-90/>90 hari);
  semua bisa diekspor Excel. Stok minimum per produk. E2E 17/17 lulus.
- **4b selesai 13 November 2026** (laravel_backend dan finlite_pos, branch
  `claude/lucid-mendel-ddotc4`): log audit (buka/tutup shift dengan selisih
  laci, batal, retur, ubah harga produk, ubah stok dan opname, diskon di atas
  batas, PIN, pengaturan), batas diskon per kasir (bawaan toko + batas pribadi),
  PIN kepala toko (hash, kunci 5 menit setelah 5 kali salah) untuk menyetujui
  diskon di atas batas, dan batal/retur oleh kasir (mati bawaan; pemilik
  menyalakannya). Izin baru `pos.audit.view` dan `pos.discount.override`.
  Tes backend 28/28 di folder POS, suite penuh tanpa gagal; E2E 21/21.
  Belum tercatat di log: perubahan harga lewat impor produk dan stok masuk.
- **4c selesai 13 November 2026** (laravel_backend, branch
  `claude/lucid-mendel-ddotc4`): uji beban satu toko 30 hari x 2.000 transaksi
  (60.000 nota) di Postgres 16 lokal, lewat `tests/TenantPgsql/PosLoadTest.php`.
  Ringkasan 30 hari 15,7 dtk -> 0,24 dtk, laporan per jam 30 hari 20,2 dtk ->
  0,04 dtk, dasbor 5,3 dtk -> 0,24 dtk, daftar transaksi 0,58 dtk -> 0,03 dtk;
  semua permintaan baca kini di bawah 250 ms. Penyebabnya: pengelompokan per
  hari/jam dikerjakan di PHP (kini di SQL), FK baris penjualan tidak
  berindeks (Postgres tidak mengindeks FK otomatis), dan umur kasbon satu query
  per pelanggan. Ditemukan dan diperbaiki juga **nomor transaksi bentrok** saat
  dua kasir menyimpan bersamaan (24 dari 120 transaksi gagal 500 pada uji 8
  permintaan serentak; kini penghitung atomik, 120/120 dan 200/200 berhasil
  tanpa nomor kembar atau deadlock). Belum diukur: Neon sungguhan dan beban
  banyak perangkat sekaligus.
- **Fase 4 selesai** (4a, 4b, 4c). Kriteria "pemilik bisa menjawab berapa laba
  minggu ini, kasir mana yang selisih, barang apa yang harus dibeli" sudah
  tersedia di aplikasi; belum diuji pemilik toko sungguhan.

---

## Fase 5 — Jembatan ke Finlite Accounting (opsional)

**Tujuan:** perusahaan yang memakai dua produk tidak perlu mencatat penjualan
kasir dua kali. Perusahaan yang hanya memakai POS tidak terpengaruh.

Syarat: Fase 0 selesai (koneksi `pos` terpisah). Tombol hanya muncul kalau
kedua produk aktif.

Backend:
- Pengaturan jembatan per perusahaan: aktif/tidak, tanggal mulai, dan
  pemetaan akun: kas laci, bank, QRIS, piutang kasbon, pendapatan, diskon,
  HPP, persediaan, pajak keluaran.
- **Satuan kiriman = shift yang sudah ditutup.** Shift tertutup tidak bisa
  berubah (pembatalan hanya selama shift terbuka), jadi aman dijadikan dasar
  jurnal. Satu shift menjadi satu jurnal sistem "Rekap Kasir" berisi:
  - Debit kas/bank/QRIS dan piutang kasbon, kredit pendapatan, debit diskon.
  - Opsional: debit HPP, kredit persediaan (memakai harga modal saat jual).
- Pelunasan kasbon menjadi jurnal penerimaan (debit kas/bank, kredit piutang).
- Retur dan stok masuk (Fase 3) mengikuti pola yang sama.
- Kunci idempoten `(company, source=pos, jenis, id)`; tabel status kiriman
  (menunggu, terkirim, gagal + pesan) dan tombol kirim ulang.
- Periode akuntansi terkunci: kiriman ditahan dan ditandai, tidak dipaksa masuk.
- Sinkron produk opsional: impor produk dari Finlite Accounting ke POS, atau
  tautkan produk POS ke produk akuntansi (untuk kartu stok di Akuntansi).
  Default: tidak sinkron; Akuntansi cukup menerima nilai HPP dan persediaan.
- Memutus jembatan menghentikan kiriman baru; jurnal yang sudah terkirim tetap.

Frontend (POS):
- Halaman "Hubungkan ke Akuntansi": status, pemetaan akun (pilih dari daftar
  akun Finlite Accounting), riwayat kiriman, kirim ulang.

Frontend (Finlite Accounting):
- Jurnal "Rekap Kasir" tampil dengan tautan sumber ke shift POS.
- Laporan laba rugi dan neraca sudah memuat penjualan kasir.

Kriteria selesai: satu minggu transaksi kasir masuk ke laba rugi Akuntansi
dengan angka sama persis dengan laporan POS; memutus dan menyambung ulang
jembatan tidak menggandakan jurnal.

Progres:
- **5a selesai 13 November 2026** (laravel_backend dan finlite_pos): jembatan
  per shift tertutup. Satu jurnal sistem "Rekap Kasir" (`source_type=pos_shift`)
  berisi penjualan menurut cara bayar, diskon, pajak, pembulatan, retur,
  pelunasan kasbon, dan opsional HPP/persediaan. Pengaturan per toko (aktif,
  tanggal mulai, pemetaan akun dengan usulan dari kode template), status kiriman
  (menunggu, terkirim, gagal, ditahan, tanpa transaksi), kirim ulang, dan
  halaman "Hubungkan ke Akuntansi" di aplikasi kasir. Idempoten dua lapis
  (kunci `(jenis, id)` dan pemeriksaan jurnal bersumber di akuntansi): putus-sambung
  atau kirim ulang tidak menggandakan jurnal. Kegagalan tidak pernah
  menggagalkan penutupan shift. Periode atau tahun fiskal terkunci -> kiriman
  ditahan. Opsi "Rekap Kasir" ada di filter Jenis Jurnal aplikasi akuntansi.
  Temuan penting: guard tanggal akuntansi menolak shift 00.00-07.00 WIB sebagai
  "transaksi masa depan" (memakai tanggal server UTC), jadi jembatan hanya
  mengecek kunci periode. Tes: 11 tes backend baru, E2E 25/25 (4 baru).
- **Belum:** stok masuk dan pembayaran pemasok sebagai jurnal (butuh akun Hutang
  pemasok), sinkron produk POS dan Akuntansi (opsional), tautan jurnal ke layar
  shift di aplikasi akuntansi. Kriteria "satu minggu transaksi cocok dengan
  laporan POS" belum diuji dengan data nyata.

---

## Fase 6 — Komersial dan rilis

- Halaman produk dan harga POS, syarat layanan, kebijakan privasi.
- Penagihan langganan: transfer manual dikonfirmasi admin dulu; payment
  gateway menyusul.
- Panduan bantuan singkat (video atau teks) per layar.
- Pemantauan error frontend dan backend, cadangan data tenant POS harian, uji pemulihan.
- PWA terpasang di layar utama HP, ikon dan nama aplikasi.
- Uji coba terbatas (pilot) di beberapa toko sebelum dibuka umum.

Kriteria selesai: toko pilot membayar langganan dan memakai POS tanpa
pendampingan selama satu bulan.

---

## Keputusan yang masih terbuka

| Topik | Usulan bawaan |
| --- | --- |
| Harga dan isi paket POS | Ditentukan pemilik produk sebelum Fase 2 |
| Mode offline penuh | Tidak; cukup antrean ulang singkat (Fase 3) |
| Model printer acuan | Ditentukan saat spike Bluetooth (Fase 3) |
| Kirim HPP/persediaan ke Akuntansi | Opsional per perusahaan, default mati |
| Satuan ganda | Diputuskan setelah uji lapangan Fase 3 |
| Domain aplikasi | `pos.finlite.my.id` |
