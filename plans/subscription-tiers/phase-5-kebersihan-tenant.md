# Fase 5 — Menutup Kebocoran Berkas Tenant

**Status: ✅ SELESAI 2026-08-12.** Ringkasan eksekusi ada di **§ Hasil
eksekusi** di akhir dokumen ini. Sisa dokumen ini adalah temuan dan rancangan
ASLI (pra-eksekusi), dipertahankan sebagai riwayat.

Ini bukan fitur langganan. Ia masuk rencana ini karena ditemukan saat menyusun
[kuota penyimpanan](phase-4-kuota-penyimpanan.md), dan karena ia membuat setiap
pengukuran penyimpanan tidak berarti sampai ditutup.

## Yang terukur 2026-08-11

```
database/tenants/
  total berkas : 33.790
  total ukuran : 53 GB
  berkas 0 byte:    555
  rentang waktu: 2026-06-09  →  2026-08-11 14:55
  dibuat hari itu juga: 4.471
```

Dua bulan, 53 GB. Laju kira-kira **26 GB per bulan** di mesin dev.

Angka 4.471 pada hari pengukuran menegaskan bahwa **kebocorannya masih
berjalan** — bukan sisa dari masa lalu. Berkas terbaru dibuat saat test suite
lengkap dijalankan sore itu.

## Sebabnya

Setiap test yang menyediakan tenant menjalankan 87 migrasi ke berkas SQLite baru
di `database/tenants/`, lalu tidak menghapusnya. Berkas berisi skema penuh
berukuran **1,7 MB**, dan satu kali `php artisan test` menghasilkan ribuan.

Sebagian sudah dibereskan: `TenantProvisioningService` kini mengambil lintasan
dari `config('tenant.database_path')` sehingga test **bisa** diarahkan ke
direktori sementara, dan `UserQuotaTest` membersihkan berkasnya di `tearDown()`.
Tapi jelas masih ada jalur lain yang menulis ke direktori nyata tanpa
membersihkan.

## Pekerjaan

### 5a. Temukan jalur yang masih bocor

Bandingkan pola nama berkas yang tertinggal (`test_access_1_*`, dan lainnya)
dengan test yang membuatnya. Nama berkasnya sudah menunjuk asalnya — itu jalur
tercepat menemukan siapa yang tidak membersihkan.

### 5b. Arahkan seluruh test ke direktori sementara

Cara paling tahan lama bukan menambal `tearDown()` satu per satu, melainkan
**menyetel `tenant.database_path` ke direktori sementara di environment
testing**, satu kali di `TestCase`. Dengan begitu, test yang lupa membersihkan
pun tidak mengotori direktori nyata.

Direktori itu dihapus di akhir suite.

### 5c. Bersihkan yang menumpuk

53 GB berkas `test_*.sqlite` yang sudah ada. **Jangan hapus `company_*.sqlite`** —
itu tenant dev yang nyata (`company_000001` 1,7 MB, `company_000002` 1,9 MB).

Perintahnya harus menyaring dengan pola nama secara eksplisit, bukan menghapus
seluruh isi direktori.

### 5d. Jaga supaya tidak terulang

Test yang gagal kalau `database/tenants/` memuat berkas berpola `test_*` setelah
suite selesai. Murah, dan ia menangkap jalur baru yang lupa dibersihkan.

## Kenapa ini penting di luar soal ruang disk

1. **Mengotori pengukuran penyimpanan.** Kuota penyimpanan tidak bisa ditegakkan
   kalau direktorinya berisi 53 GB sampah.
2. **Memperlambat test.** Menulis 1,7 MB × ribuan berkas per suite adalah I/O
   yang tidak menghasilkan apa-apa.
3. **Menutupi masalah nyata.** Dengan 33.790 berkas di satu direktori, tenant
   yang benar-benar bermasalah tidak akan terlihat.

## Risiko

- **Salah pola hapus akan menghapus tenant nyata.** Perintah pembersih wajib
  diuji dengan `--dry-run` yang mencetak daftar berkas lebih dulu, dan wajib
  menyaring `test_*` secara eksplisit — bukan mengecualikan `company_*`.

---

## Hasil eksekusi 2026-08-12

### 5a. Sumber kebocoran — ditemukan, bukan ditambal per file

Awalnya diduga puluhan file independen. Ternyata **~110 dari ~117 pemanggil
`setUpTenant()`-semacamnya** menjangkau lewat hanya **lima base class**:
`JournalTestCase` (66 penerus langsung — termasuk `TenantTestCase`),
`SalesTestCase` (16), `PurchaseTestCase` (15), `MasterDataTestCase` (12),
`BudgetTestCase` (1). Memperbaiki kelima titik itu menutup sebagian besar
volume kebocoran sekaligus. Sisa ~15 berkas mandiri (masing-masing
mengonstruksi path tenant sendiri) diperbaiki satu per satu setelahnya.

