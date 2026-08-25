# Fase 7 — Impor Saldo Awal & Aset Tetap Awal

> Status: **✅ Terimplementasi penuh** (2026-08-25), termasuk 7F dan 7D-1.
> Prasyarat: Fase 0–5 selesai (mesin impor + profil master + profil transaksi).
>
> ⚠️ **Koreksi terhadap draf pertama rencana ini.** Draf awal menyebut
> `fixed_asset_categories` "tidak pernah di-seed" dan menjadikannya pemblokir
> keras. **Itu salah.** Migration tenant
> `2026_06_15_000001_create_fixed_asset_tables.php` sudah menanam 15 kategori
> default lewat `DB::table(...)->insert(...)` saat tabelnya dibuat — pencarian
> awal hanya menyisir `database/seeders/` dan `app/`, jadi melewatkannya.
> Celah yang NYATA lebih sempit dan dijelaskan di 7A di bawah.

## Kenapa fase ini ada

Setup wizard sekarang mengizinkan user **melewati** saldo awal dan aset tetap
awal lewat dua checkbox di Step 5, dengan janji eksplisit di layar:

> *"Perusahaan ini belum punya saldo awal — lanjutkan, akan diisi nanti."*
> *"Perusahaan ini belum punya aset tetap awal — lanjutkan, akan diisi nanti."*

Janji itu saat ini hanya bisa ditepati dengan **mengetik manual**:

| Data | Satu-satunya jalur hari ini | Realistis? |
|---|---|---|
| Saldo awal | `LineItemsTable` di `OpeningBalanceBatchPage` — satu baris per akun | Klien pindahan punya 40–150 akun bersaldo |
| Aset tetap awal | `FixedAssetFormPage` (42 KB, form panjang) — satu aset per submit | Klien pindahan punya puluhan hingga ratusan aset |

Impor untuk keduanya **tidak ada**. Enam profil impor yang sudah jalan
(kontak, produk, COA, faktur penjualan, tagihan vendor, jurnal umum) semuanya
profil operasional/master — tidak satu pun menyentuh saldo awal.

Ini melengkapi maksud asli rencana impor: master data lebih dulu supaya klien
baru tidak mengetik ulang data lamanya. Saldo awal dan aset tetap adalah sisa
data lama yang belum kebagian.

---

## Keadaan terverifikasi 2026-08-25

### Yang sangat menguntungkan — mesin impor sudah profile-driven ujung ke ujung

`ImportController::profiles()` mengembalikan **seluruh** isi
`config('imports.profiles')` apa adanya, dan `ImportPage.tsx` (565 baris)
membangun dropdown profil, unduhan templat, pemetaan kolom, tabel pratinjau,
dan tombol commit **sepenuhnya dari respons itu**.

**Konsekuensi: frontend halaman impor tidak perlu diubah sama sekali.**
Menambah profil = tiga sentuhan backend:

1. Entri di `config/imports.php`
2. Kelas committer baru di `app/Modules/Imports/Services/Committers/`
3. Registrasi di `ImportCommitterFactory` + whitelist di `ImportController`

### Aturan keras yang mengikat fase ini

Dari [README](README.md) rencana ini, tidak boleh dilanggar:

> Importer **wajib** lewat service dokumen, tidak boleh menulis ke tabel secara
> langsung.

Untuk fase ini artinya: `OpeningBalanceBatchService` dan `FixedAssetService` —
bukan `OpeningBalanceLine::create()` atau `FixedAsset::create()`.

### Integrasi yang SUDAH ADA dan menentukan seluruh desain fase ini

Ini temuan paling penting, dan mengubah urutan pekerjaan:

**Aset tetap awal sudah otomatis masuk ke batch saldo awal.**
`OpeningBalanceBatchService::fixedAssetSystemLines()` membaca tabel
`fixed_assets` yang `source_type = 'opening_import'`, lalu menghasilkan dua
baris **system-generated**:

| Baris | Akun | Sisi | Nilai |
|---|---|---|---|
| `Opening fixed asset cost` | mapping `fixed_assets.cost` | Debit | `SUM(acquisition_cost)` |
| `Opening accumulated depreciation` | mapping `fixed_assets.accumulated_depreciation` | Kredit | `SUM(accumulated_depreciation)` |

