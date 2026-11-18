# 13 — Rencana uji simulasi menyeluruh Finlite Gudang

> **Status pada 18 November 2026 masih berupa rencana.** Eksekusi dijadwalkan pada Fase 6 setelah implementasi cakupan versi yang dipilih siap. Keputusan pemilik menetapkan seluruh pengujian program memakai simulasi pada fase akhir. Pilot fisik tujuh hari dijadwalkan kemudian saat gudang tersedia. Kriteria penerimaan program mengikuti hasil simulasi dalam dokumen ini.

Rencana ini mengikuti [rencana fase](11-finlite-gudang-rencana-fase.md), [keputusan dan spesifikasi awal](12-finlite-gudang-fase0-wawancara-dan-spesifikasi-awal.md), serta memakai struktur [rencana pengujian Kasir](09-rencana-testing-menyeluruh.md) sebagai acuan. Retur dan multi-satuan direncanakan pada Fase 2. Karantina dan koreksi dokumen termasuk kendali inti Fase 1. Integrasi Accounting dan Project hanya diuji bila termasuk cakupan rilis yang dipilih.

Delapan skenario Playwright dan tes backend yang pernah lulus disimpan sebagai bukti historis commit yang diuji. Kampanye dalam dokumen ini dijadwalkan pada Fase 6. Putaran pertama diikuti perbaikan dan pengujian ulang sampai kriteria penerimaan terpenuhi. Fase 0–5 menyiapkan implementasi, kontrak dan skenario. Eksekusi pengujian program mengikuti jadwal fase akhir yang ditetapkan pemilik.

## Lingkungan dan bukti versi

1. Tentukan daftar fitur dan integrasi yang benar-benar termasuk rilis. Buat matriks skenario, pemilik, status dan tautan bukti sebelum menjalankan. Fitur yang belum siap atau tidak termasuk diberi status **belum siap** atau **di luar cakupan**, tidak pernah dianggap lulus. Fitur wajib yang belum siap menghalangi kelulusan.
2. Catat SHA penuh frontend, backend, definisi workflow dan setiap repositori integrasi yang dipakai. Checkout setiap repositori pada SHA tersebut dalam GitHub Actions dan catat SHA aktual di laporan. Pasangan SHA harus sama sepanjang satu putaran penerimaan. Jika ada perbaikan, catat pasangan baru dan ulangi skenario terdampak serta regresinya.
3. Gunakan tenant dan akun sintetis baru yang terisolasi per putaran dan per pekerjaan paralel. Jangan memakai data pelanggan, kredensial produksi atau database produksi. Tetapkan waktu dan zona Asia/Jakarta, nomor referensi dan data awal yang dapat direproduksi. Bersihkan sumber daya sementara setelah bukti aman.
4. Jalankan seluruh tes di GitHub Actions. Dependensi dipasang pada runner CI, tanpa kewajiban memasang atau menyiapkan dependensi di komputer pemilik. Simpan hasil job, versi, konfigurasi, data sintetis dan referensi artefak untuk reproduksi.
5. Kondisi saat ini adalah Playwright ukuran Pixel 7 dengan satu worker, SQLite sementara, akun pemilik dan trace serta screenshot saat gagal. `finlite-gudang/.github/workflows/inventory.yml` memasang dependensi di runner, menjalankan `npm run lint`, `npm run build` dan `npm run e2e`, serta mematok backend pada SHA tertentu. Untuk penerimaan, perlu memperluas konfigurasi dan workflow agar SHA pasangan dapat dicatat dan diulang, akun terbatas tersedia, bukti sukses juga dikumpulkan, dan skenario baru dijalankan. Perluasan ini dicatat sebagai pekerjaan persiapan Fase 6.
6. Gunakan job PostgreSQL 16 yang sudah tersedia pada CI backend untuk penguncian, transaksi bersamaan, migrasi dan integritas buku stok. Perluas cakupannya sesuai skenario final. Pertahankan uji konkurensi melalui dua proses independen pada stok yang sama. Catat versi PostgreSQL dan hasilnya. Siapkan juga putaran Playwright melalui backend dengan PostgreSQL uji agar alur browser sampai penyimpanan memakai mesin database yang sesuai Neon. Putaran SQLite yang sudah ada menjadi referensi konfigurasi awal.

