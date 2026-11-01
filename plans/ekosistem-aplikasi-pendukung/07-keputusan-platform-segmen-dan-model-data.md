# Keputusan Arah: Platform, Segmen, dan Model Data

> **STATUS: KEPUTUSAN ARAH (2026-11-01) — BELUM DIIMPLEMENTASIKAN.**
>
> Dokumen ini mencatat hasil diskusi pemilik produk. Bagian "Keputusan" mengikat arah rancangan; bagian "Hipotesis" dan "Keputusan masih terbuka" belum final. Skema tabel di bawah adalah rancangan awal, bukan migrasi yang sudah ada.

## 1. Keputusan yang diambil

| # | Keputusan | Dampak |
| --- | --- | --- |
| 1 | **Setiap produk harus lengkap tanpa produk lain.** Integrasi hanya tambahan opsional. | Workspace, POS, WMS, dan CRM tidak boleh bergantung pada tabel atau modul Accounting. |
| 2 | **Workspace dijual dan dipakai mandiri.** Sekolah boleh hanya memakai Workspace untuk melacak anggaran. Idealnya dipakai bersama Accounting, tetapi semua kombinasi harus berjalan. | Workspace memiliki tabel anggaran/RAB sendiri; tidak memakai modul Budget di database Accounting. |
| 3 | **POS (dan WMS, CRM) dijual terpisah.** Pelanggannya boleh bukan pelanggan Accounting. | Perlu pendaftaran organisasi dan langganan yang tidak melewati Accounting. |
| 4 | **Langganan menempel ke organisasi dan produk**, bukan ke pengguna pemilik. | `users.plan_id` dan `subscriptions.user_id` digantikan oleh hak pakai per organisasi per produk. |
| 5 | **Lapisan platform dibangun lebih dulu**, sebelum produk baru apa pun: identitas, organisasi, langganan per produk. | Murah sekarang karena Accounting belum punya pengguna produksi; mahal bila ditunda. |
| 6 | **Satu akun orang untuk semua produk** (Finlite ID). Hak akses tetap melekat ke orang per fitur, bukan peran. | Matriks izin per pengguna yang sudah ada dipakai ulang dengan awalan per produk. |
| 7 | **Accounting tetap hanya lewat undangan** (tanpa pendaftaran terbuka dan tanpa login Google). | Alasan: mencegah akun menumpuk. Aturan ini tidak otomatis berlaku untuk produk yang dijual terbuka (lihat bagian 9). |

## 2. Segmen pelanggan (HIPOTESIS — belum divalidasi)

| Segmen | Pembayar | Pemakai | Masalah utama | Produk |
| --- | --- | --- | --- | --- |
| A. Sekolah dan yayasan swasta | Ketua yayasan / bendahara | Bendahara, kepala sekolah, banyak guru | Pengajuan dana, persetujuan berjenjang, LPJ masih di kertas atau pesan instan | Workspace (+ Accounting) |
| B. Pesantren, masjid, lembaga nirlaba | Pengurus | Bendahara, pengurus | Dana terikat per program, laporan ke donatur | Workspace (+ Accounting) |
| C. UMKM dan toko | Pemilik | Pemilik, kasir | Pembukuan manual, stok, penjualan harian | POS, Accounting |
| D. Kontraktor dan proyek kecil | Pemilik / manajer proyek | Admin proyek | RAB proyek, realisasi biaya | Accounting + Budget |
| E. Akuntan dan konsultan pembukuan | Kantor akuntan | Staf kantor | Banyak klien dengan satu login | Accounting multi-perusahaan |

Tiga ciri pembeda yang menentukan harga dan penjualan:

1. **Jumlah orang yang menyentuh sistem.** Segmen A dan B memiliki puluhan pengguna (guru, panitia); C dan D satu sampai lima.
2. **Pembeli berbeda dari pemakai.** Di A dan B pembeli (ketua yayasan) bukan pemakai harian (bendahara).
3. **Kekuatan alasan berpindah.** Sekolah dan lembaga nirlaba punya kewajiban pelaporan dana; UMKM sering cukup dengan Excel.

**Belum diketahui:** siapa calon pilot nyata, segmen mana dilayani lebih dulu, dan siapa pembeli sebenarnya. Pertanyaan ini harus dijawab sebelum harga dan prioritas final.

## 3. Tiga skenario yang wajib berjalan

| Skenario | Perilaku |
| --- | --- |
| Hanya Workspace | Pengajuan, persetujuan, pencairan, dan LPJ di Workspace. Realisasi dicatat dari pencairan dan bukti LPJ; tidak ada jurnal. |
| Hanya Accounting | Seperti sekarang, termasuk modul Budget yang sudah ada. |
| Keduanya | Pencairan yang disetujui di Workspace menghasilkan transaksi di Accounting melalui pesan terverifikasi; realisasi kembali ke Workspace. |

Kombinasi yang sama berlaku untuk POS dan Accounting: POS mandiri, atau POS yang meneruskan penjualan ke Accounting bila keduanya dimiliki organisasi yang sama.

