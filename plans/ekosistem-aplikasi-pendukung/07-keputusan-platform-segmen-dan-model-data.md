# Keputusan Arah: Platform, Segmen, dan Model Data

> **STATUS: KEPUTUSAN ARAH (diperbarui 2026-11-01) — BELUM DIIMPLEMENTASIKAN.**
>
> Dokumen ini mencatat hasil diskusi pemilik produk. Bagian "Keputusan" mengikat arah rancangan; bagian "Hipotesis" dan "Keputusan masih terbuka" belum final. Skema tabel di bawah adalah rancangan awal, bukan migrasi yang sudah ada.
>
> Revisi: rancangan awal sempat mengusulkan lapisan Organisasi baru. Usulan itu **dibatalkan** karena backend, database, dan tenant mengikuti Finlite (tenant per perusahaan, pemilik sebagai pemegang langganan); yang ditambahkan hanya dimensi produk.

## 1. Keputusan yang diambil

| # | Keputusan | Dampak |
| --- | --- | --- |
| 1 | **Setiap produk harus lengkap tanpa produk lain.** Integrasi hanya tambahan opsional. | Workspace, POS, WMS, dan CRM tidak boleh bergantung pada tabel atau modul Accounting. |
| 2 | **Workspace dijual dan dipakai mandiri.** Sekolah boleh hanya memakai Workspace untuk melacak anggaran; idealnya bersama Accounting, tetapi semua kombinasi harus berjalan. | Workspace memiliki tabel anggaran/RAB sendiri; tidak memakai modul Budget di Accounting. |
| 3 | **POS (dan WMS, CRM) dijual terpisah.** Pelanggannya boleh bukan pelanggan Accounting. | Pemilik dapat mendaftar dan membeli satu produk saja. |
| 4 | **Backend dan database mengikuti Finlite.** Satu backend Laravel modular; tenant tetap **per perusahaan**; pemilik (client) tetap pemegang langganan. **Tidak ada entitas Organisasi baru.** | Perubahan fondasi kecil: menambah dimensi produk pada langganan, tenant, dan izin. |
| 5 | **Langganan per pemilik per produk.** Pelanggan yang hanya membeli POS memiliki satu langganan POS; menambah produk berarti menambah langganan. Bundel hanyalah aturan harga. | `plans` dan `subscriptions` mendapat dimensi produk. |
| 6 | **Tenant dibuat per perusahaan per produk dan disiapkan saat produk diaktifkan.** Sekolah yang hanya berlangganan Workspace mendapat tenant berisi tabel Workspace saja; tabel Accounting dibuat nanti bila ia berlangganan Accounting. | `tenant_databases` unik per (perusahaan, produk), dengan jalur migrasi sendiri per produk. |
| 7 | **Satu yayasan = satu pembukuan.** Sekolah dan kantor yayasan adalah unit di dalam satu perusahaan, bukan perusahaan terpisah. | Unit dimodelkan sebagai dimensi (cost center) di Accounting dan struktur organisasi di Workspace. |
| 8 | **Kursi Workspace memakai pita jumlah pegawai aktif per perusahaan**, bukan tarif per pegawai. | Tagihan pelanggan dapat diprediksi; batas pita ditentukan setelah jumlah pegawai sekolah pilot diketahui. |
| 9 | **Satu akun orang (Finlite ID) untuk semua produk.** Hak akses melekat ke orang per fitur, bukan peran. | Matriks izin yang sudah ada dipakai ulang dengan awalan per produk. |
| 10 | **Accounting tetap hanya lewat undangan** (tanpa pendaftaran terbuka dan tanpa login Google). | Alasan: mencegah akun menumpuk. Tidak otomatis berlaku untuk produk yang dijual terbuka (bagian 10). |

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

Skala yang diperkirakan: **ratusan pelanggan dalam satu tahun pun belum pasti**. Rancangan tidak perlu mengoptimalkan untuk ribuan tenant sejak awal.

## 3. Tiga skenario yang wajib berjalan

| Skenario | Perilaku |
| --- | --- |
| Hanya Workspace | Pengajuan, persetujuan, pencairan, dan LPJ di Workspace. Realisasi dicatat dari pencairan dan bukti LPJ; tidak ada jurnal. |
| Hanya Accounting | Seperti sekarang, termasuk modul Budget yang sudah ada. |
| Keduanya | Pencairan yang disetujui di Workspace menghasilkan transaksi di Accounting melalui pesan terverifikasi; realisasi kembali ke Workspace. |