Pada fase akhir, tambahkan putaran ke deployment uji Vercel/Render/Neon yang tercatat pada manifest kampanye. Catat URL Gudang dan aplikasi tujuan, versi deployment, konteks tenant sintetis dan branch/schema database uji yang dipakai. Playwright dari runner GitHub menjalankan alur login sampai ekspor pada URL tersebut dengan data sintetis yang terisolasi. Cocokkan commit deployment dengan manifest dan periksa koneksi API, autentikasi lintas domain, migrasi, penyimpanan foto serta unduhan laporan. Gunakan nama resource berawalan ID kampanye agar pembersihan menyasar resource uji yang dibuat.

## Pembagian kerja AI dan biaya

Gunakan GPT-6.1 Terra dengan reasoning low selama tersedia sebagai pilihan sub-agent termurah dalam sesi, mengikuti preferensi pemilik. Periksa ketersediaan model saat kampanye dimulai dan catat pilihan aktual. Playwright dan tes backend menjalankan pemeriksaan deterministik di CI. Mulai dengan satu pekerja, lalu jalankan maksimal tiga pekerja bila paket independen siap. Maksimal empat slot aktif mencakup satu agen induk dan tiga pekerja.

| Peran | Tugas |
| --- | --- |
| Induk | Kunci cakupan dan SHA, koordinasi CI, gabungkan bukti dan putuskan status berdasarkan hasil. |
| Pekerja 1 | Alur dokumen dan perhitungan stok serta ekspor. |
| Pekerja 2 | Izin, isolasi tenant, keamanan dan kondisi gagal. |
| Pekerja 3 | PostgreSQL, persaingan transaksi, idempotensi dan integrasi yang termasuk. |

Berikan tiap pekerja instruksi ringkas, referensi dan hasil yang relevan, tanpa menyalin seluruh riwayat percakapan. Batasi jumlah putaran dan durasi job, gunakan artefak kegagalan untuk diagnosis, dan ulangi hanya cakupan terdampak sebelum regresi akhir. Tugas independen dapat paralel dengan tenant, data dan resource masing-masing. Tahapan dalam satu siklus dokumen, termasuk transaksi yang bergantung pada saldo sebelumnya, berjalan berurutan. Tes persaingan justru menggunakan permintaan serentak yang disengaja pada tenant khusus.

## Peran dan data sintetis

Buat lima akun berbeda dengan hak sesuai matriks izin yang disetujui. Catat identitas pengguna dan izin aktual pada setiap sesi.

| Identitas | Akses yang diharapkan |
| --- | --- |
| Pemilik | Seluruh gudang, laporan dan pengaturan. |
| Staf A | Operasi yang diberikan pada gudang A, tanpa akses gudang B atau persetujuan khusus. |
| Staf B | Operasi yang diberikan pada gudang B, tanpa akses gudang A atau persetujuan khusus. |
| Penyetuju | Izin khusus menyetujui penyesuaian dan selisih yang ditugaskan. |
| Orang luar | Tenant berbeda, tidak memiliki akses pada tenant uji. |

Siapkan barang `SIM-BAUT-01` dengan satuan dasar PCS dan faktor tersimpan 1 BOX = 12 PCS, gudang A dan B, lokasi terima, simpan dan karantina pada A serta lokasi simpan pada B. Buat pemasok dan pelanggan rekaan. Gunakan tujuh tanggal dokumen berturut-turut pada rentang yang diterima kontrak aplikasi. Waktu simulasi untuk langganan dan kedaluwarsa dikendalikan di lingkungan uji. Seluruh tanggal diproses dalam satu kampanye. Catat waktu acuan dan zona Asia/Jakarta agar hasil tanggal dapat diulang.

## Alur lengkap dari saldo awal sampai ekspor

### Persiapan melalui antarmuka aplikasi

