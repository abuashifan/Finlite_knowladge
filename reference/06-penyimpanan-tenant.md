# Penyimpanan Tenant — Kenapa Data Perusahaan Hilang Tiap Deploy, dan Bagaimana Diperbaiki

> **Tujuan file ini:** menjelaskan di mana data akuntansi tiap perusahaan sebenarnya
> disimpan, kenapa ia hilang setiap kali aplikasi di-deploy ke Render, dan bentuk
> penyimpanan yang menggantikannya.
>
> Ditulis 2026-09-21 setelah menelusuri masalah ini sampai akarnya di kode nyata.
> Perintah verifikasi di sini sudah dijalankan, bukan dikira-kira.
>
> **Status: selesai dan terverifikasi (2026-09-21).** Perusahaan dibuat dengan
> `driver=pgsql`, datanya bertahan melewati redeploy Render.

---

## 1. Ringkasan satu paragraf

Setiap perusahaan punya database sendiri. Awalnya itu berupa **satu berkas SQLite
per perusahaan** di `database/tenants/`. Folder itu bagian dari image Docker, dan
Render membangun ulang image dari repo setiap deploy — sementara berkas `.sqlite`
sendiri di-`.gitignore`. Akibatnya **seluruh data akuntansi hilang setiap kali kode
di-push**, dan juga setiap kali container restart setelah idle. Perbaikannya:
tenant dipindahkan menjadi **satu schema Postgres per perusahaan di dalam database
Neon yang sama dengan tabel central**.

---

## 2. Dua "database" yang namanya mirip tapi berbeda

Ini sumber kebingungan yang paling sering. Ada dua hal berbeda di sistem ini:

| | Isinya | Tinggal di mana (dulu) |
|---|---|---|
| **Central** | `users`, `companies`, `plans`, `subscriptions`, `company_users`, `tenant_databases` | Neon (server Postgres) |
| **Tenant** | `chart_of_accounts`, `journals`, `journal_lines`, master data, status setup wizard | berkas `.sqlite` di dalam container |

### `tenant_databases` BUKAN berisi database tenant

Tabel `tenant_databases` tinggal di central, dan isinya hanya **catatan alamat** —
bukan datanya. Satu barisnya kira-kira:

| company_id | database_name | database_path | driver | status |
|---|---|---|---|---|
| 5 | `company_000005.sqlite` | `/var/www/html/database/tenants/company_000005.sqlite` | `sqlite` | `active` |

Lima kolom teks. Tidak ada satu pun angka akuntansi di situ.

Analoginya kartu katalog perpustakaan: kartunya bertuliskan *"Buku X ada di rak 3"*.
Kartu itu aman di laci (Neon). Rak 3 sudah dibuang (container). Kartunya masih ada,
bukunya tidak.

Kolom `status = 'active'` juga **bukan hasil pengecekan** — nilai itu ditulis sekali
saat perusahaan dibuat dan tidak pernah diperbarui. Ia tetap berbunyi `active`
walaupun wadah datanya sudah lama lenyap.

### Akibatnya saat error

Pesan **"tenant database not available"** berarti backend **berhasil** membaca baris
di Neon, lalu mengikuti alamatnya, dan tidak menemukan apa pun di sana. Bukan gagal
membaca Neon — justru berhasil, dan Neon menunjuk ke tempat yang sudah kosong.

---

## 3. Rantai penyebab kehilangan data

Tiga fakta yang bertemu:

**a. Lokasi tenant ada di dalam folder aplikasi**

```php
// config/tenant.php
'database_path' => database_path('tenants'),
// → /var/www/html/database/tenants/company_000001.sqlite
```

**b. Dockerfile menyalin seluruh repo ke dalam image**

```dockerfile
COPY --chown=www-data:www-data . /var/www/html
```

**c. Berkas `.sqlite` tidak pernah ada di Git**

```
# .gitignore baris 28–31
/database/*.sqlite
/database/tenants/*.sqlite
/database/tenants/*.sqlite-shm
/database/tenants/*.sqlite-wal
```

Diverifikasi menyeluruh — nol berkas database di **seluruh riwayat** Git:

```bash
git rev-list --objects --all | grep -iE "\.sqlite"   # kosong
git ls-files database/tenants/                        # hanya .gitkeep
```

Jadi yang sampai ke container untuk folder itu **hanya `.gitkeep`** — berkas kosong
yang tugasnya cuma menahan agar folder kosong tetap ada di repo. Container start
dengan folder yang benar-benar kosong.

**Bukan Render yang menghapus apa pun. Datanya memang tidak pernah ikut berangkat.**

Dan ini tidak butuh deploy: Render free tier mematikan service saat idle, lalu start
ulang dari image yang sama. Data bisa hilang semalaman tanpa ada push sama sekali.

### Gejala turunan yang mudah salah didiagnosis