Kombinasi yang sama berlaku untuk POS dan Accounting.

## 4. Kondisi kode saat ini (fakta per 2026-11-01)

Diperiksa dari migrasi dan kode backend Laravel. Ini keadaan nyata, bukan rancangan.

- `users.plan_id` dan `subscriptions.user_id`: paket dan langganan menempel ke **pengguna pemilik**. Tidak ada dimensi produk.
- `plans.max_users` dan `plans.max_companies`: kuota dihitung dari pemilik; pemilik ikut dihitung dalam kuota pengguna.
- `companies.created_by`: menentukan pemilik langganan sebuah perusahaan.
- `company_users`: keanggotaan orang di perusahaan (`full_access`, `is_owner`; kolom `role` hanya label). Izin per fitur ada di `company_user_permissions`.
- `tenant_databases.company_id` UNIQUE: satu perusahaan tepat satu tenant. Di Postgres, tenant adalah **satu schema per perusahaan di dalam satu database** (`PostgresTenantStorage`), bukan database terpisah; di lokal berupa berkas SQLite.
- Satu orang sudah dapat bergabung ke banyak perusahaan; akun staf lahir lewat undangan email.

Implikasi: dasarnya sudah cocok. Yang kurang hanya dimensi produk pada langganan, tenant, dan izin.

## 5. Perubahan fondasi (Tahap P) — RANCANGAN AWAL

```
pemilik (client) ──< langganan (per produk) ──> paket (per produk)
       │
       └──< companies ──< company_users + company_user_permissions   (izin berawalan produk)
                  └──< tenant_databases   unik per (company, produk)
                            ├─ schema accounting
                            ├─ schema workspace
                            └─ schema pos ...
```

| Perubahan | Rincian |
| --- | --- |
| `plans` | Menambah kolom produk (Accounting, Workspace, POS, ...). Batas kuota memakai satuan masing-masing produk (Workspace: pita pegawai). |
| `subscriptions` | Menambah kolom produk; satu pemilik dapat memiliki beberapa langganan aktif dengan produk berbeda. Cakupannya perusahaan milik pemilik itu. |
| `users.plan_id` | Dihapus setelah kode membaca dari langganan per produk. Tanpa lapisan kompatibilitas karena belum ada pengguna produksi. |
| `tenant_databases` | Menambah kolom produk; unik per (perusahaan, produk). Lokasi tenant tetap disimpan di tabel ini. |
| Izin | Awalan per produk (contoh `workspace.proposal.submit`) pada matriks izin yang sudah ada. |
| Aktivasi produk | Mengaktifkan langganan produk menyiapkan tenant produk itu (membuat schema dan menjalankan migrasi produk tersebut). Perusahaan yang sudah ada dipetakan sebagai tenant produk Accounting. |
| Penghentian langganan | Schema produk **tidak dihapus**; akses dikunci atau dibuat baca-saja sesuai kebijakan langganan, agar data tidak hilang. |

Entitas Organisasi (induk beberapa perusahaan dengan satu penagihan) **ditunda**. Tinjau lagi hanya bila ada pelanggan yang membutuhkan beberapa pemilik atau penagihan lintas pemilik.

## 6. Data dan skala tenant

Semua produk mengikuti pola Finlite: tenant per perusahaan per produk, satu schema per tenant dalam satu database Postgres. Dengan perkiraan ratusan pelanggan, satu database cukup. Pembatasan yang perlu diketahui dan penanganannya:

| Masalah saat tenant bertambah | Penanganan (dibangun bila dibutuhkan, bukan sekarang) |
| --- | --- |
| Migrasi berjalan satu per satu, makin lama | Jalankan paralel dan berkelompok; tampilkan status per tenant |
| Ribuan schema memberatkan katalog Postgres | Pecah ke beberapa database; `tenant_databases` menyimpan lokasi tenant |
| Satu tenant besar memperlambat yang lain | Pindahkan tenant itu ke database sendiri |
| Lampiran (kuitansi, LPJ) membengkakkan database | Simpan berkas di penyimpanan objek, database hanya menyimpan referensi |
| Data lama menumpuk | Arsip per periode |

Aturan yang dijaga sejak sekarang agar pemecahan itu murah: kode produk tidak boleh mengasumsikan semua tenant berada di database yang sama; selalu menemukan tenant lewat `tenant_databases`.