Baris ini **dihitung saat `preview()`**, tidak disimpan — `replaceLines()`
selalu menulis `is_system_generated => false`, jadi isi tabel `opening_balance_lines`
seluruhnya baris manual.

Dan ada penjaganya: `additionalBlockingErrors()` menolak batch dengan
`FIXED_ASSET_CONTROL_DUPLICATE` kalau ada baris **manual** yang memakai akun
kontrol yang sama.

**Tiga konsekuensi keras untuk rencana ini:**

1. **CSV saldo awal TIDAK BOLEH memuat akun aset tetap** (harga perolehan &
   akumulasi penyusutan). Kalau dimuat, batch gagal validasi. Ini harus jadi
   validasi tingkat baris di committer — bukan catatan kecil di templat yang
   akan diabaikan orang.
2. **Urutan wajib: impor aset tetap DULU, baru saldo awal.** Bukan preferensi —
   angka aset tetap masuk ke total debit/kredit batch, jadi neraca saldo awal
   tidak akan pernah balance kalau asetnya belum ada.
3. Ekuitas penyeimbang ditangani mapping `opening_balance.equity` yang sudah
   ada. Impor tidak perlu memikirkannya.

### Yang belum ada dan menghalangi

| Temuan | Dampak | Terverifikasi di |
|---|---|---|
| ~~`fixed_asset_categories` tidak pernah di-seed~~ → **SALAH, dikoreksi.** Kategorinya ada; yang null adalah seluruh kolom `*_account_id`-nya. | Bukan pemblokir impor. Tapi 12 kunci mapping per kelas dari `3e6bcbb` jadi tidak pernah dipakai jurnal. Ditutup 7A. | `DB::table('fixed_asset_categories')->insert(...)` di migration tenant `2026_06_15_000001`, baris 170–190 |
| `StoreFixedAssetRequest` tidak punya aturan `accumulated_depreciation`. | Controller memakai `$request->validated()`, jadi field itu **dibuang diam-diam**. Aset perolehan 2020 yang diimpor per 2026 masuk dengan akumulasi penyusutan 0 dan NBV = harga perolehan penuh. Salah secara material. | `assetPayload()` baris 513–514 **sudah** menghormati field itu — hanya request-nya yang menutup pintu |
| `FixedAssetService::capitalize()` **memposting jurnal** (Aset Dr / Kliring Cr). | Untuk aset awal ini dobel — batch saldo awal sudah membukukan harga perolehan lewat system line. Aset awal harus berhenti di status `draft`, tidak boleh lewat `capitalize()`. | `capitalize()` baris 188–191 |
| `replaceLines()` **menghapus semua baris** sebelum insert. | Impor naif akan menghapus baris yang sudah diketik manual user. Committer wajib baca-gabung-tulis. | baris 109: `$batch->lines()->delete()` |
| System line memakai mapping **generik** `fixed_assets.cost` / `fixed_assets.accumulated_depreciation`. | Setelah pemisahan akun per kelas (kendaraan/gedung/peralatan/software) di commit `3e6bcbb`, seluruh aset awal — apa pun kelasnya — tetap mendarat di **satu** akun kontrol generik (Peralatan 1530/1531). Neraca benar totalnya, tapi rinciannya rata. | `fixedAssetSystemLines()` baris 443–452 |

---

## Rancangan

### Fase 7A — Sambungkan kategori aset tetap ke akunnya ✅

**Bukan** "seed kategori" — kategorinya sudah ada. Yang tidak pernah terjadi
adalah pengisian kolom `*_account_id`-nya: migration yang menanam kategori
berjalan **sebelum satu akun COA pun ada**, jadi tidak ada yang bisa ditunjuk,
dan kolom itu ditinggal null selamanya.

Akibatnya `FixedAssetService::assetAccount()` dkk selalu jatuh ke mapping
generik — dan 12 kunci mapping per kelas dari commit `3e6bcbb` **tidak pernah
menggerakkan jurnal**, cuma jadi acuan saat user mengisi kategori manual.