Wizard setup yang **memantulkan user kembali ke form setup** setelah diselesaikan
adalah akar masalah yang sama. Status setup tersimpan di tenant database. Kalau
container restart di tengah pengisian, statusnya ikut lenyap, lalu `useSetupGate`
di frontend membacanya sebagai "setup belum selesai" dan mengembalikan user ke
wizard. Satu akar, dua gejala.

---

## 4. Bentuk penggantinya: schema per perusahaan

```
Database Neon (satu, sama dengan central)
│
├── schema "public"            ← central
│   ├── users
│   ├── companies
│   ├── plans
│   ├── subscriptions
│   └── tenant_databases
│
├── schema "tenant_000006"     ← data akuntansi PT A
│   ├── chart_of_accounts
│   ├── journals
│   ├── journal_lines
│   └── ...
│
└── schema "tenant_000007"     ← data akuntansi PT B
    └── ...
```

Satu database, satu connection string, tanpa layanan tambahan. Baris
`tenant_databases` untuk tenant baru berbunyi:

| company_id | database_name | database_path | driver |
|---|---|---|---|
| 6 | `tenant_000006` | `tenant_000006` | `pgsql` |

`database_path` menyimpan nama schema yang sama — Postgres tidak punya padanan
"lokasi di disk" yang berguna bagi aplikasi. Kolom itu `unique()` dan NOT NULL, dan
nama schema memenuhi keduanya, **jadi tidak ada migration central baru**.

### Kenapa schema, bukan satu database per perusahaan

| Alasan | Penjelasan |
|---|---|
| Atomisitas provisioning | `CREATE SCHEMA` boleh jalan di dalam transaksi, `CREATE DATABASE` **tidak**. Provisioning saat ini atomik — baris `companies`, `company_users`, `tenant_databases`, dan wadah datanya dibuat dalam satu transaksi. Database-per-tenant membongkar jaminan itu. |
| Batas koneksi | Tiap database butuh pool sendiri. 20 perusahaan = 20 pool. Dengan schema semuanya berbagi satu koneksi; yang berganti hanya `search_path`. |
| Query lintas perusahaan | Postgres tidak bisa query lintas database. Dengan schema, laporan gabungan lintas perusahaan milik satu client masih mungkin. |

### Batasnya — jujur

Schema-per-tenant lazim dan layak production, tapi tidak memberi semua yang
diberikan database-per-tenant:

| | Schema per tenant | Database per tenant |
|---|---|---|
| Selamat dari deploy | ✅ | ✅ |
| Backup & PITR | ✅ seluruh database sekaligus | ✅ per perusahaan |
| Restore satu perusahaan ke kemarin | ⚠️ perlu `pg_dump` schema + restore manual; PITR akan menarik mundur semua perusahaan | ✅ |
| Tenant besar membebani yang lain | ⚠️ bisa | ✅ terisolasi |
| Isolasi data | `search_path` (dikunci test) | mutlak |

---

## 5. Isolasi: kenapa `search_path` TIDAK menyertakan `public`

Ini keputusan keamanan, bukan gaya.

Tabel central tinggal di `public`. Kalau `public` ikut di `search_path`, tabel tenant
yang kebetulan belum ada akan **diam-diam jatuh ke tabel central bernama sama** —
satu perusahaan bisa membaca data lintas tenant tanpa memunculkan error apa pun.

Membiarkan query gagal jauh lebih baik daripada diam-diam menjawab dengan data yang
salah. `pg_catalog` tetap tersedia otomatis, jadi fungsi bawaan Postgres aman.

Dikunci di `tests/TenantPgsql/PostgresTenantIsolationTest.php`, termasuk pembuktian
bahwa tabel di `public` **tidak** terjangkau dari koneksi tenant.

---

## 6. Lapisan `TenantStorage`

Seluruh urusan penyimpanan tenant ada di `app/Shared/Tenant/Storage/`:

| Berkas | Peran |
|---|---|
| `TenantStorage.php` | interface |
| `SqliteTenantStorage.php` | satu berkas per perusahaan — test & lokal |
| `PostgresTenantStorage.php` | satu schema per perusahaan — production |
| `TenantStorageManager.php` | memilih driver |

**Driver ditentukan per baris `tenant_databases`, bukan global.** Ini disengaja:
saat peralihan, tenant SQLite lama dan tenant Postgres baru hidup berdampingan di
satu database central. Tenant baru memakai `config('tenant.driver')`; tenant lama
tetap dibaca dengan driver yang tercatat di barisnya sendiri.

Tidak ada kode di luar folder `Storage/` yang tahu bentuk penyimpanan tenant.
Menambah driver lain (mis. database-per-tenant) cukup mengimplementasikan interface
yang sama dan mendaftarkannya di `TenantStorageManager::driver()`.