**Catatan POS:** POS bertransaksi lebih sering per tenant daripada Workspace. Perlu diuji beban pada tenant POS sebelum menyatakan pola ini cukup; bila tidak, pola alternatif dievaluasi saat POS direncanakan.

## 7. Batas Workspace dan Accounting

- **Workspace memiliki proses:** pengajuan, persetujuan, reservasi, pencairan, LPJ.
- **Accounting memiliki pembukuan:** jurnal, periode, laporan keuangan.
- **Kode anggaran Workspace tidak memakai akun (COA) Accounting.** Organisasi yang hanya memakai Workspace tidak punya COA.
- **Unit sekolah** di Workspace adalah bagian struktur organisasi; di Accounting adalah dimensi (cost center) pada satu pembukuan yayasan. Pemetaan unit Workspace ke dimensi Accounting disimpan di tabel jembatan.
- **Pemetaan** kode anggaran ke akun disimpan di satu tabel jembatan yang hanya diisi saat pelanggan menyambungkan kedua produk.
- Modul Budget di Accounting tetap untuk pelanggan yang hanya memakai Accounting. Bila Workspace tersambung, sumber anggaran ditentukan satu pihak (jangan diisi dua kali). Sumber yang dipilih adalah **keputusan terbuka**.
- **Sambungan memakai pesan, bukan tabel bersama.** Contoh: Workspace mengirim "pencairan disetujui, nominal, kode anggaran"; Accounting membuat transaksi. Setiap pesan memiliki ID unik (idempotency) agar pengiriman ulang tidak menggandakan jurnal. Pesan yang gagal masuk antrean rekonsiliasi.
- Karena tenant tiap produk adalah schema terpisah, kedua produk tidak berbagi tabel meski dimiliki perusahaan yang sama.
- Definisi angka (allocated, reserved, committed, actual, disbursed, outstanding advance) pada dokumen 02 tetap berlaku. Pada skenario "hanya Workspace", sumber *actual* adalah pencairan dan bukti LPJ yang diverifikasi, bukan jurnal.

## 8. Urutan implementasi yang diusulkan

| Tahap | Isi | Syarat selesai |
| --- | --- | --- |
| **P — Dimensi produk** | Produk pada paket, langganan, tenant, dan izin; aktivasi produk menyiapkan tenant produk. Accounting dipetakan sebagai produk pertama. | Pelanggan Accounting yang ada berjalan tanpa perubahan perilaku; kuota dibaca dari langganan per produk; tes aktivasi dan penguncian lulus. |
| **1 — POS mandiri** (keputusan 2026-11-01: produk pertama) | Mengikuti fase 1–4 dokumen 06: katalog, stok outlet, kasir, shift, retur, laporan, lalu Device Bridge. Tanpa Accounting. | Kriteria penerimaan MVP dokumen 06 bagian 10 terpenuhi; syarat "siap dibangun" dokumen 04 terpenuhi. |
| **2 — Workspace mandiri** | Anggota, pita pegawai, kode anggaran, pengajuan, persetujuan berjenjang, pencairan, LPJ, laporan. Tanpa Accounting. | Pilot sekolah (bagian 9) menjalankan siklus penuh. |
| **3 — Jembatan ke Accounting** | Pemetaan dan pesan idempotent untuk POS dan Workspace. | Penjualan atau pencairan menghasilkan transaksi sekali; perbedaan muncul sebagai exception. |
| **4+ — WMS, CRM** | Evaluasi setelah produk sebelumnya berjalan. | Ditentukan setelah pelajaran dari POS dan Workspace. |

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

1. **Batas pita pegawai Workspace** dan harganya, setelah jumlah guru dan pegawai sekolah pilot diketahui.
2. **Segmen yang dilayani lebih dulu** setelah pilot.
3. **Pendaftaran terbuka untuk produk yang dijual mandiri** (terutama POS): mekanisme verifikasi yang mencegah akun menumpuk, tanpa membuka pembuatan tenant Accounting secara bebas.
4. **Sumber anggaran saat Workspace dan Accounting tersambung:** Workspace atau modul Budget.
5. **Kecukupan pola tenant untuk POS** (uji beban sebelum POS direncanakan).
6. **Kebijakan penghentian langganan:** kunci total atau baca-saja, dan lama retensi data.
7. Pertanyaan teknis dan akuntansi pada dokumen 02 dan 04 (rumus available budget, reservasi saat submitted atau approved, definisi actual untuk uang muka dan AP, dan seterusnya).