Yang dikerjakan:

1. `config/fixed_asset_categories.php` — **hanya** peta kode kategori → kunci
   mapping akun. Nama/kelas/jenis penyusutan/umur manfaat sengaja TIDAK
   diduplikasi di sini; itu milik migration. (Draf pertama file ini
   menduplikasinya, dan langsung melenceng: config menulis umur manfaat
   TRADEMARK 4 tahun sementara migration 8.)
2. `FixedAssetCategoryAccountLinker::linkDefaults()` — dipanggil
   `CoaTemplateService::applyTemplate()` setelah `syncDefaultMappingsFromConfig()`.
   Idempoten, hanya mengisi kolom yang masih null, tidak pernah menimpa pilihan
   user. Pemetaan yang dipakai:

   | Kategori | Aset | Akum. penyusutan | Beban |
   |---|---|---|---|
   | `VEHICLE` | 1510 Kendaraan | 1511 | 6170 |
   | `BUILDING` | 1520 Gedung | 1521 | 6171 |
   | `MACHINE`, `OFFICE_EQUIP`, `IT_EQUIP`, `FURNITURE`, `LEASEHOLD`, `OTHER` | 1530 Peralatan | 1531 | 6172 |
   | `SOFTWARE`, `PATENT`, `COPYRIGHT`, `TRADEMARK` | 1540 Perangkat Lunak | 1541 | 6175 |
   | `LAND`, `CIP`, `GOODWILL` | 1530 (sementara) | — (`depreciation_type` bukan `depreciation`) | — |

   `LAND`, `CIP`, dan `GOODWILL` sengaja **tidak** disambungkan: templat COA
   belum punya akun khusus untuk ketiganya, dan menyambungkannya ke akun
   Peralatan akan menaruh nilai tanah di baris peralatan pada neraca. Null =
   jatuh ke mapping generik, yaitu perilaku hari ini.

### Fase 7B — Profil impor `opening_balance` ✅

**Templat CSV**

| Header | Field | Wajib | Catatan |
|---|---|---|---|
| Account Code | `account_code` | ✅ | harus akun **postable** (bukan induk), aktif |
| Description | `description` | — | default: `Saldo awal` |
| Debit | `debit` | ✅¹ | ≥ 0 |
| Credit | `credit` | ✅¹ | ≥ 0 |

¹ Persis satu dari keduanya harus > 0 — pola yang sama dengan profil
`journal_entry` yang sudah ada.

Tidak ada kolom `Ref`: satu batch saldo awal per perusahaan, jadi tidak ada
pengelompokan. `required_fields` = `['account_code']`; sisanya divalidasi
committer supaya pesan galatnya spesifik.

**`validateRow()`**

1. Akun ada, aktif, **postable** — pakai `App\Shared\Rules\PostableAccount`
   yang sudah dipakai `ReplaceOpeningBalanceLinesRequest`, jangan tulis ulang
   cek `children()->exists()`.
2. Debit XOR Credit > 0.
3. Numerik, tidak negatif.
4. **Akun bukan akun kontrol aset tetap** → tolak dengan pesan yang menyebutkan
   sebabnya: *"Akun ini dihasilkan otomatis dari data aset tetap awal. Impor
   asetnya lewat profil Aset Tetap Awal, jangan dimasukkan di sini."* Sumber
   daftar akunnya: mapping `fixed_assets.cost` /
   `fixed_assets.accumulated_depreciation` — plus 12 kunci per kelas kalau 7A
   sudah membuat system line-nya per kelas.
5. Akun tidak muncul dua kali dalam satu berkas — pakai trait
   `DetectsDuplicateCodesInBatch` yang sudah ada.

**`commit()`**

```
batch = OpeningBalanceBatchService::latestActiveBatch()
        ?? OpeningBalanceBatchService::create(['opening_date' => <lihat 7B-2>])

if (! batch->editable())  → seluruh baris 'failed', pesan OPENING_BALANCE_NOT_EDITABLE

existing = batch->lines  (semuanya manual — system line dihitung saat preview)
merged   = existing + baris impor        // 7B-1
OpeningBalanceBatchService::replaceLines(batch, merged)
```