| ID | Langkah melalui antarmuka | Hasil yang diperiksa |
| --- | --- | --- |
| AW-01 | Buka aplikasi, daftar akun sintetis dan verifikasi dengan kode dari kotak email uji atau transport email uji | Akun aktif, percobaan kode salah/kedaluwarsa ditolak, masa coba Gudang sesuai kontrak |
| AW-02 | Masuk, buat perusahaan Gudang dan pilih perusahaan aktif | Tenant, produk, konteks perusahaan dan batas paket benar |
| AW-03 | Buat gudang A/B, lokasi terima/simpan/karantina/rusak, pemasok dan pelanggan | Identitas dan hierarki tersimpan, duplikasi serta lokasi tidak valid ditolak |
| AW-04 | Buat barang, kategori, barcode, satuan dasar dan konversi BOX | SKU unik dan faktor 12 tersimpan, input keliru diberi pesan yang sesuai |
| AW-05 | Buat staf A, staf B dan penyetuju dengan izin berbeda | Sesi memakai identitas terpisah, daftar gudang dan tindakan sesuai izin |
| AW-06 | Unduh templat impor, isi data sintetis valid dan salah, unggah serta periksa pratinjau | Kolom templat terbaca, baris gagal ditandai, jumlah baris valid sesuai masukan |
| AW-07 | Simpan saldo awal, lalu jalankan tabel transaksi utama di bawah | Saldo awal masuk satu kali dan setiap tahap mempertahankan angka pembanding |
| AW-08 | Periksa kartu stok, tugas, pencarian dan seluruh laporan | Dokumen, status, saldo lokasi, gudang dan audit cocok dengan buku harapan |
| AW-09 | Ekspor Excel dan CSV yang didukung, baca ulang semua baris hasil unduhan | Isi, filter, jumlah baris dan total cocok dengan perhitungan independen |
| AW-10 | Keluar, masuk kembali dengan identitas terbatas dan ulangi akses laporan/ekspor | Data tersimpan konsisten dan hanya gudang berizin yang dapat dibaca |

Transport email uji menjalankan kode verifikasi melalui alur aplikasi. Pemindai memakai gambar barcode sintetis, aliran kamera simulasi dan kasus izin kamera ditolak. Dokumentasikan cakupan pemindai yang dijalankan.

### Rangkaian transaksi dan saldo pembanding

Tabel ini adalah buku harapan yang ditetapkan sebelum menjalankan aplikasi. Angka dihitung secara independen dari peristiwa bisnis di bawah dan dikunci sebelum dibandingkan dengan hasil aplikasi. Saldo A mencakup karantina. Barang dalam perjalanan ditampilkan terpisah sampai selisih diselesaikan. Setiap dokumen menyimpan referensi asal, aktor, tanggal, status dan jumlah dalam satuan dasar.

| Hari | Operasi dan pemeriksaan | A PCS | Dalam perjalanan PCS | B PCS | Total PCS |
| --- | --- | ---: | ---: | ---: | ---: |
| 1 | Impor saldo awal 20 PCS ke A. Periksa pratinjau dan posting satu kali. | 20 | 0 | 0 | 20 |
| 2 | Buat PO 2 BOX × 12 = 24 PCS, simpan draf dan konfirmasi. | 20 | 0 | 0 | 20 |
| 2 | Terima sebagian 1 BOX = 12 PCS di lokasi terima A. PO masih terbuka dengan sisa 12 PCS. | 32 | 0 | 0 | 32 |
| 3 | Terima sisa 12 PCS dan putaway seluruh 24 PCS dari lokasi terima ke simpan A. Putaway mengubah lokasi, bukan total. | 44 | 0 | 0 | 44 |
| 4 | Kirim transfer 10 PCS dari A ke B. Sebelum penerimaan, 10 masih dalam perjalanan. | 34 | 10 | 0 | 44 |
| 4 | B menerima aktual 9 PCS. Catat kekurangan 1 PCS dengan status menunggu keputusan. | 34 | 1 | 9 | 44 |
| 4 | Penyetuju menyelesaikan selisih dengan mengembalikan 1 PCS ke A. | 35 | 0 | 9 | 44 |
| 5 | Keluarkan 6 PCS dari A kepada pelanggan. | 29 | 0 | 9 | 38 |
| 6 | Retur pelanggan 2 PCS merujuk pengeluaran, 1 baik ke simpan A dan 1 ke karantina A. | 31 | 0 | 9 | 40 |
| 7 | Retur 3 PCS dari simpan A ke pemasok merujuk penerimaan. | 28 | 0 | 9 | 37 |
| 7 | Ajukan penyesuaian -1 PCS di simpan A dengan alasan, tunggu persetujuan. | 28 | 0 | 9 | 37 |
| 7 | Penyetuju menyetujui penyesuaian. | 27 | 0 | 9 | 36 |

