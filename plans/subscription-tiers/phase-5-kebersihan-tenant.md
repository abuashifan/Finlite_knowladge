# Fase 5 — Menutup Kebocoran Berkas Tenant

**Status: ⬜ Belum dikerjakan. ⚠️ Bug aktif, bukan perencanaan.**

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