## 4. Kondisi kode saat ini (fakta per 2026-11-01)

Diperiksa dari migrasi backend Laravel. Ini keadaan nyata, bukan rancangan.

- `users.plan_id` dan `subscriptions.user_id`: paket dan langganan menempel ke **pengguna pemilik**. Tidak ada entitas organisasi.
- `plans.max_users` dan `plans.max_companies`: kuota dihitung dari pemilik; pemilik ikut dihitung dalam kuota pengguna.
- `companies.created_by`: menentukan pemilik langganan sebuah perusahaan.
- `company_users`: keanggotaan orang di perusahaan (`full_access`, `is_owner`; kolom `role` hanya label). Izin per fitur ada di `company_user_permissions`. Tabel peran lama sudah dihapus.
- `tenant_databases.company_id` UNIQUE: satu perusahaan tepat satu database tenant (SQLite lokal, Postgres di produksi).
- Satu orang sudah dapat bergabung ke banyak perusahaan; akun staf lahir lewat undangan email.

Implikasi: untuk Accounting tersedia dasar yang baik (akses per orang, undangan, multi-perusahaan), tetapi **tidak ada tempat** untuk organisasi induk maupun hak pakai per produk.

## 5. Model platform target (RANCANGAN AWAL)

```
users (Finlite ID)
  └─< organization_members >── organizations
                                   ├─< organization_products   (hak pakai: produk, paket, kursi, tanggal)
                                   └─< companies               (unit usaha, untuk produk yang memakai database per unit)
                                          ├─< company_users + company_user_permissions
                                          └─< tenant_databases  (per perusahaan per produk)
```

Tabel baru di database pusat:

| Tabel | Isi minimum |
| --- | --- |
| `organizations` | nama, slug, status, pemilik |
| `organization_members` | organisasi, pengguna, status, tanggal bergabung; unik per pasangan |
| `organization_products` | organisasi, kode produk, paket, batas kursi, tanggal mulai dan akhir, status; unik per organisasi dan produk |

Perubahan pada tabel yang ada:

- `companies` mendapat `organization_id`.
- `tenant_databases` diubah dari unik per `company_id` menjadi unik per (`company_id`, produk) bila sebuah produk memakai database per perusahaan.
- `users.plan_id` dan `subscriptions.user_id` dihapus setelah kode membaca dari organisasi (tanpa lapisan kompatibilitas karena belum ada pengguna produksi).
- Izin diberi awalan produk (contoh `workspace.proposal.submit`) pada matriks izin yang sudah ada.

Migrasi: setiap pemilik yang sudah punya perusahaan otomatis memperoleh satu organisasi berisi perusahaannya; paketnya menjadi satu baris `organization_products` untuk Accounting.

Pola langganan: **bundel hanyalah aturan harga**, bukan struktur data. Pelanggan yang hanya membeli POS memiliki satu baris hak pakai; menambah produk berarti menambah baris.

## 6. Pola penyimpanan data per produk (HIPOTESIS)

| Produk | Pola | Alasan |
| --- | --- | --- |
| Accounting | Database per perusahaan (tetap) | Sudah berjalan; isolasi kuat; tenant relatif sedikit. |
| POS | Database bersama dengan `organization_id` | Ribuan toko kecil dengan transaksi sering; database per toko mahal dan sulit dimigrasi. |
| WMS, CRM | Database bersama dengan `organization_id` | Pola serupa POS. |
| Workspace | Belum ditentukan; lihat keputusan terbuka | Volume per tenant lebih kecil daripada POS, tetapi ia produk mandiri. |

Risiko database bersama: satu kueri yang lupa menyaring `organization_id` membocorkan data antarpelanggan. Wajib ada filter tingkat model dan tes isolasi khusus sebelum produk mana pun memakai pola ini.

Secara kode, produk baru dapat berada di repositori backend yang sama sebagai modul terpisah dengan koneksi database sendiri dan tanpa tabel yang dibagi. Pemisahan menjadi layanan fisik dapat dilakukan nanti tanpa mengubah kontrak.

## 7. Batas Workspace dan Accounting

- **Workspace memiliki proses:** pengajuan, persetujuan, reservasi, pencairan, LPJ.
- **Accounting memiliki pembukuan:** jurnal, periode, laporan keuangan.
- **Kode anggaran Workspace tidak memakai akun (COA) Accounting.** Organisasi yang hanya memakai Workspace tidak punya COA. Workspace memiliki daftar kode anggaran sendiri.
- **Pemetaan** kode anggaran ke akun disimpan di satu tabel jembatan yang hanya diisi saat pelanggan menyambungkan kedua produk.
- Modul Budget di Accounting tetap untuk pelanggan yang hanya memakai Accounting. Bila Workspace tersambung, sumber anggaran ditentukan satu pihak (jangan diisi dua kali). Sumber yang dipilih adalah **keputusan terbuka**.
- **Sambungan memakai pesan, bukan tabel bersama.** Contoh: Workspace mengirim "pencairan disetujui, nominal, kode anggaran"; Accounting membuat transaksi. Setiap pesan memiliki ID unik (idempotency) agar pengiriman ulang tidak menggandakan jurnal. Pesan yang gagal masuk antrean rekonsiliasi.
- Definisi angka (allocated, reserved, committed, actual, disbursed, outstanding advance) pada dokumen 02 tetap berlaku di Workspace mandiri. Pada skenario "hanya Workspace", sumber *actual* adalah pencairan dan bukti LPJ yang diverifikasi, bukan jurnal.