### Yang ikut dirombak

`TenantConnectionManager`, `TenantProvisioningService`, `TenantMigrationService`,
`TenantRepairService`, `CompanyPurgeService`, `CompanyCreationService`,
`CompanyUserAssignmentService`, `ClientUserService`, `MeasureTenantStorageCommand`,
`CheckTenantStorageCommand`, `SeedDemoCompaniesCommand`, dan dua report summary.

Tiga di antaranya akan **patah diam-diam** di Postgres kalau tidak ikut diperbaiki:

- `CompanyUserAssignmentService` memanggil `File::exists()` pada tenant → setiap
  penambahan anggota perusahaan ditolak dengan alasan yang menyesatkan.
- `CompanyCreationService::rollbackProvisioning` memakai `File::delete()` → tidak
  melakukan apa pun, schema tertinggal yatim tiap kali migrasi tenant gagal.
- Kedua report summary sudah driver-aware, tapi cabang non-sqlite-nya mengirim
  `DATE_FORMAT()` — fungsi **MySQL** yang tidak ada di Postgres. Ekspresi periode
  dipindah ke `App\Shared\Database\DatePeriodExpression` dengan cabang `pgsql`.

---

## 7. Cutover

**1.** Di Render tambah environment variable:

```
TENANT_DRIVER=pgsql
```

Kosongkan `TENANT_PGSQL_CONNECTION` — defaultnya mengikuti koneksi central, dan itu
yang benar karena schema tenant dititipkan di database yang sama.

**2.** ⚠️ **Jebakan paling penting:** menyimpan environment variable di Render
**memicu restart, bukan build ulang**. Service start lagi memakai **image yang sudah
ada** — tidak menarik kode baru dari GitHub. Kode lama tidak mengenal `TENANT_DRIVER`
sama sekali; variabel itu diabaikan total dan hasilnya tetap `sqlite`.

Jadi setelah memasang env var, wajib **Manual Deploy → Deploy latest commit**, dan
tunggu sampai status **Live** sebelum membuat perusahaan.

**3.** Perusahaan **baru** langsung mendapat schema Postgres.

**4.** Perusahaan **lama** barisnya masih `driver=sqlite` dan wadahnya sudah lenyap.
Di admin panel → edit client → tab **Paket & Langganan** → **Pemakaian Penyimpanan**
→ tombol **Buat Ulang Database**.

`TenantRepairService` selalu membangun ulang memakai driver yang berlaku sekarang,
jadi baris `sqlite` bangkit sebagai schema Postgres. Nama tenant hanya ditulis ulang
kalau drivernya benar-benar berpindah — kalau tidak, perbaikan sqlite ke sqlite akan
memindahkan berkas tanpa alasan dan meninggalkan yatim. Data lama **tidak** dipulihkan;
memang sudah hilang sejak deploy sebelumnya.

### Salah setel

`TENANT_DRIVER=pgsql` sementara koneksi central ternyata bukan Postgres akan **gagal
keras** saat provisioning, dengan pesan yang menyebut koneksi dan driver yang
ditemukan. Disengaja: tanpa itu, config koneksi tetap disalin beserta `search_path`
yang tidak dikenal drivernya, dan kegagalannya baru muncul jauh kemudian sebagai
error SQL yang menyesatkan.

---

## 8. Query diagnosa

Jalankan di Neon SQL Editor.

**Perusahaan mana memakai driver apa** — pertanyaan pertama yang harus dijawab:

```sql
SELECT c.id, c.name, td.driver, td.database_name, c.created_at
FROM companies c
LEFT JOIN tenant_databases td ON td.company_id = c.id
ORDER BY c.id;
```

| `driver` | Artinya |
|---|---|
| `sqlite` | masih pakai berkas — **inilah** yang datanya hilang tiap rebuild |
| `pgsql` | sudah pindah, aman |
| `NULL` | baris tenant-nya hilang sama sekali |

**Apakah sudah ada schema tenant:**

```sql
SELECT schema_name FROM information_schema.schemata
WHERE schema_name LIKE 'tenant_%';
```

**Apakah data akuntansi benar-benar ada di Neon** — pembuktian paling langsung:

```sql
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_name IN ('chart_of_accounts', 'journals', 'journal_lines');
```

Selama tenant masih `sqlite`, hasilnya **kosong** — data itu memang tidak pernah ada
di Neon. Setelah pindah, ia muncul di schema `tenant_00000X`.

---

## 9. Menjalankan tes

Mayoritas tes tetap berjalan di atas tenant SQLite — cepat dan tidak butuh server.
Yang tidak bisa dibuktikan suite itu adalah hal yang memang berbeda antar database:
sintaks DDL, perilaku `search_path`, dan fungsi tanggal. Persis di situ bug production
bersembunyi — `DATE_FORMAT()` lolos di SQLite karena cabangnya tidak pernah dipakai,
lalu meledak begitu tenant benar-benar berjalan di Postgres.