Committer **tidak** memvalidasi/memposting batch. Impor mengisi draft; user
tetap menekan Validasi → Posting sendiri di halaman Saldo Awal. Konsisten
dengan keputusan **draft-only** di [README](README.md), dan menjaga langkah
"user cek dulu" tetap ada.

**Keputusan terbuka 7B-1 — gabung atau ganti?**
`replaceLines()` menghapus semuanya. Tiga pilihan: gabung (impor menambah),
ganti (impor jadi sumber tunggal), atau checkbox di UI.
*Rekomendasi: gabung, dengan baris impor yang akunnya sudah ada di batch
ditandai invalid* — dengan pesan "Akun ini sudah punya baris saldo awal di
batch. Hapus dulu barisnya di halaman Saldo Awal, atau keluarkan dari berkas."
Alasannya: menghapus pekerjaan yang tak terlihat di layar adalah kejutan yang
merugikan; user yang memang ingin mengganti bisa mengosongkan batch dulu.

**Keputusan terbuka 7B-2 — `opening_date` saat committer membuat batch.**
Kalau belum ada batch aktif, committer harus memilih tanggal. Pilihan: hari
ini (seperti `OpeningBalanceStatusPage::handleStart()`), awal tahun fiskal, atau
kolom tambahan di CSV.
*Rekomendasi: awal tahun fiskal aktif, fallback hari ini.* Saldo awal per
tanggal hari ini hampir selalu salah, dan tanggal per-baris tidak masuk akal
untuk objek yang satu batch per perusahaan.

**Tier:** master (Basic+). Ini kebutuhan pindah masuk, bukan alat operasional
harian — sejajar dengan impor COA. Tambahkan ke `$masterProfiles` di
`Routes/api.php` **dan** ke array literal di `ImportController::storeMaster()`
(dua tempat, hardcoded terpisah — mudah terlewat).

**`async`:** `false`. Committer hanya menulis baris saldo awal, tidak ada
posting jurnal, ≤1.000 baris. Tidak butuh worker antrean.

### Fase 7C — Profil impor `fixed_asset_opening` ✅

**Templat CSV**

| Header | Field | Wajib | Catatan |
|---|---|---|---|
| Name | `name` | ✅ | |
| Category | `category` | ✅ | cocokkan `code` **atau** `name` kategori — `ResolvesModelByCodeOrName` sudah ada |
| Acquisition Date | `acquisition_date` | ✅ | `DD/MM/YYYY`, ≤ tanggal saldo awal |
| Acquisition Cost | `acquisition_cost` | ✅ | > 0 |
| Accumulated Depreciation | `accumulated_depreciation` | — | default 0, **tidak boleh > cost − salvage** |
| Salvage Value | `salvage_value` | — | default 0 |
| Useful Life Years | `useful_life_years` | — | wajib `4, 8, 10, 16, 20` — batasan `in:` yang sudah ada di request |
| Quantity | `quantity` | — | default 1 |
| Service Start Date | `service_start_date` | — | ≥ `acquisition_date` |
| Department | `department` | — | kode, opsional |
| Project | `project` | — | kode, opsional |
| Description | `description` | — | |

**Perubahan backend yang dibutuhkan sebelum committer bisa benar:**

1. `StoreFixedAssetRequest`: tambah
   `'accumulated_depreciation' => ['nullable','numeric','min:0']`.
   Tanpa ini seluruh kolom akumulasi penyusutan dibuang `validated()` dan
   angka NBV setiap aset impor salah. Perubahan aditif dan `nullable` — form
   yang sudah ada tidak terpengaruh.
2. Aturan silang `accumulated_depreciation <= acquisition_cost - salvage_value`.
   Letakkan di service, bukan hanya di request, supaya berlaku untuk kedua
   jalur (form dan impor).

**`commit()`**

```
foreach (baris valid) {
    FixedAssetService::create([
        ...,
        'source_type' => 'opening_import',      // dibaca SetupWizardService & OB batch
        'accumulated_depreciation' => ...,
    ])
}
```

