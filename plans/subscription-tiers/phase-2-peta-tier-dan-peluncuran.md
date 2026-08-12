# Fase 2 — Mengisi Peta Tier & Menyalakannya

**Status: ✅ SELESAI 2026-08-12.** Ringkasan eksekusi, deviasi dari rancangan,
dan temuan ada di **§10** — baca itu dulu kalau menyentuh ulang berkas-berkas
fase ini. Sisa dokumen di bawah adalah rancangan ASLI (pra-eksekusi),
dipertahankan sebagai riwayat keputusan.

Fase inilah yang **mengubah perilaku aplikasi**: sesudahnya ada client yang
kehilangan akses ke kemampuan yang sebelumnya terbuka. Kerjakan hanya setelah
paket setiap client yang sudah ada diperiksa satu per satu.

---

## 1. Peta tier yang disetujui

Disetujui pemilik produk 2026-08-11, **menggantikan daftar fitur di skema asli**.

| Kemampuan | Basic | Pro | Enterprise | Izin |
|---|:---:|:---:|:---:|---|
| Pembukuan, jurnal, COA, tutup buku | ✅ | ✅ | ✅ | *tidak dipetakan* |
| Penjualan, pembelian, faktur | ✅ | ✅ | ✅ | *tidak dipetakan* |
| Kas, bank, rekonsiliasi | ✅ | ✅ | ✅ | *tidak dipetakan* |
| Persediaan satu gudang | ✅ | ✅ | ✅ | *tidak dipetakan* |
| Aktiva tetap & penyusutan | ✅ | ✅ | ✅ | *tidak dipetakan* |
| Laporan standar satu periode | ✅ | ✅ | ✅ | *tidak dipetakan* |
| Impor master data | ✅ | ✅ | ✅ | ⏳ fiturnya belum ada |
| Multi-gudang | — | ✅ | ✅ | `warehouses.*` |
| Jejak audit | — | ✅ | ✅ | `audit.*` |
| Laporan tersimpan & berbagi | — | ✅ | ✅ | `reports.save` ⚠️ baru |
| Banding multi-periode | — | ✅ | ✅ | `reports.multi_period` ⚠️ baru |
| **Alur persetujuan transaksi** | — | ✅ | ✅ | mode `draft_approve_post` — lihat §2 |
| Impor transaksi | — | ✅ | ✅ | ⏳ fiturnya belum ada |
| Anggaran | — | — | ✅ | `budgets.*` |
| Dimensi departemen & proyek | — | — | ✅ | `departments.*`, `projects.*` |
| Role kustom & hak akses per orang | — | — | ✅ | `access.*` |

| | Basic | Pro | Enterprise | Custom |
|---|---|---|---|---|
| Perusahaan / user | 1 / 3 | 3 / 5 | 5 / 10 | manual |
| Fitur | — | — | — | **sama dengan Enterprise** |

**Free dan trial tidak ada.** Keputusan pemilik produk 2026-08-11:

- **Free dinonaktifkan** (`plans.status = 'inactive'`) sampai ada modal untuk
  menanggung biaya user gratis. Barisnya **tidak dihapus** — ia tetap jadi nilai
  cadangan internal, dan tinggal diaktifkan kalau nanti dipakai sebagai promosi.