Saldo akhir dihitung sebagai 20 + 24 - 6 + 2 - 3 - 1 = **36 PCS**, terdiri dari **A 27 dan B 9**. A menyimpan 26 PCS layak jual dan 1 PCS karantina. Total layak jual kedua gudang adalah **35 PCS**. Mutasi putaway berpasangan dan transfer beserta penyelesaian selisih mempertahankan total perusahaan.

Pada setiap langkah periksa status dan rincian dokumen, buku mutasi, saldo lokasi dan gudang, serta audit. Draf, permintaan persetujuan dan penolakan tidak boleh mengubah stok. Pastikan faktor 12 tersimpan pada dokumen meskipun master satuan kemudian berubah. Verifikasi barang karantina tidak dapat dikeluarkan sebagai barang layak tanpa alur dan izin yang sesuai. Periksa tanggal, asal retur dan koreksi, serta tidak ada jumlah hilang atau terhitung ganda.

## Matriks pengujian

Setiap baris memiliki data awal, langkah, hasil yang diharapkan dan bukti. Skenario fitur masa depan baru diberi **lulus** setelah fitur tersedia dan hasilnya benar pada SHA rilis.

| ID | Area | Pemeriksaan penerimaan |
| --- | --- | --- |
| UJ-01 | Master dan impor | Buat barang, barcode, pemasok, pelanggan, gudang dan lokasi. Impor campuran baris valid dan tidak valid, periksa pratinjau, pelaporan per baris dan hasil tanpa duplikasi. |
| UJ-02 | Dokumen dan draf | Buat, ubah, batalkan draf, posting dan coba posting ulang. Draf tidak memutasi saldo, nomor unik dan atomik, dokumen terposting tidak dihapus atau diubah diam-diam. |
| UJ-03 | Penerimaan | Terima langsung dan dari PO sebagian 12 + 12. Cek sisa, over-receipt sesuai aturan, bukti setiap kiriman, input tidak valid dan pembatalan yang sesuai. |
| UJ-04 | Putaway | Pindah dari lokasi terima ke simpan, periksa mutasi lokasi berpasangan dan total tetap. Tolak lokasi, jumlah atau izin yang tidak sah. |
| UJ-05 | Transfer | Periksa draf, kirim, dalam perjalanan, terima tepat, kurang dan lebih. Uji keputusan selisih, termasuk pengembalian kekurangan ke A, tanpa kehilangan atau menggandakan barang. Kasus surplus harus mengikuti aturan yang disetujui dan tidak menciptakan stok diam-diam. |
| UJ-06 | Pengeluaran dan koreksi | Pengeluaran 6 PCS, saldo tidak cukup, alasan dan dokumen balik yang merujuk asal. Periksa jejak aktor, tanggal dan tidak ada perubahan saldo ganda. |
| UJ-07 | Retur dan kondisi | Retur pelanggan sebagian baik dan karantina, retur pemasok terhadap penerimaan, batas jumlah dan referensi asal. Coba keluar atau pindah dari karantina dengan dan tanpa izin. |
| UJ-08 | Multi-satuan | Faktor 12, konversi dan pembulatan sesuai kontrak, jumlah input dan dasar tersimpan, perubahan master tidak mengubah dokumen lama, penolakan satuan atau faktor tidak valid. |
| UJ-09 | Penyesuaian dan opname | Alasan wajib, pengajuan, penolakan dan persetujuan oleh identitas berbeda. Hitung buta, hitung ulang, selisih per lokasi dan transaksi selama opname sesuai aturan. Saldo berubah hanya saat keputusan sah. |
| UJ-10 | Batch dan FEFO | Penerimaan beberapa lot dan tanggal kedaluwarsa, saldo per lot, saran lot paling dekat kedaluwarsa, karantina, penelusuran maju-mundur dan recall. Uji barang tanpa batch dan pengecualian yang diizinkan. |
| UJ-11 | Izin dan tenant | Uji setiap identitas lewat UI dan permintaan API langsung. Staf A tidak membaca atau menulis B, staf B tidak membaca atau menulis A, orang luar tidak mengakses tenant uji meski mengganti ID. Aksi persetujuan terbatas dan penolakan tidak mengubah data. |
| UJ-12 | Paralel dan idempotensi | Dua pengeluaran bersamaan untuk stok terakhir pada PostgreSQL 16 menghasilkan paling banyak satu keberhasilan sesuai stok. Nomor unik, saldo tidak negatif. Ulangi kunci idempoten setelah respons hilang dan permintaan bersamaan, hanya satu efek. Kunci sama dengan payload berbeda ditolak sesuai kontrak. |
| UJ-13 | Tanggal dan periode | Transaksi bertanggal lampau dan tujuh tanggal sintetis menghasilkan urutan kartu stok dan laporan periode yang benar. Uji batas hari WIB, tanggal tidak sah dan periode terkunci sesuai kontrak. |
| UJ-14 | Laporan dan ekspor | Bandingkan seluruh baris XLSX yang diparsing dengan buku harapan independen dan database. Validasi isi lembar, jumlah baris dan total. Uji saldo, mutasi, lokasi, kondisi, rentang tanggal, filter, pengurutan dan semua halaman. Pastikan ekspor tidak bocor tenant atau gudang terlarang, termasuk percobaan akses langsung. |
| UJ-15 | Operasi Fase 3 | Bila dipilih dan sudah tersedia, uji reservasi, pick list, short pick, packing dan pembatalan terhadap stok tersedia serta dokumen asal. Status tetap direncanakan sampai versi yang dipilih mengimplementasikannya. |
| UJ-16 | Integrasi Accounting | Bila termasuk rilis, cocokkan pesan dan jurnal terhadap dokumen sumber, kuantitas dan nilai sesuai kontrak. Uji kirim ulang, duplikasi, kegagalan, pemetaan dan periode terkunci. Gudang memiliki kuantitas dan Accounting memiliki nilai. |
| UJ-17 | Integrasi Project | Bila termasuk rilis, cocokkan permintaan, pengiriman, penerimaan, pemakaian dan pengembalian sesuai kontrak dan identitas sumber. Pisahkan status penerimaan dari pemakaian proyek. Uji izin, koreksi, kirim ulang dan rekonsiliasi tanpa duplikasi. |
| UJ-18 | Ketahanan dan beban | Jalankan data sintetis 5.000 barang dan beban mutasi sesuai target yang disepakati. Catat lingkungan, distribusi waktu dan kegagalan, serta bandingkan target yang ditetapkan sebelum tes. Simulasikan kegagalan jaringan dan respons hilang tanpa menggandakan efek. |
| UJ-19 | Keamanan dan rilis | Periksa sesi dan hak akses, input tidak sah, kebocoran data pada laporan dan log, status langganan sesuai kontrak, serta pemeriksaan cadangan dan pemulihan pada lingkungan sementara bila termasuk syarat rilis. |

