# Tutorial Hapus & Pulihkan Perusahaan (Database Tenant)

> Panduan lengkap menghapus perusahaan dari sisi client dan memulihkannya dari area super admin di Finlite ERP.
>
> Berlaku sejak 2026-08-20. Setiap perusahaan punya **satu database tenant sendiri** (SQLite), jadi "menghapus perusahaan" sama artinya dengan menyingkirkan seluruh database pembukuannya.

---

## Daftar Isi

1. [Konsep Dasar](#1-konsep-dasar)
2. [Apa yang Sebenarnya Terjadi Saat Menghapus](#2-apa-yang-sebenarnya-terjadi-saat-menghapus)
3. [Tutorial: Menghapus Perusahaan (Client)](#3-tutorial-menghapus-perusahaan-client)
4. [Tutorial: Memulihkan Perusahaan (Super Admin)](#4-tutorial-memulihkan-perusahaan-super-admin)
5. [Tutorial: Menghapus Permanen](#5-tutorial-menghapus-permanen)
6. [Masa Pemulihan 30 Hari & Sweep Harian](#6-masa-pemulihan-30-hari--sweep-harian)
7. [Aturan Kuota Saat Pemulihan](#7-aturan-kuota-saat-pemulihan)
8. [Jaminan "Kembali Persis Seperti Semula"](#8-jaminan-kembali-persis-seperti-semula)
9. [Pemecahan Masalah](#9-pemecahan-masalah)
10. [Referensi Teknis](#10-referensi-teknis)

---

## 1. Konsep Dasar

### Dua tahap penghapusan

Penghapusan di Finlite **tidak langsung permanen**. Ada dua tahap yang sengaja dipisah:

| Tahap | Istilah | Siapa yang melakukan | Bisa dibatalkan? |
|---|---|---|---|
| **1. Hapus** | *soft delete* | Owner perusahaan (client) | ✅ Ya, selama 30 hari |
| **2. Hapus permanen** | *purge* | Otomatis (sweep harian) atau super admin | ❌ Tidak, selamanya |

> 💡 **Intinya:** klik "Hapus" di aplikasi **tidak** menghancurkan data. Perusahaan hanya disembunyikan dan slot kuotanya dibebaskan. Data baru benar-benar hilang setelah 30 hari.

### Siapa boleh apa

| Peran | Hapus | Lihat daftar terhapus | Pulihkan | Hapus permanen |
|---|---|---|---|---|
| **Owner perusahaan** (client) | ✅ | — | ❌ | ❌ |
| Staf / admin perusahaan | ❌ | — | ❌ | ❌ |
| **Super admin aplikasi** | — | ✅ | ✅ | ✅ |

> ⚠️ **Client tidak punya tombol pulihkan sama sekali.** Ini disengaja. Pemulihan menyangkut kuota dan alasan penghapusan, jadi harus lewat orang yang bisa menilai keduanya. Client yang ingin datanya kembali **harus menghubungi admin aplikasi**.

---

## 2. Apa yang Sebenarnya Terjadi Saat Menghapus

Saat owner menghapus perusahaan, **hanya satu kolom yang berubah**: `companies.deleted_at` diisi waktu penghapusan.

Tidak ada yang lain disentuh:

| Hal | Status setelah dihapus |
|---|---|
| Baris `companies` | Masih ada, hanya ditandai `deleted_at` |
| Status staf (`company_users`) | **Tidak berubah** |
| Status tenant (`tenant_databases`) | **Tidak berubah** |
| File database SQLite tenant | **Masih utuh di disk** |
| Isi pembukuan (produk, jurnal, transaksi) | **Tidak pernah dibuka, apalagi diubah** |

### Kenapa satu kolom itu sudah cukup

Setiap pintu masuk ke data perusahaan melewati query yang otomatis mengenal soft delete:

- **Akses API** — `EnsureCompanyAccess` memanggil `Company::find()`; perusahaan terhapus tidak ditemukan → `404 COMPANY_NOT_FOUND`
- **Halaman Pilih Perusahaan** — daftar perusahaan tidak lagi memuatnya
- **Kuota** — `CompanyQuotaService::usedCount()` tidak menghitungnya, jadi **slot langsung bebas** untuk membuat perusahaan baru
- **Buka perusahaan** — `POST /companies/select` menolak dengan galat validasi

> 💡 **Kenapa ini penting untuk pemulihan:** karena penghapusan tidak menimpa apa pun, pemulihan cukup mengosongkan `deleted_at` — dan otomatis semuanya kembali persis seperti semula. Lihat [bagian 8](#8-jaminan-kembali-persis-seperti-semula).

---

## 3. Tutorial: Menghapus Perusahaan (Client)

**Prasyarat:** Anda harus **owner** perusahaan tersebut. Staf dan admin perusahaan tidak melihat menu ini.

### Langkah-langkah

1. **Login** sebagai client.
2. Masuk ke halaman **Pilih Perusahaan**.
   - Kalau Anda sedang berada di dalam aplikasi, buka menu profil di kanan atas → **Tutup Database**.
3. Arahkan kursor ke kartu perusahaan yang ingin dihapus.
4. Klik ikon **⋮** (tiga titik) di **pojok kanan atas kartu**.

   > Ikon ini **hanya muncul pada perusahaan yang Anda miliki (owner)**. Kalau tidak terlihat, berarti Anda bukan ownernya.

5. Pilih **Hapus Perusahaan**.
6. Dialog konfirmasi terbuka. **Ketik ulang nama perusahaan persis sama** pada kolom yang disediakan.

   - Contoh: kalau nama perusahaannya `PT Maju Jaya`, ketik `PT Maju Jaya` — bukan `pt maju jaya`, bukan `PT Maju Jaya ` (ada spasi).
   - Tombol **Hapus Perusahaan** tetap mati sampai ketikan cocok persis.

7. Klik **Hapus Perusahaan**.

### Hasil yang diharapkan

- ✅ Notifikasi "Perusahaan berhasil dihapus."
- ✅ Kartu perusahaan hilang dari daftar
- ✅ Slot kuota Anda bertambah satu (bisa langsung membuat perusahaan baru)
- ✅ Kalau perusahaan itu sedang terbuka, sesinya ditutup otomatis

> ⚠️ **Semua staf yang diundang langsung kehilangan akses.** Mereka tidak diberi notifikasi apa pun oleh sistem.

### Keluar dari wizard setup tanpa menghapus

Perusahaan yang baru dibuat langsung membawa Anda ke **wizard Setup Perusahaan Baru**. Kalau ternyata Anda salah masuk atau ingin mengurus perusahaan lain dulu, **tidak perlu menghapus perusahaannya**:

1. Klik **Batalkan** di pojok kanan atas header wizard.
2. Konfirmasi dengan **Ya, Pilih Perusahaan**.

Anda kembali ke halaman Pilih Perusahaan, dan perusahaan tadi **tetap ada**. Langkah yang sudah tersimpan tetap tersimpan — buka lagi perusahaan itu kapan saja untuk melanjutkan setup dari langkah terakhir.

> 💡 Yang hilang hanya isian pada langkah yang sedang terbuka dan belum disimpan. Menghapus perusahaan (bagian di atas) adalah tindakan yang sama sekali berbeda — pakai itu hanya kalau perusahaannya memang tidak diinginkan.

---

## 4. Tutorial: Memulihkan Perusahaan (Super Admin)

**Prasyarat:** akun **super admin aplikasi** (`is_platform_admin`), bukan akun client.

### Langkah-langkah

1. **Login** ke area admin: `/admin/login`.
2. Dari halaman **Client**, klik tombol **Perusahaan Terhapus** di kanan atas header.
   - Alamat langsung: `/admin/companies/deleted`
3. Anda melihat tabel berisi seluruh perusahaan terhapus:

   | Kolom | Isi |
   |---|---|
   | **Perusahaan** | Nama + kode perusahaan (mis. `CMP-000005`) |
   | **Owner** | Email owner + pemakaian kuotanya (mis. `Kuota 2/5`) |
   | **Dihapus** | Tanggal penghapusan |
   | **Sisa Waktu** | Hitung mundur sebelum dihapus permanen |
   | **Aksi** | Tombol **Pulihkan** dan **Hapus Permanen** |

4. Cari baris perusahaan yang diminta client.
5. Klik **Pulihkan**.

### Hasil yang diharapkan

- ✅ Notifikasi "*(nama perusahaan)* berhasil dipulihkan."
- ✅ Baris hilang dari daftar perusahaan terhapus
- ✅ Client langsung melihat perusahaannya kembali di halaman Pilih Perusahaan
- ✅ Client bisa membukanya dan seluruh pembukuannya utuh

### Kalau tombol Pulihkan mati (disabled)

Arahkan kursor ke tombolnya — akan muncul keterangan alasannya. Ada dua kemungkinan:

| Penyebab | Arti | Solusi |
|---|---|---|
| **Kuota owner penuh** | Client sudah memakai seluruh jatah perusahaannya | Lihat [bagian 7](#7-aturan-kuota-saat-pemulihan) |
| **Kedaluwarsa** | Sudah lewat 30 hari | Tidak bisa dipulihkan lagi — lihat [bagian 6](#6-masa-pemulihan-30-hari--sweep-harian) |

Spanduk kuning di atas tabel juga merangkum berapa perusahaan yang sedang terhalang.

---

## 5. Tutorial: Menghapus Permanen

> ⚠️ **Tindakan ini tidak bisa dibatalkan dengan cara apa pun.** File database tenant dihapus dari disk. Tidak ada undo, tidak ada tong sampah kedua.

Gunakan hanya bila:
- Client meminta datanya benar-benar dimusnahkan, **atau**
- Slot kuota client perlu dibebaskan agar perusahaan lain bisa dipulihkan (lihat [bagian 7](#7-aturan-kuota-saat-pemulihan))

### Langkah-langkah

1. Buka `/admin/companies/deleted`.
2. Pada baris yang dituju, klik **Hapus Permanen**.
3. Dialog peringatan terbuka. **Ketik ulang nama perusahaan persis sama.**
4. Klik **Hapus Permanen**.

### Hasil yang diharapkan

- ✅ Notifikasi "*(nama perusahaan)* dihapus permanen."
- ✅ Baris hilang dari daftar
- ✅ Baris `companies`, `company_users`, `tenant_databases`, tahun fiskal, periode akuntansi, dan seluruh tabel pusat terkait ikut terhapus (lewat cascade)
- ✅ File SQLite tenant dihapus dari disk
- ✅ Nama dan `slug`-nya bebas dipakai lagi oleh perusahaan baru

> 💡 **Jejak audit tetap tinggal.** Tabel `activity_logs` sengaja memakai `nullOnDelete`, jadi catatan siapa menghapus apa dan kapan tidak ikut hilang.

---

## 6. Masa Pemulihan 30 Hari & Sweep Harian

### Aturannya

Perusahaan terhapus bisa dipulihkan **selama 30 hari** sejak dihapus. Lewat dari itu, perusahaan dihapus permanen secara otomatis.

### Mengubah lama masa pemulihan

Diatur di `config/companies.php`, bisa ditimpa lewat environment:

```env
COMPANY_DELETION_RETENTION_DAYS=30
```

### Menjalankan sweep

Penghapusan permanen otomatis dikerjakan oleh command berikut — **jadwalkan harian lewat cron**:

```bash
php artisan companies:sweep-deleted
```

Contoh entri cron (setiap hari pukul 02:00):

```cron
0 2 * * * cd /path/ke/laravel_backend && php artisan companies:sweep-deleted >> storage/logs/sweep.log 2>&1
```

### Memeriksa dulu sebelum menghapus

**Selalu jalankan `--dry-run` lebih dulu** kalau ragu. Mode ini mencetak daftar yang akan terhapus **tanpa mengubah apa pun**:

```bash
php artisan companies:sweep-deleted --dry-run
```

Contoh keluaran:

```
+------------+----------------------+---------------------+--------------+
| Company ID | Perusahaan           | Dihapus pada        | Umur         |
+------------+----------------------+---------------------+--------------+
| 12         | PT Contoh Lama       | 2026-07-15 09:12:44 | 36 hari lalu |
+------------+----------------------+---------------------+--------------+
--dry-run: 1 perusahaan DI ATAS akan dihapus permanen. Tidak ada yang diubah.
```

### Menguji dengan ambang berbeda

Opsi `--days` menimpa ambang dari config — berguna untuk melihat apa saja yang akan kena bila masa pemulihan diperpendek:

```bash
# Lihat apa yang akan kena kalau masa pemulihan cuma 7 hari
php artisan companies:sweep-deleted --dry-run --days=7
```

> ⚠️ **Gabungkan `--days` dengan `--dry-run` saat bereksperimen.** `--days=0` tanpa `--dry-run` akan menghapus permanen **seluruh** perusahaan terhapus seketika.

---

## 7. Aturan Kuota Saat Pemulihan

### Aturannya

**Pemulihan tidak boleh membuat kuota client terlampaui.** Kalau client berpaket 3 perusahaan dan sudah memakai 3, perusahaan keempat tidak bisa dipulihkan — meski masih dalam masa 30 hari.

### Kenapa ini bisa terjadi

Menghapus perusahaan **langsung membebaskan slot**. Jadi urutan ini lazim terjadi:

1. Client punya kuota 3, terpakai 3 → penuh
2. Client menghapus `PT Lama` → terpakai 2, ada slot kosong
3. Client membuat `PT Baru` → terpakai 3 lagi, penuh
4. Client berubah pikiran, minta `PT Lama` dipulihkan → **terhalang**, karena memulihkannya berarti 4 perusahaan

### Tiga jalan keluarnya

| Solusi | Cara | Cocok bila |
|---|---|---|
| **Client menghapus perusahaan aktif** | Minta client menghapus salah satu perusahaan aktifnya sendiri | Client memang ingin menukar |
| **Hapus permanen yang lain** | Super admin purge perusahaan terhapus lain milik client itu | Ada perusahaan terhapus yang memang tidak diinginkan lagi |
| **Naikkan kuota** | Admin → Client → ubah paket atau kuota khusus (`company_quota`) | Client bersedia naik paket |

Setelah slot tersedia, ulangi langkah pemulihan — tombol **Pulihkan** akan aktif kembali.

> 💡 **Kuota dihitung per client (owner), bukan per perusahaan.** Kalau sebuah perusahaan punya lebih dari satu owner, slotnya terpakai di jatah semua owner tersebut, dan pemulihan menuntut semuanya punya sisa slot.

---

## 8. Jaminan "Kembali Persis Seperti Semula"

Pemulihan **tidak boleh mengubah apa pun** dibanding keadaan sebelum penghapusan. Yang dijamin:

| Hal | Jaminan |
|---|---|
| Staf yang **dinonaktifkan** sebelum dihapus | Tetap nonaktif setelah dipulihkan — **tidak** berubah jadi aktif |
| Staf yang **dikeluarkan** sebelum dihapus | Tetap dikeluarkan |
| Produk **nonaktif** | Tetap nonaktif |
| Transaksi **void** | Tetap void — **tidak** berubah jadi posted |
| Periode / tahun fiskal tertutup | Tetap tertutup |
| Nomor dokumen & urutannya | Tidak bergeser |

### Kenapa bisa dijamin

Karena penghapusan **hanya mengisi `companies.deleted_at`** dan tidak pernah membuka file tenant, tidak ada satu pun status di dalam pembukuan yang tersentuh. Pemulihan mengosongkan kolom yang sama. Tidak ada langkah "menyalakan ulang" yang bisa salah menebak keadaan semula.

> 📌 **Catatan sejarah.** Versi pertama fitur ini (sebelum 2026-08-20) ikut menimpa `company_users.status` menjadi `removed` dan `tenant_databases.status` menjadi `deleted`. Itu **merusak jaminan di atas**: status asli tiap staf tertimpa dan mustahil dikembalikan. Perilaku itu dibuang, dan migrasi `repair_legacy_company_deletion_state` memperbaiki baris yang terlanjur tertimpa. Kalau Anda menemukan perusahaan terhapus lama yang gagal dibuka setelah dipulihkan, periksa apakah migrasi ini sudah jalan.

---

## 9. Pemecahan Masalah

### Client: "Menu ⋮ tidak muncul di kartu perusahaan"

Anda bukan **owner** perusahaan itu. Hanya owner yang bisa menghapus. Periksa peran Anda di perusahaan tersebut.

### Client: "Tombol Hapus tetap mati padahal sudah mengetik nama"

Ketikan harus **persis sama**, termasuk huruf besar-kecil dan spasi. Salin-tempel nama dari kartu perusahaan untuk memastikan.

### Client: "Saya ingin perusahaan saya kembali"

Hubungi **admin aplikasi**. Client tidak punya jalur pemulihan sendiri. Sebutkan **nama perusahaan** dan **kapan kira-kira dihapus** — admin butuh keduanya untuk menemukan barisnya.

### Admin: "Tombol Pulihkan mati"

Arahkan kursor ke tombol untuk melihat alasannya. Dua kemungkinan: kuota owner penuh ([bagian 7](#7-aturan-kuota-saat-pemulihan)) atau sudah lewat 30 hari ([bagian 6](#6-masa-pemulihan-30-hari--sweep-harian)).

### Admin: "Perusahaan yang diminta client tidak ada di daftar"

Kemungkinannya:
1. **Sudah lewat 30 hari** dan sweep harian sudah menghapusnya permanen → data tidak bisa dikembalikan
2. Perusahaan itu **tidak pernah dihapus** — mungkin client hanya tidak menemukannya (minta client memeriksa kembali halaman Pilih Perusahaan)

Cek jejaknya di `activity_logs` dengan event `companies.delete` dan `companies.purge`.

### Admin: "Client sudah dipulihkan tapi tidak bisa membuka perusahaannya"

Periksa status tenant database-nya:

```bash
php artisan tinker --execute="
\$td = App\Shared\Models\TenantDatabase::where('company_id', <ID>)->first();
echo \$td->status.' | '.\$td->database_path.' | file='.(file_exists(\$td->database_path) ? 'ada' : 'HILANG');
"
```

- Status harus `active`. Kalau `deleted`, jalankan migrasi perbaikan (lihat catatan sejarah di [bagian 8](#8-jaminan-kembali-persis-seperti-semula)).
- Kalau file-nya `HILANG`, database sudah terhapus permanen dan tidak bisa dipulihkan.

### "Berapa perusahaan terhapus yang ada sekarang?"

```bash
php artisan tinker --execute="
foreach (App\Shared\Models\Company::onlyTrashed()->orderBy('deleted_at')->get() as \$c) {
    echo \$c->id.' | '.\$c->name.' | dihapus '.\$c->deleted_at.PHP_EOL;
}"
```

---

## 10. Referensi Teknis

### Endpoint

| Method | Path | Akses | Fungsi |
|---|---|---|---|
| `DELETE` | `/api/companies/{id}` | Client (owner) | Hapus perusahaan (soft delete). Body: `confirm_name` |
| `GET` | `/api/admin/companies/deleted` | Super admin | Daftar perusahaan terhapus + sisa waktu + status kuota |
| `POST` | `/api/admin/companies/{id}/restore` | Super admin | Pulihkan |
| `DELETE` | `/api/admin/companies/{id}/purge` | Super admin | Hapus permanen. Body: `confirm_name` |

### Kode galat

| Kode | Status | Arti |
|---|---|---|
| `COMPANY_DELETE_NOT_OWNER` | 403 | Yang menghapus bukan owner perusahaan |
| `COMPANY_RESTORE_QUOTA_EXCEEDED` | 422 | Kuota owner penuh — bebaskan slot dulu |
| `COMPANY_RESTORE_WINDOW_EXPIRED` | 422 | Sudah lewat masa pemulihan |
| — | 404 | Id tidak ditemukan **di antara perusahaan terhapus** (mis. sudah dipurge, atau perusahaannya masih aktif) |
| — | 422 | `confirm_name` kosong atau tidak cocok dengan nama perusahaan |

### Berkas backend

| Berkas | Peran |
|---|---|
| `app/Shared/Company/CompanyDeletionService.php` | Soft delete — hanya `deleted_at` + audit |
| `app/Shared/Company/CompanyRestoreService.php` | Pemulihan + penjaga kuota & masa pemulihan |
| `app/Shared/Company/CompanyPurgeService.php` | Hapus permanen + hapus file tenant |
| `app/Modules/Companies/Controllers/CompanyController.php` | `destroy()` untuk client |
| `app/Modules/Admin/Controllers/DeletedCompanyController.php` | Daftar / pulihkan / purge untuk admin |
| `app/Console/Commands/SweepDeletedCompaniesCommand.php` | Sweep harian 30 hari |
| `config/companies.php` | `deletion_retention_days` |

> 💡 **Kenapa ketiga service ada di `app/Shared/Company/`, bukan `app/Modules/Companies/`?** Karena dipakai dua modul sekaligus (Companies untuk hapus, Admin untuk pulihkan/purge) dan hanya menyentuh model `app/Shared/Models/`. Menaruhnya di dalam modul akan melanggar `ModuleBoundariesTest`. Presedennya sama dengan `app/Shared/Subscription/CompanyQuotaService.php`.

### Berkas frontend

| Berkas | Peran |
|---|---|
| `src/modules/auth/pages/CompanyPickerPage.tsx` | Menu ⋮ per kartu (owner saja) |
| `src/modules/auth/components/DeleteCompanyDialog.tsx` | Dialog konfirmasi ketik-nama |
| `src/modules/onboarding/pages/OnboardingPage.tsx` | Tombol **Batalkan** untuk keluar dari wizard tanpa menghapus |
| `src/modules/admin/pages/AdminDeletedCompaniesPage.tsx` | Halaman admin perusahaan terhapus |
| `src/modules/admin/hooks/useDeletedCompanies.ts` | Query + mutasi restore/purge |

### Test

```bash
# Seluruh alur hapus, pulihkan, kuota, masa pemulihan, dan sweep
php artisan test --filter=Companies
```

| Test | Cakupan |
|---|---|
| `DeleteCompanyTest` | Owner-only, konfirmasi nama, kuota bebas, status staf tidak tertimpa |
| `RestoreCompanyTest` | Client tidak bisa akses, pemulihan utuh, blokir kuota, blokir 30 hari, sweep, purge |

---

## Ringkasan Satu Halaman

```
CLIENT (owner)                     SUPER ADMIN
─────────────                      ───────────
Pilih Perusahaan                   /admin/companies/deleted
  └ kartu → ⋮ → Hapus Perusahaan     ├ Pulihkan      (≤30 hari, kuota ada)
      └ ketik nama → konfirmasi      └ Hapus Permanen (ketik nama, TIDAK BISA DIBATALKAN)

         ↓ soft delete                         ↑ pulihkan
   companies.deleted_at diisi          companies.deleted_at dikosongkan
   (tidak ada yang lain berubah)       (tidak ada yang lain berubah)

                    ↓ lewat 30 hari
         php artisan companies:sweep-deleted
              → HAPUS PERMANEN + file tenant dihapus
```