## 8. Urutan implementasi yang diusulkan

| Tahap | Isi | Syarat selesai |
| --- | --- | --- |
| **P — Platform** | Finlite ID, organisasi, hak pakai per produk. Accounting dipindahkan ke struktur ini. | Pelanggan Accounting yang ada berjalan tanpa perubahan perilaku; kuota dibaca dari hak pakai; tes isolasi lulus. |
| **1 — Workspace mandiri** | Anggota organisasi, kode anggaran, pengajuan, persetujuan berjenjang, pencairan, LPJ, laporan. Tanpa Accounting. | Satu pilot nyata dapat menjalankan siklus penuh; syarat "siap dibangun" pada dokumen 04 terpenuhi. |
| **2 — Jembatan Workspace-Accounting** | Pemetaan kode anggaran dan pesan idempotent. | Pencairan menghasilkan transaksi sekali; perbedaan muncul sebagai exception. |
| **3+ — POS, WMS, CRM** | Mengikuti dokumen 06 dan evaluasi setelah pilot. | Ditentukan setelah Tahap 1 menghasilkan pelajaran. |

Sisa pekerjaan kecil Accounting (izin impor, noise 403 dashboard untuk staf tanpa izin dashboard) dapat dikerjakan sebelum atau sesudah Tahap P dan tidak menghalanginya.

Urutan ini adalah hipotesis prioritas, **bukan jadwal**.

## 9. Pilot dan strategi pengujian (keputusan 2026-11-01)

**Pilot pertama adalah sekolah milik pemilik produk**, memakai data dan aturan sekolah itu. Pengujian tidak mengandalkan pihak luar:

1. **Agen AI memerankan pengguna** (guru, kepala kurikulum, kepala sekolah, bendahara, auditor) berdasarkan struktur dan aturan sekolah sebenarnya, dengan skrip skenario normal dan skenario gagal (persetujuan ganda, melewati batas kewenangan, revisi berulang, pembatalan, pengiriman ulang).
2. **Pemilik produk menguji secara manual satu per satu** setelah tiap tahap, untuk menilai rasa pakai yang tidak terjangkau agen.
3. **Bahan nyata** yang dikumpulkan lebih dulu: struktur organisasi, form pengajuan, contoh RAB, aturan batas nominal dan siapa menyetujui apa, contoh LPJ, dan bagan akun anggaran.

Batas yang harus diingat:

- Agen berperilaku rapi; pengguna sungguhan lupa mengunggah bukti, salah mengisi, dan bingung istilah. Hasil tes agen **tidak membuktikan** kemudahan pakai.
- Satu sekolah adalah satu sampel. Aturan sekolah lain bisa berbeda; sebelum alur persetujuan dikunci, tambahkan 2–3 percakapan singkat dengan sekolah atau yayasan lain.
- Pilot internal tidak membuktikan kesediaan membayar.
- **Data nyata sekolah (nama, nominal, dokumen) tidak boleh masuk repositori ini** karena bersifat publik; simpan di luar repo atau anonimkan.

## 10. Keputusan masih terbuka

1. ~~Calon pilot nyata~~ — sekolah milik pemilik produk (bagian 9). Segmen yang dilayani lebih dulu masih terbuka.
2. **Pemetaan unit ke company:** apakah setiap sekolah/unit selalu sama dengan satu perusahaan berpembukuan sendiri, atau sebuah unit hanya bagian organisasi di dalam Workspace tanpa pembukuan.
3. **Kursi pegawai Workspace:** terpisah dari kursi staf Accounting (kecenderungan saat ini), atau pegawai tidak dihitung kursi dan harga per unit. Termasuk skema lisensi per organisasi, per pegawai aktif, atau per paket unit.
4. **Satu orang di beberapa organisasi** (konsultan, auditor): skema mengizinkan, tetapi perlu desain pemilihan organisasi di antarmuka.
5. **Pendaftaran terbuka untuk produk yang dijual mandiri** (terutama POS): mekanisme verifikasi yang mencegah akun menumpuk, tanpa membuka pembuatan database tenant Accounting secara bebas.
6. **Pola data Workspace:** database per organisasi, atau bersama dengan `organization_id`.
7. **Sumber anggaran saat Workspace dan Accounting tersambung:** Workspace atau modul Budget.
8. Pertanyaan teknis dan akuntansi pada dokumen 02 dan 04 (rumus available budget, reservasi saat submitted atau approved, definisi actual untuk uang muka dan AP, dan seterusnya).