### 5b. Deviasi dari rancangan: perbaikan sumber, bukan redirect ke direktori sementara

Rancangan menyarankan "arahkan `tenant.database_path` ke direktori sementara
di environment testing, satu kali di TestCase". **Tidak dikerjakan seperti
itu** — diperiksa lebih dulu dan ternyata TIDAK ADA test yang membaca
`config('tenant.database_path')` untuk menentukan path tenantnya; semuanya
memanggil `database_path('tenants/...')` langsung (helper Laravel, bukan
config). Membuat redirect config itu benar-benar berlaku berarti menulis
ulang path construction di puluhan berkas — pekerjaan yang **sama besarnya**
dengan alternatif yang dipilih.

Alternatif yang dibangun: `Tests\TestCase::registerTenantFile(string $path)`
— metode `protected` yang mendaftarkan path ke array yang sudah dibersihkan
`tearDown()` (mekanisme ini sudah ada sejak Fase 2, dibangun untuk
`companyOwnedBy()`). Kelima base class dan ~15 berkas mandiri dipanggil
sekali menambahkan satu baris `$this->registerTenantFile($tenantPath);`
setelah tiap `File::put(...)` yang menciptakan tenant. Efeknya sama
(kebersihan terjamin lewat mekanisme bersama), risikonya lebih kecil (tidak
menyentuh cara test menemukan direktori tenant-nya, hanya menambah satu
baris pendaftaran).

**Ranjau yang ditemukan saat eksekusi:** `CompanyQuotaTest.php` sudah punya
method `private function trackTenantFile(int $companyId)` sendiri dengan
signature berbeda total (menerima ID, bukan path). Nama metode baru di-
`TestCase` sempat bentrok dan menyebabkan fatal error visibilitas. Diberi
nama `registerTenantFile()` (bukan `trackTenantFile()`) untuk menghindarinya.

### 5c. Pembersihan yang sudah menumpuk

**14 GB, 8.168 berkas** (bertambah dari 53 GB/33.790 di pengukuran awal
2026-08-11 — turun karena ada pembersihan manual di sesi sebelumnya, lalu
naik lagi karena kebocoran masih berjalan sepanjang sesi ini sampai
diperbaiki). Dihapus dengan pola eksplisit `test_*` (bukan mengecualikan
`company_*`, sesuai peringatan risiko di atas). Diverifikasi SEBELUM
menghapus: hanya `.gitkeep`, `company_000001.sqlite`, `company_000002.sqlite`
yang tidak berpola `test_*` — ketiganya selamat. Direktori akhir: **5,7 MB**.

### 5d. Guard — dibangun sebagai PHPUnit extension, bukan test biasa

Rancangan menyebut "test yang gagal kalau ada berkas `test_*` tersisa
setelah suite selesai". **Bentuknya diputuskan saat eksekusi**: PHPUnit
tidak menjamin urutan eksekusi antar test class secara default, jadi test
class biasa yang dimaksudkan "berjalan terakhir" bisa saja tidak benar-benar
terakhir. Dibangun sebagai extension (`tests/Support/TenantFileLeakGuardExtension.php`,
didaftarkan di `phpunit.xml`) yang berlangganan event `TestRunner\Finished`
— dijamin menyala setelah SEMUA test selesai apa pun urutannya. Kalau ada
berkas `test_*` tersisa, dicetak ke STDERR lalu `exit(1)` — cara resmi yang
didukung PHPUnit untuk membuat pemeriksaan tambahan ikut menggagalkan build.

Diuji dengan menaruh berkas `test_*` palsu secara manual dan mengonfirmasi
`php artisan test`/`vendor/bin/phpunit` keduanya keluar dengan kode 1 dan
pesan yang jelas; lalu dikonfirmasi kembali ke kode 0 setelah berkasnya
dibuang.

### Hasil terukur

```
Sebelum  : ribuan berkas baru per `php artisan test` (tanpa batas, terus menumpuk)
Sesudah  : 0 berkas net setelah suite penuh (1271 test) — diverifikasi dua kali berturut-turut
Direktori: 14 GB → 5,7 MB
```

### Yang belum dikerjakan

- **Redirect ke direktori sementara** (mekanisme asli §5b) — sengaja tidak
  dikerjakan, lihat deviasi di atas. Kalau nanti ada test baru yang lupa
  memanggil `registerTenantFile()`, guard 5d akan menangkapnya di CI/lokal
  sebelum sempat menumpuk lagi.