Celah itu ditutup suite terpisah (18 test: provisioning, repair, purge, 100 migration
tenant di Postgres asli, ekspresi periode, isolasi antar tenant):

```bash
TENANT_TEST_PGSQL_URL="postgresql://..." vendor/bin/phpunit --testsuite=TenantPgsql
```

Pakai connection string **direct**, bukan yang pooled — migration gagal di PgBouncer
dengan `SQLSTATE[25P02]`. (Error yang sama muncul dulu saat memindahkan database
central ke Neon.)

Tanpa variabel itu seluruh suite tersebut di-skip, sehingga `php artisan test` tetap
hijau di mesin tanpa Postgres.

**Catatan status:** per 2026-09-21 suite `TenantPgsql` **belum pernah dijalankan**
terhadap Postgres sungguhan — belum ada `TENANT_TEST_PGSQL_URL` yang disetel. Jadi
jalur Postgres teruji secara kode, belum secara eksekusi. Saran: pakai **branch Neon
gratis** khusus tes, jangan database central production.

---

## 10. Dua jebakan yang memakan waktu paling lama

Keduanya tidak terlihat dari kode, dan keduanya berulang kalau tidak dicatat.

### Region database harus sama dengan region aplikasi

Project Neon pertama dibuat di `us-east-2` (Ohio) sementara Render berjalan di
Oregon (`us-west1`). Tiap perintah SQL menempuh ~50–70 ms pulang-pergi. Karena
provisioning menjalankan ratusan perintah DDL, pembuatan perusahaan menggantung
lebih dari dua menit lalu diputus gateway — tanpa pesan error apa pun, karena
respons tidak pernah sempat dikirim.

Setelah project Neon dipindah ke `us-west-2` (Oregon), waktunya turun ke hitungan
detik.

Untuk aplikasi yang membangun 70 tabel setiap kali perusahaan dibuat, jarak
antara aplikasi dan database bukan penyetelan halus — ia menentukan bisa atau
tidak. Cara memeriksa region Render: dashboard → service → **Settings → Region**.

### `$table->enum(...)->change()` tidak jalan di Postgres

Di Postgres, `enum()` bukan tipe tersendiri melainkan `varchar` + CHECK
constraint terpisah. Laravel menempelkan `check (...)` langsung ke
`ALTER COLUMN ... TYPE`, yang bukan sintaks sah dan gagal dengan
`SQLSTATE 42601`. Karena migration tenant dijalankan saat provisioning, satu
migration seperti ini membuat **setiap** pembuatan perusahaan gagal.

Di SQLite gejalanya tidak pernah muncul: `change()` di sana membangun ulang
seluruh tabel, jadi enum baru terpasang tanpa keluhan.

**Aturannya: jangan pernah `->change()` kolom enum di migration tenant.** Ganti
daftar nilainya lewat helper yang sadar driver — contohnya `setStatusValues()`
di `2026_08_14_000003_add_versioning_to_budget_submissions_table.php`, yang
membuang CHECK constraint lama (namanya dicari dari `pg_constraint`, bukan
ditebak) lalu memasang yang baru.

### Pelajaran umumnya

Kedua bug ini lolos dari 1.370 test karena test berjalan di SQLite lokal —
tidak ada latensi jaringan, dan `change()` selalu bekerja. Yang membedakan
SQLite dari Postgres justru persis di titik yang tidak teruji.

Karena itu **suite `TenantPgsql` wajib dijalankan setiap kali menambah migration
tenant** (§9). Bug `enum()` ditemukan dengan cara paling mahal — satu per satu
lewat UI production, tiap putaran butuh deploy — padahal satu kali menjalankan
suite itu akan menampilkan semuanya sekaligus.

## 11. Rujukan

- Prosedur cutover ringkas: `laravel_backend/docs/tenant-postgres-cutover.md`

| Commit | Isi |
|---|---|
| `b1c5b9e` | lapisan `TenantStorage` + schema Postgres per tenant (1.370 test, 1.365 lulus, 5 skip, 0 gagal) |
| `362c4b3` | alasan gagal provisioning ditampilkan saat `APP_DEBUG` menyala |
| `d905ea6` | perbaikan `enum()->change()` yang menggagalkan migrasi di Postgres |

Catatan: `362c4b3` yang akhirnya memecahkan kebuntuan. Selama pesan errornya
masih generik, penyebabnya hanya bisa ditebak — dan empat tebakan berturut-turut
meleset. Begitu alasan aslinya tampil di layar, bug-nya ketahuan dalam hitungan
menit. Kalau ada kegagalan provisioning lagi, nyalakan `APP_DEBUG` lebih dulu
sebelum menganalisis apa pun.