Aset berhenti di status `draft`. **Jangan panggil `capitalize()`** — itu
memposting jurnal Aset Dr / Kliring Cr, sementara harga perolehan sudah dibukukan
batch saldo awal lewat system line. Memanggilnya membukukan aset dua kali.

Efek berantai yang otomatis dan diinginkan:

- `SetupWizardService::validateOpeningFixedAssets()` menghitung baris
  `source_type = 'opening_import'` → step Step 5 lolos tanpa checkbox.
- `OpeningBalanceBatchService::fixedAssetSystemLines()` langsung menampilkan
  baris kontrol di pratinjau saldo awal.

**Keputusan terbuka 7C-1 — status aset setelah setup difinalisasi.**
Aset `draft` tidak menghasilkan jadwal penyusutan; `generateSchedules()` hanya
berjalan saat `capitalized_at` terisi. Jadi aset awal tidak akan pernah
menyusut sampai ada yang mengaktifkannya. Butuh jalur "kapitalisasi tanpa
jurnal" — mungkin dijalankan saat `SetupWizardService::lockOpeningFixedAssetRecords()`,
yang memang sudah menyentuh baris yang sama.
*Sudah dikerjakan — lihat [Fase 7F](#fase-7f--aktivasi-aset-saldo-awal-) di
bawah.* Sengaja tidak diselundupkan ke committer impor: pemicunya adalah
posting batch saldo awal, bukan impornya.

**Tier:** master (Basic+), sama alasannya dengan 7B.
**`async`:** `false`.

### Fase 7D — Frontend: pintu masuk, bukan halaman baru ✅

`ImportPage` sudah mengurus semuanya begitu profil terdaftar. Yang kurang cuma
**cara menemukannya** — hari ini impor hanya ada di ribbon Master Data, jauh
dari tempat orang berpikir soal saldo awal.

1. **Tombol "Impor dari Berkas"** di `OpeningBalanceStatusPage` dan
   `OpeningBalanceBatchPage` (status `draft`/`reopened` saja) → buka
   `/master-data/import?profile=opening_balance`.
2. **Tombol serupa** di `FixedAssetListPage` → `?profile=fixed_asset_opening`.
3. `ImportPage` membaca query param `profile` untuk memilih dropdown awal —
   satu `useSearchParams`, ~5 baris.
4. **Petunjuk urutan di layar.** Saat profil `opening_balance` dipilih dan modul
   aset tetap aktif tapi belum ada baris `opening_import`, tampilkan catatan:
   *"Impor aset tetap awal dulu — harga perolehan dan akumulasi penyusutannya
   dihitung otomatis ke saldo awal, jadi jangan dimasukkan ke berkas ini."*
   Urutan yang salah menghasilkan galat neraca yang sangat membingungkan;
   satu kalimat di tempat yang tepat jauh lebih murah daripada mendiagnosisnya.
5. Tautan ke halaman impor dari **Step 5 wizard**, di sebelah dua checkbox
   "akan diisi nanti" — di situlah user pertama kali diberi tahu bahwa data
   ini bisa menyusul.

Tanpa file komponen baru. Kalau nanti ada, `docs/struktur_frontend.md` wajib
diperbarui (aturan `AGENTS.md`).

### Fase 7E — Verifikasi ✅

Backend (`vendor/bin/pint --test` + tes terkait, aturan `AGENTS.md`):

- `tests/Feature/Imports/OpeningBalanceImportTest.php`
  - baris valid → masuk sebagai baris manual batch
  - akun induk ditolak
  - akun kontrol aset tetap ditolak dengan pesan pengarah
  - baris manual yang sudah ada **tidak** terhapus (7B-1)
  - batch `posted`/`locked` → seluruh baris `failed`, tidak ada penulisan
- `tests/Feature/Imports/FixedAssetOpeningImportTest.php`
  - `source_type` tersimpan `opening_import`
  - `accumulated_depreciation` **tersimpan** (regresi langsung dari celah request)
  - `net_book_value` = cost − akum
  - kategori tak dikenal → baris invalid, pesan menyebut nama kategorinya
  - status berhenti di `draft`, **nol** `journal_entries` baru
- `tests/Feature/Setup/…` — setelah impor aset, step `opening_fixed_assets`
  valid tanpa `confirm_no_opening_fixed_assets`
- Tes seed kategori: perusahaan baru punya 15 kategori dengan akun tersambung

Frontend: `rtk tsc`, `rtk lint`, `npm run build` 0 error, lalu jalankan alurnya
di browser dengan perusahaan baru (Playwright, sama seperti verifikasi
Step 5/COA sebelumnya) — impor aset → impor saldo awal → validasi → posting.

---

## Urutan kerja

| Urutan | Isi | Kenapa di sini |
|---|---|---|
| 1 | **7A** seed kategori | Pemblokir keras 7C |
| 2 | **7C** profil aset tetap | Harus ada sebelum saldo awal bisa balance |
| 3 | **7B** profil saldo awal | Bergantung pada angka aset tetap |
| 4 | **7D** pintu masuk frontend | Setelah kedua profil hidup |
| 5 | **7E** verifikasi | |
| 6 | **7F** kapitalisasi aset awal tanpa jurnal (7C-1) | Sebelum penyusutan bulan pertama, bukan sebelum rilis impor |

Perhatikan 7C mendahului 7B — kebalikan dari urutan yang natural dibaca, dan
kebalikan dari urutan di judul fase ini. Itu dipaksa oleh integrasi system-line
yang sudah ada, bukan pilihan gaya.

### Fase 7F — Aktivasi aset saldo awal ✅

Aset hasil impor berhenti di `draft`, dan penyusutan bulanan digerakkan tabel
jadwal — bukan status aset. Tanpa jadwal, aset itu tidak pernah ikut
depreciation run, diam-diam, tanpa error. Ini yang ditutup 7F.

**Pemicunya posting, bukan tombol.** Sempat dirancang sebagai tombol manual
"Aktifkan Aset Saldo Awal" di Daftar Aktiva. Dibatalkan setelah ditemukan bahwa
`SetupWizardService::finalize()` **sendiri** yang memanggil `post()` di klik
terakhir wizard: selama wizard batch masih draft, jadi tombolnya mati sampai
halaman terakhir — lalu user mendarat di dashboard dan harus INGAT mampir ke
Aktiva Tetap. Lupa sekali = aset tidak pernah menyusut. Persis kegagalan diam
yang mau dihindari.

Aturannya sekarang seragam: **setiap batch saldo awal yang diposting sekaligus
mengaktifkan aset yang dibukukannya.** Berlaku untuk batch setup awal maupun
batch koreksi.

Yang dilakukan `FixedAssetService::activateOpeningAssets()`:

1. Nomor aset, `capitalized_at` = **tanggal saldo awal** (bukan `now()`), status aktif
2. Cap `opening_balance_batch_id`
3. Baris `fixed_asset_transactions` bertipe `opening_import`, menunjuk ke jurnal pembuka
4. Jadwal sisa nilai / sisa umur (lihat di bawah)
5. **Nol jurnal**

`capitalize()` menolak aset `opening_import` (`FIXED_ASSET_OPENING_NOT_CAPITALIZABLE`),
dan tombolnya disembunyikan di `FixedAssetFormPage` — tombol itu sebelumnya hidup
dan menekannya membukukan harga perolehan dua kali.

**Matematika jadwalnya** (`generateOpeningSchedules()`):

```
Periode pertama = bulan tanggal saldo awal   (BUKAN +1 bulan seperti aset baru)
Periode terakhir = last_depreciation_period  (dari tanggal mulai pakai ASLI)
Nilai dijadwalkan = depreciable_basis − accumulated_depreciation
```

Contoh terverifikasi di test: Avanza 250jt, akumulasi 23.437.500, perolehan
Mar 2025, saldo awal 1 Jan 2026 → **87 baris, Jan 2026 s/d Mar 2033**, dan
akumulasi baris terakhir tepat 250jt.

Sisa umur dihitung dari **kalender**, bukan dari angka akumulasi — supaya akhir
masa manfaat tetap cocok dengan tanggal riil aset walau sistem lama memakai
metode berbeda.

**Aset yang umurnya sudah habis tapi masih bernilai buku ditolak**
(`OPENING_ASSET_LIFE_ALREADY_ENDED`), dengan pesan menyebut nama asetnya.
Diperiksa saat posting, bukan saat impor: di titik itu tanggal saldo awal sudah
pasti, dan aset juga bisa masuk lewat form manual, bukan hanya impor.

**Reopen mengembalikan aset ke draft** (`deactivateOpeningAssets()`) — reopen
membatalkan jurnal pembuka, jadi aset yang dibukukannya tidak boleh tetap aktif.
Ditolak kalau penyusutannya sudah terposting.

### Fase 7G — Batch koreksi ✅

Kalau klien melaporkan aset terlewat **setelah** setup selesai, jalan yang benar
adalah **menambah**, bukan mengubah: batch baru bertipe `correction`. Reopen
bersifat destruktif (membatalkan jurnal pembuka) dan diblokir sistem begitu ada
transaksi operasional.

`OpeningBalanceType::CORRECTION` sudah ada di kode sejak awal tapi tidak pernah
dipakai. Tiga penjaga "hanya satu batch" dilonggarkan khusus untuknya
(`create()`, `post()`, `additionalBlockingErrors()`).

Yang membuatnya aman: **cap batch pada aset**. Batch yang belum diposting
melihat aset yang belum bercap; batch yang sudah diposting melihat aset
bercap dirinya. Tanpa cap, batch koreksi akan membukukan ulang seluruh aset
batch pertama.

Batch koreksi bertanggal periode berjalan, bukan tanggal saldo awal asli — jadi
akumulasi asetnya dinyatakan per tanggal batch itu, dan jadwalnya mulai dari
situ. Selisihnya jatuh ke ekuitas sebagai koreksi periode lalu.

Form manual juga dapat centang **"Aset saldo awal"**, yang hanya muncul selama
ada batch yang masih bisa diisi (draft/reopened, atau belum ada batch sama
sekali). Tanpa batasan itu, cepat atau lambat ada yang mencentangnya untuk aset
yang baru dibeli — dan biaya aset itu tidak akan pernah masuk buku besar.

---

## Keputusan terbuka (ringkasan)

| # | Pertanyaan | Rekomendasi |
|---|---|---|
| 7A-1 | ~~15 kategori default atau 4 saja?~~ | Gugur — kategorinya sudah ditanam migration, bukan keputusan rencana ini |
| 7B-1 | Impor menggabung atau mengganti baris saldo awal? | ✅ Diterapkan: gabung; akun bentrok ditandai invalid |
| 7B-2 | `opening_date` saat committer membuat batch? | ✅ Diterapkan: awal tahun fiskal aktif, fallback hari ini |
| 7C-1 | Kapan aset awal `draft` jadi tersusutkan? | ✅ Saat batch saldo awalnya diposting — efek dari `post()`, bukan tombol terpisah |
| 7D-1 | System line aset tetap dipecah per kelas? | ✅ Ya, WAJIB barengan 7F — tanpa itu akumulasi satu aset terbelah antara akun pembuka (generik) dan akun penyusutan bulanan (per kelas) |

---

## Sudah dikerjakan di luar fase ini

**Menu "Saldo Awal" permanen** — `moduleConfig.ts` menandai item ribbon Saldo
Awal `setupOnly: true`, sehingga `RibbonPanel` menyembunyikannya begitu
`initial_setup_available` jadi `false` — yaitu tepat setelah wizard selesai.
Digabung dengan checkbox "akan diisi nanti" di Step 5, hasilnya user diberi janji
yang tidak bisa ditepati: rutenya hidup, tapi tidak terjangkau menu mana pun.

Flag `setupOnly` dihapus dari item itu. Karena itu satu-satunya pemakainya,
mekanismenya (field di `RibbonItem` + cabang filter + `useSetupGate` di
`RibbonPanel`) ikut dihapus daripada ditinggal sebagai kode mati.
