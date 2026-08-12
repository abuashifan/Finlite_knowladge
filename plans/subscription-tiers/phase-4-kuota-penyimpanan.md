# Fase 4 — Kuota Penyimpanan

**Status: ✅ SELESAI 2026-08-12.** Ringkasan eksekusi ada di **§ Hasil
eksekusi** di akhir dokumen ini — baca itu dulu kalau menyentuh ulang
berkas-berkas fase ini. Dikerjakan SETELAH Fase 5 (prasyarat kebersihan di
bawah sudah ditutup lebih dulu). Sisa dokumen ini adalah rancangan ASLI
(pra-eksekusi), dipertahankan sebagai riwayat keputusan.

Diminta pemilik produk 2026-08-11: *"buat skema untuk besarnya kapasitas hardisk
atau alokasi cloud-nya."*

Fase ini menggantikan `max_transactions_per_month` yang dibuang (keputusan
2026-08-11: **tidak ada batas jumlah transaksi**). Membatasi jumlah transaksi
menghukum client yang paling aktif — justru yang paling bernilai. Kalau biaya
perlu dikendalikan, batasnya lebih tepat di penyimpanan.

## Pengukuran nyata, bukan taksiran

Diukur langsung dari dua tenant di mesin dev, 2026-08-11:

| | Ukuran | Tabel | Baris jurnal |
|---|---|---|---|
| `company_000001.sqlite` | 1,7 MB | 78 | 66 |
| `company_000002.sqlite` | 1,9 MB | 78 | 361 |

Dua angka penting yang bisa ditarik:

- **Dasar per perusahaan ≈ 1,7 MB.** Itu biaya skema 87 migrasi sebelum satu
  transaksi pun dicatat. Setiap perusahaan baru langsung memakan segitu.
- **Pertumbuhan ≈ 0,7 KB per baris jurnal.** Selisih 0,2 MB untuk ~300 baris
  jurnal.

## Proyeksi untuk kasus pemakaian yang diminta

Kasus yang mendorong rencana data-import: **500 faktur per hari**.

Satu faktur menghasilkan kira-kira: baris faktur + 3 baris barang + entri jurnal
+ 4 baris jurnal + mutasi piutang ≈ **3 KB**.

| | Per bulan (22 hari kerja) | Per tahun |
|---|---|---|
| 500 faktur/hari | 11.000 faktur ≈ **33 MB** | ≈ **400 MB** |
| 100 faktur/hari | 2.200 faktur ≈ 7 MB | ≈ 80 MB |
| 20 faktur/hari | 440 faktur ≈ 1,3 MB | ≈ 16 MB |

Ditambah berkas impor: satu berkas 1.000 baris ≈ 150 KB, satu per hari, masa
simpan 30 hari ≈ **5 MB tetap**.

**Kesimpulannya: penyimpanan bukan biaya yang menakutkan.** Client Pro paling
sibuk sekalipun tumbuh di bawah 500 MB setahun. Yang menjadikannya biaya adalah
**jumlah perusahaan × dasar 1,7 MB**, bukan volume transaksi.

## Skema yang diusulkan

| | Basic | Pro | Enterprise | Custom |
|---|---|---|---|---|
| Perusahaan | 1 | 3 | 5 | manual |
| **Kuota penyimpanan per perusahaan** | **1 GB** | **2 GB** | **5 GB** | manual |
| Total maksimum per client | 1 GB | 6 GB | 25 GB | manual |
| Masa simpan berkas impor | 30 hari | 30 hari | 90 hari | manual |

Angkanya sengaja **longgar** — sekitar dua kali lipat proyeksi paling sibuk.
Alasannya: kuota penyimpanan bukan alat jualan di sini, melainkan **pagar
terhadap pemakaian anomali** (client yang mengunggah berkas raksasa berulang
kali, atau kesalahan yang menulis jutaan baris). Kuota yang ketat akan lebih
sering menghukum pemakaian normal daripada menghemat biaya.

## Cara menegakkannya

**Yang diukur:** ukuran berkas SQLite tenant + total berkas impor yang tersimpan
untuk perusahaan itu.

**Kapan diperiksa:** bukan tiap request — itu pemborosan. Cukup:

1. **Sebelum menerima unggahan impor** — satu-satunya jalur yang bisa menambah
   penyimpanan secara melonjak.
2. **Sekali sehari** lewat command terjadwal, yang mencatat ukuran tiap tenant ke
   database pusat.

