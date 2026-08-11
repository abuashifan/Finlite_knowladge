# Fase 3 — Siklus Langganan

**Status: ⬜ Belum dikerjakan. Seluruh keputusannya sudah diambil.**

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