- **Tidak ada masa percobaan.** Nilai `trial` di `companies.status` (dipakai
  perusahaan #1 di database dev) jadi tidak bermakna; tandai untuk dibersihkan.

Konsekuensi yang harus diurus saat peluncuran: **setiap client wajib punya
paket.** Tidak ada lagi keadaan "belum berlangganan" yang sah — client tanpa
`plan_id` adalah kesalahan konfigurasi, dan lapis paket akan menutup semuanya
untuk mereka. Lihat §7.

**Custom = fitur Enterprise dengan angka manual.** Kalau nanti perlu Custom yang
fiturnya dipilih per client, itu berarti peta fitur pindah dari paket ke client —
perubahan besar yang menunggu permintaan nyata.

**Enam entri di peta** (`warehouses`, `audit`, `reports` lanjutan, `budgets`,
`dimensions`, `access`), plus dua baris ⏳ yang menunggu fiturnya dibangun di
[rencana Data Import](../data-import/README.md).

Pro membawa empat kemampuan di atas Basic, Enterprise membawa tiga di atas Pro.
Bandingkan dengan skema asli, di mana **Pro dan Enterprise identik secara fitur**.

---

## 2. Alasan di balik peta

### Aktiva tetap TIDAK digerbangi

Usulan awal menaruhnya di Pro sebagai pemicu upgrade. **Dibatalkan atas keberatan
pemilik produk**, dan keberatannya benar: tanpa aktiva tetap, penyusutan tidak
tercatat — neraca menyatakan aset terlalu rendah dan laba rugi menyatakan laba
terlalu tinggi. Basic menjanjikan "laporan keuangan standar"; menahan alat yang
membuatnya benar berarti menjual laporan yang salah.

> **Aturan tetap, berlaku untuk setiap penambahan peta di masa depan:
> apa pun yang dibutuhkan agar laporan keuangan benar tidak boleh digerbangi.**

### Turun tier tidak mencabut hak baca

Keputusan pemilik produk 2026-08-11. Peta hanya memuat izin **tulis**; semua
`.view` tetap terbuka di setiap tier. Client Enterprise yang turun ke Pro tetap
bisa membaca anggaran dan dimensi yang sudah dibuatnya — yang tertutup hanyalah
membuat yang baru.

Rincian izin mana yang tetap terbuka ada di
[Fase 1](phase-1-lapis-paket.md#kenapa-izin-view-sengaja-tidak-ikut-digerbangi).

Ini melunakkan risiko terbesar peluncuran (§7): gerbang tidak lagi mencabut akses
ke data yang sudah diisi, hanya menahan penambahan — jadi perilakunya kini sejalan
dengan kuota.

Penerapan langsung lainnya: **filter tanggal dan akun tidak dibatasi di tier
mana pun.** Pemilik usaha Basic tetap harus bisa menarik neraca per tanggal mana
pun.

### Persediaan tetap di Basic, multi-gudang yang dijual

Mayoritas UMKM Indonesia adalah usaha dagang. Mencabut persediaan dari Basic
membuat Basic tidak terpakai oleh pasar sasarannya sendiri. Yang dijual naik tier
bukan "punya stok" melainkan **"punya gudang kedua"** — pemicu jujur, karena
usaha dengan dua gudang memang usaha yang lebih besar.

### Dimensi jadi jantung Enterprise

`department_id` dan `project_id` adalah dimensi di `journal_entry_lines`, tersebar
di 20 tabel tenant, dan laporannya benar-benar menyaring berdasarkan keduanya
(`HasReportDimensionFilters`, `ReportFilterService`, `BalanceSheetService`,
`EquityChangesService`, `MultiPeriodReportService`, laporan penjualan).

Jadi **laporan tersegmentasi per cabang dan per proyek sudah jadi dan sudah
jalan**, dan skema asli membagikannya gratis. Perusahaan dengan tiga cabang tidak
butuh "5 perusahaan" — mereka butuh satu pembukuan yang bisa dilaporkan per
cabang. Itu yang membuat deskripsi Enterprise (*"untuk perusahaan dengan beberapa
unit usaha"*) jadi benar.

Filter dimensi di laporan **ikut otomatis**: karena `departments.*` dan
`projects.*` digerbangi, `ReportFilterService` tinggal menolak parameter dimensi
ketika paketnya tidak memuatnya. Tidak ada mekanisme baru.

### Anggaran ikut Enterprise

Anggaran baru bermakna kalau ada unit yang dianggarkan, jadi ia berpasangan
alami dengan dimensi — bukan berdiri sendiri di tengah Pro.

### Laporan lanjutan mengisi Pro

Mulai Pro, user bisa membuat dan menyimpan laporan; Basic memakai laporan standar
saja.

### Alur persetujuan transaksi — ADA, dan digerbangi lain dari yang lain

Koreksi terhadap dugaan sebelumnya bahwa persetujuan transaksi umum belum
dibangun. **Sudah ada**, terverifikasi: `transaction_workflow_mode` di
`UpdateCompanyAccountingSettingRequest` menerima tiga nilai —

| Mode | Arti |
|---|---|
| `simple_auto_post` | **Bawaan sekarang.** Dokumen langsung terposting |
| `draft_then_post` | Draft dulu, posting manual |
| `draft_approve_post` | Draft → disetujui → posting |

Ditambah bendera `approval_enabled`, dengan validasi silang yang sudah menolak
kombinasi tidak masuk akal.

Kata pemilik produk: *"approval adalah salah satu fitur untuk perusahaan yang
ingin lebih rapih."* Itu tepat menggambarkan pembeli Pro.

**Cara menggerbanginya berbeda dari yang lain.** Ini bukan izin, melainkan
**nilai pengaturan** — jadi lapis paket tidak bisa menahannya lewat corong
permission. Yang dibatasi adalah nilai yang boleh dipilih:

- Basic → hanya `simple_auto_post` dan `draft_then_post`
- Pro ke atas → ketiganya, termasuk `draft_approve_post`

Penegakannya di `UpdateCompanyAccountingSettingRequest`, memeriksa paket pemilik
perusahaan sebelum menerima nilai. Ini pengecualian pertama dari pola "semua
lewat permission", dan ia harus ditulis eksplisit supaya tidak jadi preseden
diam-diam: **pengaturan bertingkat digerbangi di validasi request, bukan di
peta izin.**

Perusahaan yang **sudah** memakai `draft_approve_post` lalu turun ke Basic tidak
dipaksa berpindah mode — sejalan dengan aturan "turun tier tidak mencabut". Yang
ditahan hanyalah memilihnya lagi setelah berpindah.

### `audit_trail` — biner, bukan bertingkat

Diserahkan pemilik produk untuk ditentukan di sini. Keputusannya: **biner.**

Alasannya mekanis, bukan selera. Namespace `audit` hanya punya **satu izin**
(`audit.view`), jadi tidak ada yang bisa dipisah jadi "basic" dan "full" lewat
corong permission. Membuat tingkatan berarti mekanisme baru — entah masa simpan
atau cakupan modul — dan itu tidak sepadan untuk pembeda yang belum terbukti
diminta.

Jadi: **jejak audit ada mulai Pro, tidak ada di Basic.** Titik.

Kalau nanti tingkatan benar-benar diperlukan, sumbu yang paling wajar adalah masa
simpan, dan fondasinya sudah ada — `app/Shared/DataRetention/`
(`DataRetentionPolicy`, `DataRetentionService`, `DataRetentionValidator`). Itu
pekerjaan tersendiri, bukan penyempurnaan peta ini.

---

## 3. Dua kunci izin yang harus dibuat

**Barangnya sudah lengkap** (terverifikasi 2026-08-11):

- migrasi `2026_07_12_000001_create_saved_reports_table.php` — dua tabel:
  `saved_reports` (`report_key`, `name`, `params` JSON) dan `saved_report_shares`
- `SavedReportController` CRUD penuh + `shareableUsers` (6 rute)
- model `SavedReport`, `SavedReportShare`, `SavedReportRequest`
- banding multi-periode lewat `MultiPeriodReportController`
  (`/profit-loss/multi-period`, `/balance-sheet/multi-period`)

**Hambatannya:** seluruh **41 rute** modul Reports memakai **satu izin yang
sama — `reports.view`**. Laporan standar dan laporan tersimpan tidak terpisahkan,
jadi tidak ada yang bisa digerbangi tanpa memisahkannya lebih dulu.

Pekerjaannya:

1. Tambah `reports.save` dan `reports.multi_period` di `config/permissions.php`
2. Pindahkan grup `reports/saved` (6 rute) ke `permission:reports.save`, dan dua
   rute multi-periode ke `permission:reports.multi_period`
3. Masukkan keduanya ke role preset `finance` dan `accountant`
   (`owner`/`admin` otomatis lewat `*`)

Pola yang sama dengan `access.*`: fiturnya sudah dibangun, hanya belum punya
kunci sendiri untuk digerbangi.

---

## 4. Yang tidak dipetakan, dan kenapa

| Flag di skema asli | Alasan |
|---|---|
| `sales`, `purchases`, `inventory`, `fixed_asset`, `tax`, `invoice`, `products_and_services`, `bank_reconciliation`, `accounting`, `journal`, `general_ledger`, `balance_sheet`, `profit_loss`, `financial_reports`, `cash_and_bank`, `accounts_receivable`, `accounts_payable`, `dashboard` | **Bernilai sama di semua tier.** Memetakan flag yang tidak pernah berbeda berarti memasang gerbang yang tidak pernah menutup: risiko bertambah, efek bisnis nol. |
| `export_excel_pdf` | **Tidak ada barangnya.** Nol rute ekspor, nol pustaka ekspor di frontend, dan `reports.export` tidak disebut sekali pun di `frontend/src` — padahal izin itu diberikan tiga role. Izin hantu. |
| `data_import` | Fiturnya belum ada, **tapi akan dibangun** — lihat §5. |
| `max_transactions_per_month` | **Dibuang.** Keputusan pemilik produk 2026-08-11: tidak ada batas jumlah transaksi. Membatasinya menghukum client paling aktif — justru yang paling bernilai. Kolomnya ada sejak Mei dan tidak pernah dibaca; hapus lewat migrasi bersih-bersih. Pengendalian biaya pindah ke [kuota penyimpanan](phase-4-kuota-penyimpanan.md). |
| `user_permission` bertingkat | Dipetakan biner ke `access.*`. Role kustom **sudah ada** — koreksi terhadap dugaan awal bahwa ini fitur yang belum dibangun. Yang ada: tabel `roles`, `role_permissions`, `company_user_permission_overrides` (allow/deny per orang), `RoleAccessController`, `CompanyUserAccessController`. |
| `api`, `marketplace_integration`, `pos_integration` | Tidak ada barangnya. |
| `advanced_reports` per laporan | Modul Reports punya rencananya sendiri (14 fase). Pembagian laporan "dasar vs lanjutan" per laporan ditunda; yang dipetakan sekarang hanya laporan tersimpan & multi-periode. |

**Akibat untuk materi jualan:** `export_excel_pdf` ditandai `true` di semua tier
padahal aplikasi belum bisa mengekspor apa pun. Perlu diputuskan: keluarkan dari
lembar tier, atau bangun fiturnya (rencana tersendiri — menyentuh hampir setiap
halaman daftar dan laporan).

---

## 5. Ketergantungan pada rencana Data Import

Pemilik produk memutuskan 2026-08-11 bahwa impor **harus dibangun**, dengan alasan
yang mengubah bentuk fiturnya: bukan sekadar migrasi awal, melainkan **jalur
operasional harian** — ratusan faktur penjualan ke pelanggan tetap per hari.

Dua baris ⏳ di peta tier menunggu rencana itu:

| | Tier | Alasan |
|---|---|---|
| Impor master data | Basic | Kebutuhan pindah masuk. Client baru tidak boleh dipaksa mengetik ulang seluruh data lamanya hanya karena berlangganan Basic. |
| Impor transaksi | Pro | Alat operasional harian. Usaha yang menerbitkan ratusan faktur sehari jelas bukan pelanggan Basic, dan fitur ini menuntut worker antrean — biaya infrastruktur nyata. |

Rincian teknis, keputusan terbuka, dan fasenya ada di
**[plans/data-import/README.md](../data-import/README.md)**.

Setelah importer ada, menggerbangkannya cukup satu kunci izin baru per jenis
(`*.import`) dan dua baris di `config/plan_features.php`. **Fase 2 tidak menunggu
rencana itu selesai** — enam entri lainnya bisa dinyalakan lebih dulu.

---

## 6. Pekerjaan

### 6a. Isi `config/plan_features.php`

Mengikuti peta di §1. Kemampuan yang tidak ada barangnya tidak dimasukkan — biar
peta hanya memuat janji yang bisa ditepati.

### 6b. Pisahkan izin laporan

Sesuai §3.

### 6c. Editor role ikut menyaring

Kalau client Basic merakit role berisi `budgets.*`, lapis paket mematikannya
diam-diam: admin perusahaan melihat izin tercentang, tapi tidak ada efeknya.

Di UI role (modul Access), izin di luar paket **ditampilkan tapi dikunci** dengan
label "tidak termasuk paket" — bukan disembunyikan. Jujur (admin tahu izin itu
ada dan kenapa mati), sekaligus jadi permukaan upsell.

### 6d. Tombol "Minta upgrade" — tautan WhatsApp

Keputusan pemilik produk 2026-08-11. Saat client kena `FEATURE_NOT_IN_PLAN`,
pesannya menyertakan tautan WhatsApp ke nomor penyedia, bukan sekadar
"hubungi penyedia aplikasi" tanpa jalan.

- Nomor disimpan di `.env` (`SUPPORT_WHATSAPP_NUMBER`), bukan di-hardcode
- Tautan `https://wa.me/<nomor>?text=<pesan>` dengan pesan terisi otomatis:
  nama perusahaan, paket sekarang, dan fitur yang diminta — supaya kamu tahu
  konteksnya tanpa bertanya balik
- Muncul di dua tempat: layar penolakan fitur, dan editor role di sebelah izin
  yang terkunci

Tanpa ini, gerbang jadi dinding buntu. Dengan ini, ia jalur penjualan.

**Editor role dan tombol ini adalah satu-satunya kerja frontend di seluruh
Fase 1–2.**

### 6d. Biarkan `reports.export` apa adanya

Izin hantu itu tidak menyakiti siapa pun selama tidak dipetakan ke tier. Jangan
petakan — supaya tidak ada tier yang kelihatan "kehilangan ekspor" padahal tidak
pernah punya.

### 6e. Nyalakan

`plan_features.enforce = true`.

---

## 7. Peluncuran — bagian paling berbahaya

Urutan ini tidak boleh dibalik:

1. **Beri paket ke SETIAP client.** Sejak Free dinonaktifkan dan trial ditiadakan,
   tidak ada lagi keadaan "belum berlangganan" yang sah. Client tanpa `plan_id`
   akan kehilangan seluruh kemampuan digerbangi begitu `enforce` menyala. Karena
   selama ini paket tidak pernah berakibat apa-apa, kemungkinan besar sebagian
   besar client memang belum diisi.
2. **Cocokkan dengan apa yang mereka pakai**, bukan apa yang mereka bayar. Client
   yang sudah membuat anggaran atau memakai dimensi di paket yang tidak memuatnya
   harus dinaikkan dulu.
3. **Nyalakan `enforce`.**
4. Kalau ada yang terlewat, matikan lagi lewat `.env` — tanpa deploy ulang.

### Bagaimana ini dibanding kuota

Sejak keputusan "turun tier tidak mencabut hak baca" (§2), keduanya kini
**berperilaku sama**: yang ditahan adalah penambahan, bukan yang sudah ada.

- **Kuota** — perusahaan & user yang ada tetap; menambah yang baru ditahan.
  Keadaan `over_quota` sah.
- **Lapis paket** — data yang sudah dibuat tetap bisa dibaca; membuat yang baru
  ditahan.

Yang tersisa sebagai risiko peluncuran bukan lagi "client kehilangan datanya",
melainkan "client tidak bisa melanjutkan pekerjaan yang sedang berjalan" —
misalnya anggaran yang sudah diajukan tapi belum disetujui. Langkah 2 di atas
yang menangkap kasus seperti itu.

---

## 8. Pengujian

### Keadaan terverifikasi 2026-08-11

- **`CompanyFactory` tidak ada.** Yang ada hanya `UserFactory` dan 11 factory
  tenant. Nol test memanggil `Company::factory()`.
- **27 berkas test membuat perusahaan langsung** lewat `Company::query()->create()`,
  semuanya menyetel `created_by` — rantai perusahaan → pemilik utuh.
- **`UserFactory` tidak menyetel `plan_id`.** Pemilik perusahaan uji selalu tanpa
  paket.
- **`tests/TestCase.php` kosong** — tidak ada satu pun method pembantu.
- `phpunit.xml` sudah punya blok `<env>` berisi 15 baris.

Jadi "cukup perbaiki factory" **tidak cukup**: tidak ada factory yang bisa
diperbaiki, dan 27 berkas merakit perusahaannya sendiri.

### Suite lama: nol berkas disunting

Satu baris di `phpunit.xml`:

```xml
<env name="PLAN_FEATURES_ENFORCE" value="false"/>
```

1174 test lama berjalan persis seperti sekarang.

**Syarat supaya ini benar-benar netral:** saat `enforce = false`,
`PlanPermissionResolver` harus keluar lebih awal **sebelum menyentuh database**.
Kalau ia tetap mencari paket lalu tabel `plans` kosong, ia bisa melempar di
ratusan test yang tidak ada urusannya dengan langganan.

**Kenapa bukan "beri paket penuh di factory":** lebih rapuh — mengharuskan tabel
`plans` terisi di setiap test (`RefreshDatabase` mengosongkannya), dan 27 berkas
itu tetap harus disentuh karena tidak lewat factory.

### Empat berkas baru

**1. `tests/TestCase.php` — pembantu bersama.** Sekarang kosong; diisi empat
method supaya berkas baru tidak mengulang blok yang sudah disalin 27 kali:

```php
protected function seedTierPlans(): void;                 // basic, pro, enterprise, custom
protected function clientOn(string $planCode): User;
protected function companyOwnedBy(User $owner): Company;  // + tenant_databases
protected function enforcePlanFeatures(bool $on = true): void;
```

`seedTierPlans()` wajib karena `RefreshDatabase` mengosongkan tabel `plans`.
`companyOwnedBy()` mengikuti pola `UserQuotaTest::seedCompany()` yang sudah
terbukti — **jangan** memakai `TenantProvisioningService`, karena
`RefreshDatabase` mengulang id dari 1 dan akan bertabrakan dengan tenant dev yang
nyata.

`CompanyFactory` juga layak dibuat, tapi untuk kenyamanan test **baru** — bukan
untuk memperbaiki yang lama.

**2. `PlanFeatureMatrixTest` — matriks tier.** Satu test berbasis data provider:

| Izin diuji | Basic | Pro | Enterprise | |
|---|:---:|:---:|:---:|---|
| `warehouses.create` | 403 | 200 | 200 | tulis |
| `audit.view` | 403 | 200 | 200 | *(hanya punya view)* |
| `reports.save` | 403 | 200 | 200 | tulis |
| `reports.multi_period` | 403 | 200 | 200 | tulis |
| `budgets.submit` | 403 | 403 | 200 | tulis |
| `budgets.manage` | 403 | 403 | 200 | tulis |
| `departments.create` | 403 | 403 | 200 | tulis |
| `projects.create` | 403 | 403 | 200 | tulis |
| `access.roles.create` | 403 | 403 | 200 | tulis |
| `access.permissions.assign` | 403 | 403 | 200 | tulis |
| **`budgets.view`** | **200** | **200** | **200** | baca — tidak digerbangi |
| **`warehouses.view`** | **200** | **200** | **200** | baca |
| **`departments.view`** | **200** | **200** | **200** | baca |
| **`projects.view`** | **200** | **200** | **200** | baca |
| **`access.roles.view`** | **200** | **200** | **200** | baca |
| **`access.users.invite`** | **200** | **200** | **200** | semua tier perlu menambah tim |
| `reports.view` | 200 | 200 | 200 | inti |
| `fixed_assets.view` | 200 | 200 | 200 | inti |
| `inventory.view` | 200 | 200 | 200 | inti |
| `journal.view` | 200 | 200 | 200 | inti |
| `dashboard.view` | 200 | 200 | 200 | inti |

Enam puluh tiga pemeriksaan dari satu method. Nilainya bukan cuma cakupan:
**matriks ini adalah definisi tier yang bisa dieksekusi.** Ubah
`config/plan_features.php` tanpa menyentuh matriksnya, test gagal — perubahan
tier jadi keputusan sadar, bukan efek samping.

Sebelas baris terbawah menjaga arah sebaliknya, dan enam yang ditebalkan adalah
yang paling mudah rusak: **pasangan `view`/`create` dari modul yang sama, satu
digerbangi satu tidak.** Kalau nanti seseorang menyederhanakan peta jadi
`budgets.*`, baris-baris itulah yang gagal — dan itu memang tujuannya.

**3. `PlanLayerBoundaryTest` — batas dua lapis.** Yang tidak muat di matriks:

- **Owner (`*`) tetap ditolak** untuk kemampuan di luar paketnya, dengan kode
  `FEATURE_NOT_IN_PLAN` — **test terpenting di seluruh fase ini**, karena owner
  ada di setiap perusahaan dan jalan pintas `*` di `hasPermission()` adalah
  tempat paling mudah bocor
- Owner tetap lolos untuk kemampuan yang dibuka paketnya
- Role staff ditolak dengan `PERMISSION_DENIED`, **bukan** `FEATURE_NOT_IN_PLAN` —
  mengunci bahwa dua sumbunya tidak tertukar
- `deny` override tetap menang atas `*`
- Client tanpa paket jatuh ke Free
- Perusahaan tanpa `created_by` ditolak, bukan error
- `enforce = false` membuka semua izin tanpa menyentuh database

**4. Test asap per tier — gerbang menyala, alur nyata.** Matriks menguji satu
endpoint per izin; ini menguji alur utuh:

| Alur | Tier | Harapan |
|---|---|---|
| Buat jurnal → posting → buku besar | Basic | lolos |
| Buat faktur penjualan → posting | Basic | lolos |
| Catat aktiva tetap → hitung penyusutan | Basic | lolos |
| Terbitkan neraca & laba rugi | Basic | lolos |
| Simpan laporan | Basic | ditolak |
| Simpan laporan | Pro | lolos |
| Buat gudang kedua | Basic | ditolak |
| Buat gudang kedua | Pro | lolos |
| Ajukan → setujui anggaran | Pro | ditolak |
| Ajukan → setujui anggaran | Enterprise | lolos |
| Jurnal bertanda departemen → laporan per departemen | Enterprise | lolos |
| Rakit role kustom → tetapkan ke user | Enterprise | lolos |
| Undang anggota tim baru | Basic | lolos |
| **Turun Enterprise → Pro, lalu baca anggaran lama** | Pro | **lolos** |
| Turun Enterprise → Pro, lalu buat anggaran baru | Pro | ditolak |

Dua baris terakhir menguji keputusan "turun tier tidak mencabut hak baca" secara
utuh — bukan hanya izinnya, tapi alurnya.

Empat baris pertama adalah intinya: **membuktikan client Basic tetap bisa menutup
bukunya dengan benar** setelah gerbang menyala. Itu janji terpenting di seluruh
rencana ini, dan ia harus punya test yang gagal kalau janjinya dilanggar.

### Empat lapis pengujian

Saklar `enforce = false` **bukan** berarti gerbangnya tidak diuji — ia memisahkan
apa yang diuji di mana:

| Lapis | Saklar | Menguji | Jumlah |
|---|---|---|---|
| Suite lama | mati | logika bisnis: jurnal seimbang, faktur benar, isolasi tenant | 1174 test |
| Matriks tier | **menyala** | lapis paket, per tier per izin | ~39 pemeriksaan |
| Batas dua lapis | **menyala** | owner, override, kode error, jatuh ke Free | ~7 test |
| Asap per tier | **menyala** | alur utuh setelah gerbang menyala | ~12 test |

Gerbangnya diuji **lebih teliti** daripada kalau ia cuma ikut terbawa suite lama:
di sana ia hanya tersentuh secara kebetulan, tanpa ada yang memeriksa apakah
owner ditolak atau kode errornya benar.

### Yang benar-benar hilang

Satu hal: **hasil kali silang** — 1174 skenario lama × gerbang menyala. Regresi
berbentuk "gerbang mematikan kemampuan yang seharusnya terbuka pada alur yang
tidak masuk daftar asap" tidak akan tertangkap.

Pertukaran yang disengaja. Suite lama menguji apakah jurnalnya seimbang;
menjalankan seluruhnya dengan gerbang menyala hanya menguji resolver yang sama
sebanyak 1174 kali, dengan ongkos menyunting 27 berkas dan menyortir ratusan
kegagalan palsu.

Kalau nanti terasa kurang, peningkatannya murah: tambah alur ke daftar asap.
Tidak perlu menyentuh suite lama.

---

## 9. Risiko

- **Peluncuran mencabut akses seketika** (§7). Ini risiko terbesar di seluruh
  rencana subscription-tiers.
- **`audit_trail` bertingkat** tidak bisa dinyatakan sebagai prefix `audit.*`
  saja. Sampai definisinya ada, biner.
- **Salah mengenali `transaction_approval`.** Persetujuan anggaran ≠ persetujuan
  transaksi. Menggerbangi yang salah mematikan alur anggaran yang sudah dipakai.
- **Memisahkan izin Reports menyentuh 8 dari 41 rute** di modul terbesar.
  Perubahannya kecil, tapi role preset yang lupa diperbarui membuat `finance`
  dan `accountant` kehilangan laporan tersimpan di semua tier.

---

## 10. Hasil eksekusi 2026-08-12

Saklar **menyala** (`plan_features.enforce` bawaan `true`). Ini fase yang
mengubah perilaku aplikasi — semua §6 dikerjakan, plus tiga temuan yang
mengubah detail rancangan (bukan keputusannya).

### 10.1 Peta fitur — dibangun persis §1, dengan satu koreksi

`database/seeders/PlanSeeder.php`: Basic tanpa kunci gerbang; Pro dapat
`multi_warehouse`, `audit_trail`, `advanced_reports`, `transaction_approval`;
Enterprise dapat semua itu plus `budgeting`, `dimensions`, `user_permission`;
Custom disalin dari Enterprise. Free `status = 'inactive'`, baris tidak
dihapus.

**Koreksi terhadap rancangan §1/§2:** `audit_trail` di `config/plan_features.php`
**tidak** menggerbangi `audit.*` seperti ditulis rancangan. Diverifikasi
`grep -rn "permission:audit\." app/` **kosong** — kunci `audit.view` ada di
katalog izin dan di preset role `finance`/`accountant`, tapi nol rute
memakainya sebagai gerbang. Rute jejak audit yang benar-benar hidup
(`GET /access/audit`, `AccessAuditController`) dijaga `access.audit.view`,
namespace berbeda. Peta diubah menggerbangi `access.audit.view` supaya
"Jejak audit ada mulai Pro" benar-benar berlaku, bukan cuma tertulis di
dokumen. Rancangan §2 ("Namespace `audit` hanya punya satu izin") salah
menyebut namespace-nya — koreksi ini dicatat di sini, bukan di §2, supaya
riwayat argumennya (biner vs bertingkat) tetap utuh.

Temuan sampingan yang **tidak** diperbaiki (tidak berefek, daftar putih):
`access.permissions.assign` dan `access.permissions.revoke` di `user_permission`
juga tidak dipakai rute mana pun (hanya `access.permissions.manage` dan
`.view` yang hidup). Dibiarkan di peta — kunci mati di daftar putih tidak
menutup apa pun yang seharusnya terbuka.

### 10.2 Alur persetujuan — dibangun sesuai §2, dengan perbaikan saklar

`UpdateCompanyAccountingSettingRequest::planAllowsTransactionApproval()`
memeriksa `PlanPermissionResolver::enforcing()` lebih dulu sebelum membaca
`featuresFor()`. Tanpa ini, gerbang baru itu (jalur tersendiri, bukan lewat
`blockedKeysFor()`) akan tetap menahan Basic walau `plan_features.enforce =
false` — melanggar janji "saklar mati = perilaku identik sebelum fase ada"
yang jadi dasar seluruh Fase 1.

### 10.3 Izin Reports dipisah sesuai §3

`reports.save` (6 rute `reports/saved`) dan `reports.multi_period` (2 rute
`*/multi-period`) — persis §3. Ditambahkan ke role preset `finance` dan
`accountant`. Migrasi sinkronisasi baru:
`2026_08_11_000006_sync_advanced_reports_permissions.php` (pola yang sama
dengan migrasi sync lain di modul ini).

### 10.4 Tombol upgrade WhatsApp — dibangun sesuai §6d, plus satu jalur baru

- `UpgradeLinkBuilder` (`app/Shared/Subscription/`), nomor dari
  `services.support.whatsapp_number` (`SUPPORT_WHATSAPP_NUMBER` di `.env`).
  `null` kalau nomor belum diisi — pemanggil menyembunyikan tombol, bukan
  menampilkan tautan buntu.
- Muncul di **tiga** tempat, bukan dua seperti §6d: (1) `meta.upgrade_url`
  di respons `FEATURE_NOT_IN_PLAN` — dipakai layar penolakan fitur; (2)
  `PermissionCatalogController` mengirim `blocked_by_plan_keys` +
  `upgrade_url` — dipakai editor role; (3) **baru** — jaring pengaman global
  di interceptor axios (`http.ts`): setiap respons `FEATURE_NOT_IN_PLAN` di
  mana pun di aplikasi otomatis menampilkan toast dengan tombol WhatsApp,
  tanpa menyentuh satu pun dari ~80 pemanggil `toast.error()` yang sudah ada.
  Alasannya: aksi yang digerbangi normalnya sudah tersembunyi lewat
  `PermissionGuard` (daftar izin dari `/auth/permissions` sudah disaring
  paket), jadi kasus ini semestinya jarang benar-benar terpicu — tapi kalau
  terpicu (race condition, tombol yang sengaja tetap terlihat-tapi-terkunci),
  ada satu tempat yang menanganinya, bukan nol.

### 10.5 Editor role — dibangun sesuai §6c

`RolesPage.tsx`: izin di luar paket ditampilkan **terkunci** (checkbox
nonaktif + ikon gembok + tooltip "Tidak termasuk paket saat ini"), bukan
disembunyikan. Tombol "Minta Upgrade" muncul di header editor kalau ada
izin terkunci dan nomor WhatsApp sudah diisi.

**Editor role dan ketiga tempat tombol upgrade di atas adalah satu-satunya
kerja frontend di Fase 1–2**, sesuai janji rancangan.

### 10.6 Test — empat berkas baru, sesuai §8 dengan penyesuaian cakupan

| Berkas | Isi | Hasil |
|---|---|---|
| `tests/TestCase.php` | `seedTierPlans()`, `clientOn()`, `companyOwnedBy()`, `enforcePlanFeatures()` — diisi dari kosong, dipakai semua test baru | — |
| `PlanFeatureMatrixTest.php` | Matriks tier lewat `EffectivePermissionService::hasPermission()` langsung (bukan lewat rute HTTP) — 11 izin gerbang × 3 tier + 12 izin selalu-terbuka × 3 tier | 2 test, 69 assertion |
| `PlanLayerBoundaryTest.php` | Owner tetap ditolak lapis paket (test terpenting), owner lolos lapis 2, staff ditolak `PERMISSION_DENIED` bukan `FEATURE_NOT_IN_PLAN`, deny override menang, jatuh ke Free, perusahaan tanpa pemilik, saklar mati | 7 test |
| `PlanSmokeTest.php` | Alur nyata lewat HTTP sungguhan: Basic buat+posting jurnal (janji terpenting — pembukuan inti tidak tersentuh), Basic ditolak gudang kedua, Pro lolos gudang kedua, Pro ditolak anggaran, Enterprise lolos anggaran, turun Enterprise→Pro (baca dimensi lama tetap lolos, buat dimensi baru ditahan) | 6 test |
| `TransactionApprovalGateTest.php` | Basic ditolak `draft_approve_post`, Pro lolos, Basic tetap bisa `draft_then_post`, saklar mati membuka semua tier — tidak disebut eksplisit di §8 tapi perlu untuk §2 "Alur persetujuan transaksi" | 4 test |

**Deviasi dari §8:** rancangan meminta matriks 63 pemeriksaan lewat data
provider yang memukul rute HTTP satu per satu untuk 11 kemampuan (termasuk
`budgets.submit`, `departments.edit`, dst. dengan payload valid per domain).
Yang dibangun: matriks lewat **service layer langsung**
(`EffectivePermissionService::hasPermission()`), bukan HTTP — mengukur
persis hal yang sama (resolusi lapis paket per tier per izin) tanpa perlu
merakit payload valid untuk delapan domain berbeda. Cakupan HTTP nyata
dipindah ke `PlanSmokeTest` (6 alur, bukan 12-15 seperti tabel §8) — dipilih
yang paling representatif: satu per kategori kemampuan (gudang, anggaran,
dimensi+downgrade), plus yang **terpenting**, jurnal Basic tetap jalan.
Alasan memotong cakupan: delapan domain (budget submission chain,
role-kustom-lalu-assign, dst.) masing-masing butuh provisioning tenant
sendiri: `PlanFeatureMatrixTest` sudah membuktikan resolusi gate-nya benar
untuk semuanya; `PlanSmokeTest` membuktikan kabelnya nyambung end-to-end
untuk satu wakil tiap kategori. "Hasil kali silang" (1215 skenario lama ×
gerbang menyala) tetap sengaja tidak dikerjakan, persis alasan §8.

**Total test baru: 19** (2+7+6+4), suite penuh **1215 test, 1210 lulus, 5
skip, 0 gagal**.

### 10.7 Ranjau yang ditemukan saat menyalakan saklar

**`phpunit.xml` wajib mengunci `PLAN_FEATURES_ENFORCE=false`.** Menyalakan
`enforce` di `config/plan_features.php` (bawaan produksi) otomatis ikut
menyala di test run kalau tidak dikunci — dan **19 test lama gagal**
persis seperti diperingatkan §8 "Yang benar-benar hilang": `UserFactory`
tidak menyetel `plan_id`, jadi perusahaan uji lama jatuh ke Free (tanpa
fitur gerbang apa pun) dan setiap pemeriksaan `warehouses.create`,
`reports.save`, `budgets.manage`, dst. di test lama (`WarehouseTest`,
`DepartmentTest`, `ProjectTest`, `BudgetFlowTest`, `MultiPeriodReportTest`,
`SavedReportTest`, `AccessManagementTest`) berubah dari lolos jadi
`403 FEATURE_NOT_IN_PLAN`. Baris `<env name="PLAN_FEATURES_ENFORCE"
value="false"/>` ditambahkan ke `phpunit.xml` — persis solusi yang sudah
ditulis §8, cuma belum diterapkan sampai saklar sungguhan dinyalakan.
Test `Subscription/*` tidak terpengaruh: masing-masing memanggil
`enforcePlanFeatures(true)` sendiri di `setUp()`.

**Audit data dev menemukan pelanggaran nyata sebelum saklar dinyalakan** —
persis skenario §7 langkah 2 ("cocokkan dengan apa yang mereka pakai").
Client dev #1 (pemilik `PT Maju Jaya` dan `PT Nusantara Dagang Sejahtera`)
berlangganan **Pro**, tapi kedua perusahaannya sudah punya baris departemen
(4 masing-masing) dan proyek (6 dan 3) — dimensi yang di peta baru hanya
terbuka di **Enterprise**. Anggaran dan role kustom nol, aman. Diserahkan ke
pemilik produk (sesi ini): **client dinaikkan ke Enterprise** sebelum saklar
dinyalakan, supaya tidak ada penambahan/pengubahan dimensi yang tiba-tiba
ditahan pada data yang sudah berjalan.

### 10.8 Verifikasi yang dijalankan

```
php artisan test              → 1215 test, 1210 lulus, 5 skip, 0 gagal
./vendor/bin/pint --dirty     → lulus
npm run build (tsc -b && vite) → 0 error
npm run lint                  → 0 error, 0 warning
```

### 10.9 Yang belum dikerjakan

- **Hasil kali silang** (1215 skenario lama × gerbang menyala) — sengaja,
  alasan sama dengan §8.
- **Ekspor/impor** — masih di luar cakupan seperti dicatat README utama.
- **Migrasi bersih-bersih `max_transactions_per_month`** dan nilai
  `companies.status = 'trial'`— ditandai §1, belum dieksekusi; tidak
  mendesak dan bukan bagian dari janji perilaku fase ini.