Kolom `tenant_databases` adalah tempat yang wajar untuk menyimpan hasil
pengukuran harian (`size_bytes`, `measured_at`).

**Saat terlampaui:** tahan penambahan data baru dengan pesan yang jelas, **jangan
kunci akses baca**. Sejalan dengan aturan yang sudah berlaku di seluruh rencana
ini — yang ditahan adalah pertumbuhan, bukan yang sudah ada.

## Area admin

Daftar client menampilkan pemakaian penyimpanan per perusahaan, dengan penanda
saat mendekati batas. Itu juga yang memberi kamu data nyata untuk menyesuaikan
angka di atas setelah beberapa bulan — angka sekarang adalah tebakan terdidik
dari dua tenant yang isinya masih sedikit.

## Prasyarat kebersihan ⚠️

Sebelum kuota apa pun ditegakkan, **kebocoran berkas test harus ditutup lebih
dulu**. Terukur 2026-08-11: `database/tenants/` memuat **33.790 berkas, 53 GB**,
di mana 4.471 di antaranya dibuat pada hari itu juga oleh test suite. Setiap
tenant uji menjalankan 87 migrasi lalu meninggalkan berkas 1,7 MB yang tidak
pernah dihapus.

Itu bukan masalah kuota client — itu masalah kebersihan mesin — tapi ia mengotori
setiap pengukuran penyimpanan dan harus beres sebelum fase ini bermakna. Rincian
dan perbaikannya ada di
[Fase 5](phase-5-kebersihan-tenant.md).

## Alokasi server — bahan hitung kasar

Dengan skema di atas, satu server dengan **100 GB** ruang tenant menampung
kira-kira:

| Bauran client | Perkiraan |
|---|---|
| 100% Basic (1 perusahaan) | ~1.000 client *(dibatasi kuota, bukan pemakaian nyata)* |
| Realistis (pemakaian nyata, bukan kuota) | **beberapa ribu client** |

Perbedaan besar antara keduanya menegaskan poin di atas: kuota adalah pagar, dan
pemakaian sebenarnya jauh di bawahnya. Untuk perencanaan kapasitas, pakai
pengukuran harian dari command terjadwal — bukan penjumlahan kuota.

---

## Hasil eksekusi 2026-08-12

### Angka yang dipakai

| | Free | Basic | Pro | Enterprise | Custom |
|---|---|---|---|---|---|
| Kuota penyimpanan | 500 MB | 1 GB | 2 GB | 5 GB | manual, cadangan 5 GB |
| Masa simpan impor | 30 hari | 30 hari | 30 hari | 90 hari | manual, cadangan 90 hari |

Persis rancangan §"Skema yang diusulkan", ditambah Free (tidak disebut
rancangan — diberi 500 MB, separuh Basic, konsisten dengan Free sebagai tier
paling terbatas di semua sumbu lain). Custom membaca `users.storage_quota_mb`
/ `users.import_retention_days` kalau diisi, sama persis pola
`company_quota`/`user_quota` dari Fase 0.

### File yang dibangun

| Berkas | Isi |
|---|---|
| `database/migrations/2026_08_12_000002_add_storage_quota_to_plans_and_tenant_databases.php` | `plans.storage_quota_mb`/`import_retention_days`; `users.storage_quota_mb`/`import_retention_days` (override Custom); `tenant_databases.measured_at` — `size_bytes` **sudah ada** sejak Mei, cuma tidak pernah diisi. |
| `app/Shared/Subscription/StorageQuotaService.php` | `quotaBytesFor`, `usedBytes`, `canAccept`, `retentionDaysFor`, `summaryFor`. Membaca angka pengukuran TERAKHIR, tidak menghitung ulang tiap panggilan — alasan sama dengan cache lapis paket di Fase 1. |
| `app/Console/Commands/MeasureTenantStorageCommand.php` (`storage:measure`) | Ukur sqlite tenant + berkas impor per perusahaan, tulis `size_bytes`/`measured_at`. |
| `app/Console/Commands/SweepImportRetentionCommand.php` (`imports:sweep-retention --dry-run`) | Hapus batch impor + berkasnya yang lebih tua dari masa simpan tier. |
| `app/Modules/Imports/Services/ImportBatchService.php` (diubah) | `ensureStorageQuotaAvailable()` — dipanggil di awal `upload()`, sebelum berkas dibaca/dihash. |
| Perluasan `ClientUserController`/`ClientUserService` (Admin) | `GET /admin/clients/{id}/storage` — daftar per perusahaan: `used_bytes`, `quota_bytes`, `percent_used`, `can_accept`, `measured_at`, `near_limit` (≥90%). |
| Frontend: `StorageUsageSection.tsx` | Tab "Penyimpanan" di form client admin — bar per perusahaan + penanda mendekati batas. |