## Rekonsiliasi dan ekspor

Paket beban menggunakan 5.000 barang dan 500 mutasi per tanggal selama tujuh tanggal sintetis, total 3.500 mutasi. Ukur endpoint daftar barang, saldo, stok per lokasi/gudang, pergerakan, pencarian dan kartu stok, sekurangnya lima permintaan per endpoint dengan data yang sama. Target baca di bawah 250 ms diterapkan pada tiap permintaan yang diukur di runner API/database. Catat maksimum, kondisi awal cache, versi dan sumber daya runner. Waktu browser serta jaringan deployment dicatat terpisah agar sumber keterlambatan dapat ditelusuri.

Sesudah setiap peristiwa utama, bandingkan hasil yang terlihat di UI dan API dengan buku harapan independen serta query baca database uji. Query database harus membaca mutasi dan saldo secara terpisah, mengelompokkan per barang, gudang, lokasi dan kondisi, lalu memeriksa keseimbangan dan referensi dokumen. Jangan memakai satu laporan aplikasi sebagai satu-satunya pembanding laporan lain.

Unduh XLSX di Playwright, parse isi lembar dan bandingkan semua baris serta jumlah dengan harapan untuk seluruh data dan setiap kombinasi filter yang diuji. Buat data cukup untuk melewati satu halaman dan periksa baris awal, tengah dan akhir termasuk total baris. Periksa tanggal, satuan, lokasi, kondisi dan nilai sel yang relevan. Uji ekspor sebagai masing-masing identitas terbatas dan orang luar. Bukti mencatat jumlah baris yang dibandingkan, filter dan hasil rekonsiliasi.

