# Fase 3 — Siklus Langganan

**Status: ✅ SELESAI 2026-08-12.** Ringkasan eksekusi, deviasi, dan temuan ada
di **§8** — baca itu dulu kalau menyentuh ulang berkas-berkas fase ini. Sisa
dokumen di bawah adalah rancangan ASLI (pra-eksekusi), dipertahankan sebagai
riwayat keputusan.

Skema tier memuat harga bulanan dan tahunan. Begitu ada periode berbayar, ada
tanggal mulai, tanggal berakhir, dan pertanyaan "apa yang terjadi setelah lewat" —
tidak satu pun yang ada hari ini.

Fase ini **tegak lurus terhadap Fase 1–2**; ia tidak menunggu lapis paket dan
lapis paket tidak menunggunya.

---

## 1. Keadaan terverifikasi 2026-08-11

- Paket menempel di **client**: `users.plan_id`. Seluruh perhitungan kuota
  membacanya.
- Tabel `subscriptions` ada dengan kolom yang hampir tepat — `plan_id`, `status`,
  `trial_ends_at`, `starts_at`, `ends_at`, `cancelled_at`, `billing_cycle`,
  `price`, `metadata` — **tapi kuncinya `company_id`**, bukan `user_id`.
- **Tabelnya praktis mati.** Isinya dua baris, dibuat `DemoCentralSeeder`
  2026-06-09, keduanya `status=trial` / `billing_cycle=free` tanpa `ends_at`:

  ```
  company=1  plan=1  status=trial  cycle=free  mulai=2026-06-09  akhir=-
  company=2  plan=1  status=trial  cycle=free  mulai=2026-06-09  akhir=-
  ```

  Yang menyebut model `Subscription` di seluruh kode hanya **dua berkas**:
  seeder itu sendiri dan `SharedServiceProvider`. Tidak ada logika bisnis yang
  membacanya.
- Tidak ada trial, kedaluwarsa, maupun masa tenggang yang berfungsi.
- Belum ada worker antrean yang berjalan, dan **belum ada pengiriman email sama
  sekali**.

---

## 2. Keputusan

### 2a. Langganan pindah dari perusahaan ke client

Ini akar seluruh fase. Ada dua model yang bertabrakan:

```
users.plan_id            →  satu paket per CLIENT
subscriptions.company_id →  satu langganan per PERUSAHAAN
```

Client Pro dengan 3 perusahaan: model pertama bilang dia membeli **satu**
langganan yang mencakup ketiganya; model kedua bilang ada **tiga** baris yang
bisa berisi tiga paket dan tiga tanggal berakhir berbeda.

Yang berlaku adalah **model pertama** — itu sudah jadi keputusan sejak kuota
dibangun. `subscriptions` adalah peninggalan asumsi lama.

**Keputusan: `subscriptions.company_id` → `user_id`, satu baris per periode
langganan.** Perpanjangan membuat baris baru, sehingga riwayat penagihan
terbentuk sendiri — dan riwayat itu memang dibutuhkan, karena perpanjangan manual
dengan harga terkunci menuntut jawaban atas "client ini bayar berapa, untuk
periode mana".

Tabelnya efektif kosong, jadi **sekarang waktu termurah untuk mengubahnya**.

### 2b. Siklus: bulanan atau tahunan, tidak ada yang lain

*"Client hanya bisa memilih pembayaran per bulan atau per tahun."*

Enum tertutup dua nilai: `monthly` | `yearly`. Bukan jumlah hari, bukan jumlah
bulan bebas. Tidak ada kuartalan, tidak ada seumur hidup.

Perhitungan tanggal berakhir cuma punya dua cabang — dan wajib memakai varian
**no-overflow**: langganan bulanan yang mulai 31 Januari berakhir 28/29 Februari,
bukan melompat ke 3 Maret.

Harga sudah tersedia di `plans.monthly_price` / `yearly_price`.

### 2c. Tidak ada trial, tidak ada Free

Free dinonaktifkan sampai ada modal menanggung biayanya; masa percobaan tidak
pernah diadakan.