### Deviasi dari rancangan

**Cakupan sweep retensi dipersempit ke status `failed` saja.** Rancangan
mengasumsikan siklus hidup batch impor yang lengkap (draft → ... →
selesai/dibatalkan, disimpan sampai masa berlaku habis). Diverifikasi saat
eksekusi: modul Imports **masih Fase 0** — `ImportBatchService::commit()`
sendiri melempar "Commit impor belum tersedia di Fase 0", dan `cancel()`
menghapus baris + berkas **seketika** (bukan menandai `cancelled` untuk
disimpan). Satu-satunya status terminal yang sungguhan ada hari ini adalah
`failed`. `SweepImportRetentionCommand::TERMINAL_STATUSES` didokumentasikan
eksplisit sebagai daftar yang perlu ditambah `committed` begitu commit
sungguhan dibangun — menebak nama status yang belum ditulis modul lain akan
diam-diam tidak pernah cocok dengan apa pun.

**Gerbang kuota di service layer, bukan FormRequest.** Percobaan pertama
menaruh pemeriksaan di `StoreImportRequest::withValidator()` (pola yang sama
dengan gerbang `transaction_approval` Fase 2). Dipindah ke
`ImportBatchService::upload()` karena modul ini sudah punya pola identik
untuk kasus serupa — `DuplicateImportFileException` dilempar dari service,
ditangkap controller, dikembalikan sebagai respons berkode. Memakai
`ApiException::make(STORAGE_QUOTA_EXCEEDED, ..., 422, ..., $summary)` (bukan
exception kustom baru) mengikuti persis pola `ensureNoActiveBatch()`/
`ensureProfileExists()` di file yang sama — konsisten dengan konvensi modul
yang sudah ada, bukan pola baru bersebelahan.

### Test

15 test baru: `StorageQuotaServiceTest` (9 — kuota per tier, override Custom,
fallback, `canAccept` menghitung unggahan yang sedang diajukan, retensi per
tier, ringkasan persen), `MeasureTenantStorageCommandTest` (4 — ukur sqlite +
impor, abaikan tenant nonaktif, jalan tanpa data), `StorageQuotaImportGateTest`
(3 — ditolak saat kuota penuh, lolos saat longgar, Pro punya ruang lebih dari
Basic), `SweepImportRetentionCommandTest` (4 — hapus batch `failed` lama,
batch aktif tidak pernah dihapus walau tua, Enterprise menyimpan lebih lama,
`--dry-run` tidak menghapus apa pun), plus 2 test admin endpoint storage.

Plus 2 test endpoint admin `GET /admin/clients/{id}/storage` (mendekati batas,
belum pernah diukur). **Total 22 test baru** (1249 → 1271). Suite penuh:
**1271 test, 1266 lulus, 5 skip, 0 gagal.**

### Verifikasi di database dev

```
php artisan migrate --path=.../2026_08_12_000002_...   → dijalankan (backup diambil dulu)
php artisan db:seed --class=PlanSeeder                  → angka tier terisi
php artisan storage:measure                             → company_000001: 1.71 MB, company_000002: 1.88 MB
```

Cocok dengan pengukuran manual 2026-08-11 di dokumen ini (1,7 MB / 1,9 MB) —
memvalidasi command mengukur dengan benar terhadap tenant nyata.

### Yang belum dikerjakan

- **Penjadwalan `storage:measure` dan `imports:sweep-retention`** — sama
  seperti `subscriptions:sweep` di Fase 3, belum ada `Schedule::command()`
  yang mendaftarkannya (repo ini tidak punya pola scheduling sebelumnya).
  Perlu dijalankan manual atau disambungkan ke cron saat deploy.
- **Menambah `committed` ke `SweepImportRetentionCommand::TERMINAL_STATUSES`**
  begitu `ImportBatchService::commit()` sungguhan dibangun — lihat deviasi di
  atas.
- **Indikator "mendekati batas" di daftar client** (bukan hanya di halaman
  detail) — akan perlu query agregat per baris di `AdminClientsPage`; belum
  dikerjakan, dianggap di luar cakupan minimum "area admin menampilkan
  pemakaian penyimpanan" karena halaman detail sudah menampilkannya lengkap
  per perusahaan.