Untuk akhir rangkaian utama, laporan seluruh gudang harus menghasilkan A 27 PCS dan B 9 PCS, total 36 PCS. Filter karantina A menghasilkan 1 PCS. Jika laporan menyediakan status layak jual, totalnya 35 PCS. Rincian mutasi masuk eksternal adalah 20 saldo awal + 24 penerimaan + 2 retur pelanggan = 46 PCS. Mutasi keluar eksternal adalah 6 pengeluaran + 3 retur pemasok + 1 penyesuaian = 10 PCS. Selisihnya 36 PCS. Mutasi internal putaway, transfer dan penyelesaian transit direkonsiliasi terpisah sebagai pasangan perpindahan lokasi.

### Paket integrasi bila dipilih dalam versi final

Jalankan fixture integrasi pada tenant tersendiri dan simpan perhitungan nilainya sebelum aplikasi dijalankan.

| Paket | Masukan sintetis | Hasil pembanding |
| --- | --- | --- |
| Accounting rata-rata | Saldo awal 10 PCS bernilai Rp1.000.000, terima 10 PCS bernilai Rp1.200.000, kemudian keluarkan 5 PCS untuk penjualan | Modal rata-rata Rp110.000/PCS, HPP Rp550.000, sisa 15 PCS bernilai Rp1.650.000. Jurnal seimbang dan saldo akun persediaan cocok dengan valuasi pada tanggal yang sama |
| Koreksi dan periode Accounting | Koreksi transaksi dengan dokumen balik, kirim ulang pesan, tahan kiriman pada periode terkunci, lalu buka periode dan proses ulang sesuai kontrak | Satu dampak per peristiwa sumber, referensi koreksi lengkap dan jejak status ditahan/terkirim. Transfer internal mempertahankan total kuantitas dan nilai perusahaan |
| Project | Permintaan 8 PCS, kirim dan terima 5 PCS, pakai 3 PCS, kembalikan sisa 2 PCS | Permintaan, pengiriman, penerimaan, pemakaian dan pengembalian masing-masing terlacak ke sumber. Stok material tersisa pada lokasi proyek 0 PCS, kuantitas kembali ke asal 2 PCS dan sisa permintaan 3 PCS tetap tercatat sesuai kontrak. Bila kontrak mengakui biaya saat pemakaian dengan modal Rp110.000/PCS, biaya proyek Rp330.000 |
| Kasir | Kirim 4 PCS dari gudang ke outlet, konfirmasi penerimaan, lalu ulangi pesan yang sama | Gudang berkurang 4 PCS dan outlet bertambah 4 PCS setelah penerimaan yang sah. Pengulangan menghasilkan satu dampak sumber yang sama |

Kontrak integrasi menetapkan titik pengakuan mutasi dan biaya, akun serta pemetaan barang sebelum angka pembanding dikunci. Pisahkan hasil setiap produk, lalu rekonsiliasi dampak konsolidasi untuk mencegah kuantitas atau biaya terhitung ganda. Skenario integrasi yang termasuk cakupan versi wajib selesai diimplementasikan sebelum diberi hasil penerimaan.

