# Fase 8 — Saldo awal jadi impor jurnal umum

> Status: **SELESAI** — diimplementasikan 2026-09-06.
> Membalik keputusan 7C-1 dan 7D-1.
>
> Verifikasi: `php artisan test` 1502 test, 0 gagal · `vendor/bin/pint --test` bersih ·
> frontend `npm run build` + `npx eslint src/` bersih.
> Seluruh database tenant di-reset setelahnya atas permintaan pemilik produk.

## Keputusan pemilik produk

> *"Import saldo awal itu terpisah dengan aset tetap. Sebatas import jurnal saja,
> di mana lawannya kas → opening balance. Tidak wajib ada urutan — terserah user
> mau import aset tetap dulu atau saldo akun dulu. Jika ada beda nilai akun
> dengan aset yang terdaftar, tidak masalah, beritahu saja di dashboard."*

Tiga aturan, dan tidak ada aturan keempat:

1. **Impor saldo awal mengisi saldo akun.** Ia impor jurnal umum, lawannya
   otomatis akun perantara.
2. **Impor aset tetap mendaftar kartu aset.** Nol jurnal. Boleh sebagian, boleh
   berkali-kali.
3. **Keduanya tidak saling tahu.** Urutan bebas, tidak ada prasyarat, tidak ada
   akun yang ditolak.

Selisih antara saldo akun dan register **bukan galat** — tanah bisa ada di
beberapa lokasi sementara yang terdaftar baru satu. Dashboard memberitahu, user
yang memutuskan.

## Bentuknya

Akun baru di templat COA: **`3900 Saldo Awal (Perantara)`**, tipe `equity`,
mapping key `opening_balance.clearing`.

```
Impor saldo awal (berkas neraca saldo lama, apa adanya):
  Kas                   D  10.000.000
  Tanah                 D 100.000.000
  Kendaraan             D 200.000.000
  Akum. Peny. Kendaraan K  30.000.000
  Utang Usaha           K  40.000.000
  Perantara             K 240.000.000   ← satu baris lawan, dihitung sistem

Impor aset tetap (kapan saja — nol jurnal):
  kartu Tanah (lokasi A) 60jt · kartu Kendaraan 200jt, akum 30jt, umur 8th

Dashboard:
  "Akun Tanah 100jt, kartu aset terdaftar 60jt — selisih 40jt."

Penutupan (satu tombol, kapan user siap):
  Perantara D 240.000.000 → Modal Pemilik K 240.000.000
```

Modal pemilik / laba ditahan tidak ditebak user — ia hasil hitungan, aset
dikurangi liabilitas.

## Yang dihapus

Rencana ini mengurangi kode, bukan menambah.

| Dihapus | Lokasi |
|---|---|
| `fixedAssetSystemLines()`, `openingFixedAssetTotals()` | `OpeningBalanceBatchService.php:500,542` |
| Galat `FIXED_ASSET_CONTROL_DUPLICATE` | `OpeningBalanceBatchService.php:585` |
| `FIXED_ASSET_CONTROL_KEYS` + penolakan akun aset tetap per baris | `OpeningBalanceImportCommitter.php` |
| `openingFixedAssetsPrecondition()`, `confirmedNoOpeningFixedAssets()` | `OpeningBalanceImportCommitter.php` |
| `preconditionError()` "saldo awal sudah diposting" | `FixedAssetOpeningImportCommitter.php` |
| `activateOpeningAssets()` / `deactivateOpeningAssets()` sebagai efek posting | `FixedAssetService.php`, `OpeningBalanceBatchService::post()/reopen()` |
| Checkbox *"tidak punya aset tetap awal"* | wizard Step 5 |
| Batch saldo awal + 6 statusnya + Validasi/Posting/Lock/Reopen | modul OpeningBalance |
| Editor baris + selisih yang dihitung dari state lokal | `OpeningBalanceBatchPage.tsx:101-103` |
| Batch koreksi (Fase 7G) | menambah yang terlewat cukup impor lagi |

`OpeningBalanceImportCommitter` hari ini 418 baris. Setelah jadi impor jurnal
biasa — baris berkas → baris jurnal, satu baris lawan, posting — ia tinggal
sepersekian itu, dan memakai jalur posting yang sama dengan profil
`journal_entry` yang sudah ada.

## Yang dibangun