Akibatnya: **tidak ada keadaan "belum berlangganan" yang sah.** Setiap client
punya langganan berbayar sejak dibuat. Kolom `trial_ends_at` ikut dibuang, dan
nilai `trial` di `companies.status` (dipakai perusahaan #1 di dev) jadi tidak
bermakna — tandai untuk dibersihkan.

### 2d. Kedaluwarsa: kunci penuh, tenggang 7 hari, pengingat H-14

| | |
|---|---|
| Pengingat | **H-14** sebelum `ends_at` |
| Masa tenggang | **7 hari** setelah `ends_at` — akses masih penuh |
| Setelah tenggang | **Kunci penuh** — login ditolak |

Aku sempat merekomendasikan "turun ke Free" dan menyarankan kunci penuh
dihindari; pemilik produk memutuskan sebaliknya, dan keputusan itu yang berlaku.

Satu hal faktual untuk diurus dalam pelaksanaannya, bukan untuk membatalkan
keputusan: pembukuan wajib bisa diproduksi ulang untuk keperluan pajak, dan
client terkunci tidak bisa menariknya. Dua peredam yang tidak mengubah keputusan:

1. **Admin bisa membuka kunci** kapan saja — jalur pemulihan wajib.
2. **Selama 7 hari tenggang akses masih penuh**, jadi ada jendela nyata untuk
   menarik data. Ini alasan ketiga kenapa
   [ekspor](../data-import/phase-6-ekspor.md) sebaiknya sudah ada sebelum
   penguncian dinyalakan.

### 2e. Perpanjangan manual, baris baru

Manual selama belum ada gerbang pembayaran — kamu yang memperpanjang lewat area
admin setelah pembayaran diterima. Karena riwayat disimpan, memperpanjang berarti
**membuat baris baru** yang mulai di `ends_at` baris sebelumnya, bukan menggeser
tanggal baris lama.

---

## 3. Bentuk data

### Migrasi ubah `subscriptions`

Bukan drop-and-create: tabel ini mungkin sudah berisi sesuatu di lingkungan yang
tidak terlihat dari sini. Ubah bertahap.

| Langkah | Catatan |
|---|---|
| Tambah `user_id` (nullable dulu) | FK ke `users`, **`restrictOnDelete`** |
| Isi dari `companies.created_by` lewat `company_id` | Pemilik perusahaan = pemilik langganan |
| Hapus baris `billing_cycle = 'free'` atau `status = 'trial'` | Nilai yang sudah tidak ada di model bisnis. Di dev, ini menghapus tepat dua baris demo. |
| Hapus baris yang `user_id`-nya tetap kosong | Perusahaan tanpa `created_by` |
| Jadikan `user_id` non-nullable, drop `company_id` | |
| Drop `trial_ends_at` | Tidak ada trial |
| `starts_at`, `ends_at` jadi non-nullable | Setiap langganan punya periode |
| Ganti bawaan `billing_cycle` dari `'free'` → tanpa bawaan | Harus diisi eksplisit |
| Drop kolom `status` | Lihat di bawah |
| Indeks `user_id`, `ends_at` | `ends_at` dipakai command harian |

**`restrictOnDelete` pada `user_id` disengaja.** Ia sekaligus menutup risiko laten
yang ditemukan saat QA: `users` tidak memakai SoftDeletes, dan menghapus pemilik
membuat `companies.created_by` jadi NULL sehingga perusahaannya membeku di batas
cadangan. Dengan restrict, client yang punya riwayat langganan tidak bisa dihapus
begitu saja.

### Status diturunkan dari tanggal, bukan disimpan

Kolom `status` dibuang. Keadaan langganan **dihitung** dari `starts_at`,
`ends_at`, `cancelled_at`, dan tenggang 7 hari:

```
cancelled_at terisi        → dibatalkan
now < ends_at              → aktif
now < ends_at + 7 hari     → tenggang
selain itu                 → kedaluwarsa
```

Alasannya penting: kalau status disimpan dan digeser command harian, **command
yang gagal jalan semalam berarti orang terkunci atau terbuka secara keliru.**
Dengan diturunkan, gerbangnya selalu benar apa pun yang terjadi pada penjadwalan.
Command harian tinggal mengurus hal yang memang butuh dijalankan — pengingat dan
pencabutan token.

### `users.plan_id` tetap ada

Ia jawaban cepat "paket aktif sekarang", dibaca setiap request oleh lapis kuota
dan lapis paket. Menggantinya dengan join ke `subscriptions` di tiap request
adalah pemborosan.

Ia diperlakukan sebagai **turunan dengan satu penulis**: hanya
`SubscriptionService` yang boleh mengubahnya, dan selalu bersamaan dengan
membuat/mengubah baris langganan.

**Kunci penuh membuat ini aman.** Client kedaluwarsa tidak bisa login sama
sekali, jadi tidak ada request yang membawa `plan_id` basi ke lapis kuota atau
lapis paket. Keduanya boleh mempercayai `users.plan_id` tanpa memeriksa tanggal.

---

## 4. Pekerjaan

### 4a. Migrasi + model

Sesuai §3. `Subscription` model diperbarui, `DemoCentralSeeder` disesuaikan agar
tidak lagi menulis baris `trial`/`free`.

### 4b. `SubscriptionService` di `app/Shared/Subscription/`

Satu-satunya penulis `subscriptions` dan `users.plan_id`:

```php
public function subscribe(User $client, Plan $plan, string $cycle, ?Carbon $startsAt = null): Subscription;
public function renew(User $client, ?Plan $plan = null, ?string $cycle = null): Subscription;
public function cancel(User $client): void;
public function currentFor(User $client): ?Subscription;
public function stateFor(User $client): string;   // aktif | tenggang | kedaluwarsa | dibatalkan
public function daysRemaining(User $client): int;
```

`subscribe()` mengunci harga dari paket saat itu ke kolom `price`. Kenaikan harga
paket tidak boleh menyentuh langganan yang sedang berjalan.

Aturan: **hanya satu baris per client yang boleh aktif atau dalam tenggang.**
`renew()` membuat baris baru yang mulai di `ends_at` baris sebelumnya.

### 4c. Penguncian di titik login

Di `AuthController::login()`, **bukan** di `EnsureCompanyAccess`. Alasannya:
penguncian berlaku ke client bukan ke perusahaan, dan menolak di login memberi
satu tempat untuk menampilkan pesan berisi tautan WhatsApp.

Token yang sudah terbit **ikut dicabut** saat client berpindah ke kedaluwarsa —
kalau tidak, sesi yang sedang berjalan tetap hidup sampai tokennya mati sendiri.
Itu tugas command harian di 4e.

### 4d. Area admin

- Kolom tanggal berakhir + sisa hari di daftar client
- Tab Langganan: paket, siklus, periode berjalan, harga terkunci, riwayat baris
- Tombol **Perpanjang** (memilih siklus, membuat baris baru)
- Tombol **Buka kunci** — jalur pemulihan, wajib ada
- Daftar tersaring **"akan jatuh tempo 14 hari ke depan"** — ini yang kamu pakai
  untuk menghubungi client lewat WhatsApp

### 4e. Command harian

```
php artisan subscriptions:sweep [--dry-run]
```

Dua tugas, keduanya tidak memengaruhi kebenaran gerbang:

1. Mencabut token client yang baru melewati tenggang
2. Menandai siapa yang perlu dihubungi (H-14 dan selama tenggang)

Wajib `--dry-run` yang mencetak daftar tanpa mengubah apa pun, dan wajib mencatat
apa yang diubah.

### 4f. Peringatan di aplikasi client

Spanduk sejak H-14 dan selama masa tenggang, menyebut sisa hari dan tautan
WhatsApp.

**Pengingat H-14 lewat apa?** Belum ada pengiriman email sama sekali di aplikasi
ini. Kalau pengingat harus sampai ke client di luar aplikasi, itu pekerjaan
tersendiri. Jalur termurah untuk gelombang pertama: spanduk di dalam aplikasi
plus daftar "akan jatuh tempo" di area admin, lalu kamu menghubungi manual.

---

## 5. Test

- `subscribe()` menghitung `ends_at` benar untuk kedua siklus
- **31 Januari + 1 bulan = 28/29 Februari**, bukan 3 Maret
- Harga terkunci: menaikkan `plans.monthly_price` tidak mengubah langganan berjalan
- `renew()` membuat baris baru yang mulai tepat di `ends_at` sebelumnya
- Hanya satu baris aktif/tenggang per client
- Keadaan diturunkan benar di keempat batas: sehari sebelum `ends_at`, tepat di
  `ends_at`, hari ke-7 tenggang, hari ke-8
- Client kedaluwarsa **tidak bisa login**; pesannya memuat tautan WhatsApp
- Client dalam tenggang **masih bisa login penuh**
- Admin membuka kunci → client bisa login lagi
- Token dicabut saat melewati tenggang
- `--dry-run` tidak mengubah apa pun
- Client dengan riwayat langganan **tidak bisa dihapus** (`restrictOnDelete`)
- Migrasi: baris `trial`/`free` lama terhapus, `user_id` terisi dari
  `companies.created_by`

---

## 6. Risiko

- **Penguncian penuh tanpa jalur ekspor** membuat client tidak bisa menarik
  pembukuannya untuk keperluan pajak. Tombol buka kunci adalah peredamnya, dan
  ekspor sebaiknya sudah ada sebelum penguncian menyala.
- **Command harian menyentuh seluruh basis client sekaligus.** Bug di sana
  mencabut token semua orang dalam semalam. `--dry-run` dan pencatatan wajib.
  Diperingan oleh keputusan menurunkan status dari tanggal: command yang salah
  tidak membuat gerbangnya salah.
- **Migrasi menghapus baris.** Di dev hanya dua baris demo, tapi perintahnya
  harus menyaring dengan syarat eksplisit (`billing_cycle = 'free'` atau
  `status = 'trial'`), bukan mengosongkan tabel.
- **Belum ada worker antrean maupun email.** Keduanya prasyarat operasional,
  bukan kode semata.

---

## 7. Yang sudah beres dan tidak perlu diulang

Perilaku **penurunan paket** sudah benar sejak kuota dibangun: perusahaan dan
user yang ada tidak pernah dicabut, hanya penambahan berikutnya yang ditahan.
Sejak keputusan "turun tier tidak mencabut hak baca", lapis paket berperilaku
sama.

**Kedaluwarsa adalah pengecualian dari pola itu** — ia mengunci penuh, bukan
menurunkan. Jadi ia tidak memakai ulang mekanisme penurunan paket; ia mekanisme
tersendiri di titik login.

---

## 8. Hasil eksekusi 2026-08-12

Semua §4 dikerjakan. Satu keputusan desain diambil di tempat yang rancangan
tidak menyebutnya secara eksplisit — §8.1 — dan satu koreksi kecil terhadap
rute lama yang ternyata memakai konsep langganan-per-perusahaan (§8.6).

### 8.1 Keputusan yang diambil saat eksekusi: `none` ≠ `expired`

Rancangan §2c menulis "tidak ada lagi keadaan 'belum berlangganan' yang sah",
tapi tidak menjawab pertanyaan operasional: **apa status client yang tidak
pernah punya baris `subscriptions` sama sekali?** Ini bukan kasus hipotetis —
migrasi §3 membuang dua baris demo trial/free, dan `UserFactory` tidak pernah
mengisi langganan sama sekali. Kalau `stateFor()` memperlakukan "tidak ada
baris" sama dengan `expired`, akibatnya:

- **Setiap client yang ada hari ini langsung terkunci** begitu migrasi
  dijalankan — termasuk kedua client dev, dan (di lingkungan nyata) setiap
  client yang sudah berlangganan sebelum Fase 3 ada tapi belum di-backfill.
- `test_client_cannot_login_through_admin_endpoint` (test lama,
  `AdminClientManagementTest`) memakai login client sungguhan sebagai bagian
  dari setup-nya (bukan yang diuji) — akan ikut gagal.

`SubscriptionService::stateFor()` dibangun dengan kelima keadaan eksplisit
(`none`, `active`, `grace`, `expired`, `cancelled`); `isLocked()` **hanya**
`true` untuk `expired` dan `cancelled`. `none` diperlakukan sebagai "belum
di-backfill", bukan "kedaluwarsa" — analog dengan
`CompanyQuotaService::DEFAULT_PLAN_CODE = 'free'`: absennya data berarti nilai
aman, bukan penolakan agresif.

**Konsekuensi yang harus disadari sebelum peluncuran nyata:** kunci penuh
di titik login hanya benar-benar menahan siapa pun setelah admin memanggil
`subscribe()` untuk mereka. Fase ini **tidak** membangun langkah backfill
massal ("beri langganan ke SETIAP client", analog checklist Fase 2 §7) —
itu pekerjaan operasional terpisah, bukan bagian dari janji Fase 3. Sampai
backfill itu terjadi, mekanisme kedaluwarsa berlaku hanya untuk client yang
memang sudah pernah disubscribe lewat area admin.

### 8.2 Siapa yang terkunci login — batasan yang disadari, bukan gap tersembunyi

"Penguncian berlaku ke client bukan ke perusahaan" (§4c) diterapkan literal:
`SubscriptionService::isLocked($user)` dipanggil untuk user yang login,
bukan untuk "pemilik perusahaan tempat dia bekerja". Akibatnya: **staf yang
BUKAN pemilik langganan tidak pernah terkunci lewat mekanisme ini**, bahkan
kalau client (owner) yang mempekerjakannya sudah kedaluwarsa — karena staf
biasa tidak pernah punya baris `subscriptions` sendiri (state-nya selalu
`none`).

Ini bukan bug yang lolos; ini pilihan dari dua opsi yang sama-sama tidak
sempurna: mengunci staf berdasarkan status langganan owner-nya berarti
menelusuri "siapa staf ini, di perusahaan siapa, siapa pemiliknya" saat
login — padahal satu staf bisa bekerja di perusahaan milik client berbeda
sekaligus (relasinya banyak-ke-banyak lewat `company_users`), dan rancangan
tidak membahas kasus ini sama sekali. Dicatat di sini sebagai batasan
eksplisit, bukan didiamkan: **kalau nanti dibutuhkan, sumbunya paling wajar
lewat lapis paket (Fase 1) di `company.access`, bukan di titik login** —
tapi itu pekerjaan tersendiri.

### 8.3 `unlock()` — bentuknya diputuskan saat eksekusi

Rancangan menyebut "Tombol Buka kunci" tanpa merinci mekanismenya, dan itu
tidak sepele: status **diturunkan** dari tanggal (§3), jadi "membuka kunci"
tidak bisa berarti "ubah kolom status jadi aktif" — kolom itu tidak ada.

Yang dibangun: `unlock()` menggeser `ends_at` baris langganan berjalan ke
SEKARANG (dan membatalkan `cancelled_at` kalau ada), sehingga client jatuh
tepat ke keadaan `grace` dan mendapat 7 hari akses penuh — TANPA dicatat
sebagai baris riwayat penagihan baru, karena ini jalur pemulihan darurat,
bukan perpanjangan berbayar. Beda eksplisit dari "Perpanjang" (`renew()`),
yang membuat baris baru dengan harga terkunci.

### 8.4 File yang dibangun

| Berkas | Isi |
|---|---|
| `database/migrations/2026_08_12_000001_migrate_subscriptions_to_client_scope.php` | Sesuai §3, delapan langkah. SQLite butuh `dropIndex()` eksplisit untuk `company_id`/`status` sebelum `dropColumn()` — tidak dilepas otomatis seperti MySQL/Postgres. |
| `app/Shared/Models/Subscription.php` | Ditulis ulang: `user_id` bukan `company_id`, tanpa `status`/`trial_ends_at`. |
| `app/Shared/Subscription/SubscriptionService.php` | `subscribe/renew/cancel/unlock/currentFor/stateFor/isLocked/daysRemaining`. Konstanta `STATE_*` publik (dipakai controller & test). |
| `app/Console/Commands/SweepSubscriptionsCommand.php` | `subscriptions:sweep [--dry-run]`, dua tugas §4e. |
| Perluasan `ClientUserController`/`ClientUserService` (Admin) | `subscribe`, `renew`, `unlock`, `dueSoon` + payload `subscription` (state, ends_at, days_remaining, billing_cycle, price, riwayat). |
| Perluasan `AuthController` | Kunci di `login()`; `subscriptionSummary()` dipakai `login()` dan `me()` untuk spanduk. |
| Frontend: `SubscriptionCycleSection.tsx`, `SubscriptionWarningBadge.tsx`, `useSubscriptionStatus.ts` | Tab Siklus Langganan (admin), badge kompak di Topbar (client) — lihat §8.5. |

### 8.5 Spanduk peringatan — bentuknya beda dari draf §4f

§4f menyebut "spanduk sejak H-14 dan selama tenggang". Yang dibangun bukan
strip banner yang menambah tinggi shell, melainkan **badge kompak di
Topbar** (52px tetap, tidak berubah) dengan tooltip berisi detail dan tautan
WhatsApp. Alasan: menambah strip banner berarti menghitung ulang
`contentChromeTop` di `AppShell.tsx`, dan aplikasi ini punya aturan tinggi
viewport tablet yang ketat (`spec-23-tablet-first-layout-rules.md`,
tidak dibaca ulang secara penuh sesi ini) — mengubah tinggi shell tanpa
memverifikasi aturan itu berisiko melanggarnya. Badge di ruang topbar yang
sudah ada mencapai tujuan yang sama (visibilitas peringatan, tautan
perpanjang) tanpa risiko itu.

Muncul di **tiga** tempat: badge Topbar (semua halaman, client yang statusnya
`grace` atau H-14), toast global saat `SUBSCRIPTION_EXPIRED` di layar login
(memakai ulang `actionUrl` di `useToast` yang sudah dibangun Fase 2), dan tab
Siklus Langganan di admin.

**Batasan yang sama dengan §8.2 berlaku di sini**: badge hanya tampil untuk
user yang memang pemilik langganan (`subscription` dari `/auth/me` bukan
`null`). Staf tidak melihat peringatan milik client-nya.

### 8.6 Koreksi: `Company::activeSubscription()` dan `MyCompaniesController`

Ditemukan saat migrasi mengubah skema: `Company` model punya relasi
`subscriptions()`/`activeSubscription()` yang mengasumsikan langganan
per-perusahaan (query ke `status`, kolom yang baru saja dihapus). Satu
pemakai nyata: `MyCompaniesController` — ternyata **rute mati**, tidak
terdaftar di `routes/api.php` mana pun dan tidak dipanggil frontend
(`grep` kosong di keduanya), dengan `$user` di-hardcode ke
`admin@example.com`. Dihapus, beserta kedua relasi di `Company` yang jadi
tidak valid setelah migrasi. `DemoCentralSeeder` juga disesuaikan: blok yang
membuat langganan trial/free per perusahaan dibuang (konsisten dengan §2c —
tidak ada lagi trial).

### 8.7 Test

| Berkas | Isi | Jumlah |
|---|---|---|
| `SubscriptionServiceTest.php` | subscribe (kedua siklus + no-overflow 31 Jan), harga terkunci, `plan_id` client ikut berubah, tolak langganan ganda, renew (baris baru tepat di `ends_at`, ganti paket), state di empat batas, `none` vs `expired`, cancel langsung mengunci, `restrictOnDelete` | 12 |
| `SubscriptionLoginLockTest.php` | `none` tetap login, aktif login, tenggang login penuh, lewat tenggang ditolak + `renewal_url`, dibatalkan ditolak, admin unlock memulihkan, password salah tidak ketiban cek langganan, ringkasan di respons login, `me()` `null`/`grace` untuk badge | 10 |
| `SweepSubscriptionsCommandTest.php` | `--dry-run` tidak mencabut, cabut token kedaluwarsa, cabut token dibatalkan, tidak menyentuh aktif/tenggang, jalan tanpa data | 5 |
| `AdminSubscriptionManagementTest.php` | Subscribe pertama, tolak subscribe ganda, renew (+ganti paket), unlock, `due-soon` (H-14 + tenggang, bukan yang jauh), butuh platform admin | 7 |

**34 test baru.** Suite penuh: **1249 test, 1244 lulus, 5 skip, 0 gagal.**

### 8.8 Migrasi dijalankan di database dev

`php artisan migrate --path=...` dijalankan untuk kedua migrasi Fase 2/3 baru
(disengaja TIDAK menjalankan migrasi `sync_import_permissions` yang sudah
pending sebelumnya — itu pekerjaan lain, di luar cakupan sesi ini). Backup
`database.sqlite` disalin ke scratchpad sebelum migrasi. Hasil: dua baris
demo trial/free terhapus persis seperti diperkirakan §3; client dev #1
(pemilik `PT Maju Jaya`/`PT Nusantara Dagang Sejahtera`, dinaikkan ke
Enterprise di Fase 2) sekarang berstatus `none` — belum terkunci, sesuai
§8.1.

### 8.9 Verifikasi yang dijalankan

```
php artisan test              → 1249 test, 1244 lulus, 5 skip, 0 gagal
./vendor/bin/pint --dirty     → lulus
npm run build (tsc -b && vite) → 0 error
npm run lint                  → 0 error, 0 warning
```

### 8.10 Yang belum dikerjakan

- **Backfill massal** — memberi langganan ke setiap client yang sudah ada
  sebelum Fase 3. Lihat §8.1; ini keputusan operasional pemilik produk, bukan
  kode.
- **Worker antrean dan email** — prasyarat operasional, dicatat §6 sejak
  rancangan awal, tidak berubah.
- **Penjadwalan `subscriptions:sweep`** — command-nya ada dan teruji, tapi
  tidak ada `Schedule::command(...)->daily()` yang mendaftarkannya. Repo ini
  tidak punya pola scheduling sebelumnya (`routes/console.php` maupun
  `bootstrap/app.php` kosong dari `Schedule::`), jadi menambahkannya tanpa
  konfirmasi infrastruktur cron yang sesungguhnya berisiko jadi kode mati atau
  mengejutkan. Perlu dijalankan manual atau disambungkan ke cron saat
  di-deploy.
- **Kasus staf-dari-client-kedaluwarsa** — lihat §8.2. Batasan yang disadari,
  bukan pekerjaan yang terlewat; keputusan menutupnya (dan bagaimana) milik
  pemilik produk.