## Eksekusi CI pada Fase 6

Sebelum kampanye, siapkan perluasan fixture identitas, putaran browser PostgreSQL, pembaca XLSX dan pengumpulan bukti yang dijelaskan di atas. Langkah aplikasi memakai UI normal. API langsung dipakai untuk percobaan akses tanpa izin, kasus bersamaan dan pemeriksaan hasil. Data awal fixture dipakai untuk mengisolasi kasus gagal dari rangkaian utama.

1. Induk mencatat manifest versi dan cakupan, kemudian memicu workflow penerimaan melalui PR atau pemicu yang tersedia pada repositori. Pasangkan backend dan frontend melalui SHA penuh yang dicatat dalam konfigurasi CI.
2. Runner memasang dependensi, menjalankan lint/build dan suite backend, lalu Playwright serta paket PostgreSQL pada versi yang sama. Tambahkan paket integrasi yang termasuk cakupan.
3. Pekerja memeriksa hasil sesuai paketnya. Saat gagal, catat langkah dan bukti, perbaiki penyebab, kemudian ulangi tes terdampak. Run lama tetap terikat pada SHA lama.
4. Setelah perbaikan terakhir, jalankan regresi seluruh cakupan versi pada pasangan SHA final. Induk menyatukan hasil menjadi laporan penerimaan dan daftar pekerjaan tersisa.

Perintah pemantauan berikut tersedia melalui `gh`. Jalankan pada Fase 6 dengan branch dan ID run kampanye yang sebenarnya.

```powershell
gh run list -R abuashifan/finlite-gudang -b <branch-kampanye> -L 3 --json databaseId,headSha,status,conclusion
gh run watch <run-id-aplikasi> -R abuashifan/finlite-gudang --exit-status
gh run view <run-id-aplikasi> -R abuashifan/finlite-gudang --log-failed
gh run list -R abuashifan/laravel_backend -b <branch-kampanye> -L 3 --json databaseId,headSha,status,conclusion
gh run watch <run-id-backend> -R abuashifan/laravel_backend --exit-status
```

Pada runner aplikasi, gunakan skrip repositori `npm run lint`, `npm run build` dan `npm run e2e`. Suite backend menggunakan workflow `Tests` beserta job PostgreSQL. Nama workflow dan pemicu penerimaan final diperiksa ketika perluasannya diimplementasikan. Catat hasil job pada SHA final dan pastikan seluruh run selesai sebelum menetapkan kelulusan.

## Bukti, temuan dan keputusan

Simpan laporan CI dan Playwright, SHA penuh semua repositori, tautan run, konfigurasi dan versi, hasil pemeriksaan PostgreSQL, buku harapan, hasil rekonsiliasi, serta daftar skenario dan statusnya. Sertakan screenshot keadaan penting, trace kegagalan dan bukti jaringan yang relevan. Redaksi token, cookie, kata sandi dan informasi sensitif sebelum menyimpan atau membagikan artefak. Gunakan data sintetis saja dan batasi akses serta masa simpan artefak sesuai kebijakan proyek.

Catat setiap temuan dengan tanggal, SHA, skenario, langkah reproduksi, harapan dan hasil, tingkat dampak, tautan bukti, pemilik dan status. Temuan kehilangan atau salah stok, pelanggaran izin, duplikasi atau salah jurnal diperlakukan sebagai tingkat tinggi. Setelah perbaikan, jalankan ulang skenario terkait dan regresi yang terdampak pada pasangan SHA baru.

Penerimaan simulasi Fase 6 lulus bila seluruh fitur wajib dalam cakupan telah siap dan seluruh skenario wajib lulus pada pasangan SHA yang tercatat, rekonsiliasi dan ekspor cocok dengan buku harapan, tes PostgreSQL dan keamanan lulus, serta tidak ada temuan tinggi terbuka. Integrasi yang dipilih wajib lulus rekonsiliasi masing-masing. Catat fitur di luar cakupan dan keterbatasan simulasi secara eksplisit. Pilot fisik dijadwalkan setelah gudang tersedia. Penerimaan program mengikuti kriteria simulasi di atas.