| # | Pekerjaan | Berat |
|---|---|---|
| 8A | Akun 3900 + mapping `opening_balance.clearing` (migration + templat COA) | Kecil |
| 8B | Tanggal saldo awal jadi setelan perusahaan, bukan atribut batch | Kecil–sedang |
| 8C | `OpeningBalanceImportCommitter` memposting jurnal + baris perantara | Sedang |
| 8D | Lepas seluruh precondition aset tetap; aset langsung aktif | Sedang |
| 8E | `POST /opening-balance/close-clearing` → jurnal Perantara → Modal | Kecil |
| 8F | `GET /imports` + `POST /imports/{uuid}/revert` (void jurnalnya / hapus kartu aset) | Sedang |
| 8G | Papan pemantau Saldo Awal + kartu selisih di dashboard | Sedang |
| — | Pembersihan kode yang gugur | Sedang |

**8B bukan detail administratif.** `FixedAssetService::fillAutoAccumulatedDepreciation()`
(`:312`) menghitung akumulasi penyusutan *per tanggal saldo awal*, dan hari ini
tanggal itu baru pasti saat batch diposting. Begitu batch bubar, tanggalnya harus
punya rumah yang pasti sejak awal — kalau tidak, aset yang diimpor duluan memakai
tebakan. Urutannya: tetapkan tanggal di wizard → impor apa saja, bebas.

**8F** dibutuhkan karena hari ini tidak ada rute `index` di
`app/Modules/Imports/Routes/api.php` — UUID batch cuma hidup di state React, jadi
batch lama tidak bisa dibuka lagi, apalagi dibatalkan. Dan `cancel()`
(`ImportBatchService.php:193`) menghapus jejak impor tanpa menghapus datanya;
ia dipersempit ke batch yang belum di-commit.

**Papan pemantau (8G)** menggantikan `OpeningBalanceBatchPage`: tanggal saldo
awal, **saldo perantara** sebagai angka terbesar, daftar jurnal pembuka dengan
tombol Batalkan per baris, kartu selisih akun-vs-register, tombol Tutup ke Modal.

## Data lama: tidak ada migrasi

Pemilik produk 2026-09-06: seluruh data tenant yang ada adalah data dummy dan
boleh dibuang.

Artinya **tidak ada jalur migrasi yang perlu ditulis**. Batch saldo awal lama,
aset ber-`source_type = 'opening_import'` yang sudah diaktifkan, dan jurnal
pembukanya tidak perlu dipetakan ke model baru — modul batch dibongkar bersih,
dan tenant di-reset saat implementasi.

Reset database tenant dikerjakan **saat implementasi, dengan konfirmasi
terpisah** — bukan sekarang, dan bukan sebagai efek samping pekerjaan lain.

## Verifikasi

**Backend** — `vendor/bin/pint --test` + tes tersempit:

- impor saldo awal → satu jurnal seimbang, baris perantara sebesar selisih
- dua berkas berurutan → dua jurnal, saldo perantara terakumulasi
- akun aset tetap di berkas saldo awal → **diterima** (regresi terbalik dari 7B)
- akun nominal → tetap ditolak
- impor aset tetap sebelum **dan** sesudah impor saldo awal → dua-duanya lolos,
  nol jurnal baru
- register 60jt vs akun 100jt → impor tetap sukses, selisih muncul di laporan
- `close-clearing` → perantara 0; dipanggil lagi → ditolak
- `revert` saldo awal → jurnal ter-void, perantara balik
- `revert` aset tetap → kartu terhapus; ditolak bila penyusutannya sudah terposting
- `GET /imports` tidak bocor antar-tenant

**Frontend** — `rtk tsc`, `rtk lint`, lalu **`npm run build` + `npx eslint src/`**
untuk konfirmasi (dua perintah rtk itu melaporkan kurang dari yang sebenarnya).

**End-to-end** (Playwright, perusahaan baru, data `AUDIT-`): jalankan alurnya dua
kali dengan urutan impor dibalik — hasilnya harus identik.

## Pertanyaan yang menunggu jawaban

| # | Pertanyaan | Rekomendasi |
|---|---|---|
| 8-2 | Penutupan ke satu akun (Modal Pemilik), atau boleh dipecah Modal / Laba Ditahan? | Default satu akun, pemecahan manual tersedia. |
| 8-3 | Perantara belum nol saat tutup buku periode — blokir atau peringatan? | **Belum dikerjakan.** Yang sudah ada: spanduk peringatan di dashboard (`OpeningBalanceAlert`) dan peringatan di validasi wizard. Penjagaan di tutup buku periode menunggu keputusanmu. |
