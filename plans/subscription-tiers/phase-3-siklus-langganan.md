# Fase 3 — Siklus Langganan

**Status: ⬜ Belum dikerjakan. Belum disetujui.**

Skema pemilik produk memuat `price.monthly` dan `price.yearly`. Begitu ada
periode berbayar, ada tanggal mulai, tanggal berakhir, dan pertanyaan "apa yang
terjadi setelah lewat" — tidak satu pun yang ada hari ini.

Fase ini bisa dikerjakan **tanpa** Fase 1–2; ia tegak lurus terhadap feature
gate. Tapi ia baru mendesak ketika penagihan benar-benar dimulai.

## Keadaan terverifikasi 2026-08-11

- Paket menempel di **client**: `users.plan_id`.
- Tabel `subscriptions` **ada** tapi ber-scope **perusahaan**, dan **tidak
  dipakai untuk kuota sama sekali**. Ini ketidakcocokan yang sudah ditemukan
  saat membangun kuota perusahaan — alasan kuota diikat ke user, bukan ke
  `subscriptions`.
- Tidak ada trial, kedaluwarsa, atau masa tenggang.
- `companies.status` mengenal nilai `trial` (perusahaan #1 di database dev
  berstatus itu), tapi tidak ada logika yang membacanya sebagai masa percobaan
  berjangka. Statusnya juga di level perusahaan, sementara langganan di level
  client — jangan pakai ini sebagai fondasi trial tanpa memikirkan ulang.

## Keputusan yang sudah diambil

### Siklus penagihan: bulanan atau tahunan, tidak ada yang lain

Ditetapkan pemilik produk 2026-08-11: *"client hanya bisa memilih pembayaran per
bulan atau per tahun."*

Artinya siklusnya **enum tertutup dua nilai** — `monthly` | `yearly`. Bukan
jumlah hari, bukan jumlah bulan yang bisa diisi bebas. Tidak ada kuartalan,
tidak ada seumur hidup.

Ini menyederhanakan dua hal sekaligus:

- **Perhitungan tanggal berakhir** cuma punya dua cabang:
  `addMonthNoOverflow()` atau `addYear()`. Pakai varian *no-overflow*: langganan
  bulanan yang dimulai 31 Januari harus berakhir 28/29 Februari, bukan melompat
  ke 3 Maret.
- **Harga sudah tersedia.** Tabel `plans` sudah punya `monthly_price` dan
  `yearly_price` (`decimal(15,2)`, bawaan 0) sejak
  `2026_05_15_000004_create_plans_table.php`. Tidak perlu kolom harga baru —
  yang belum ada hanyalah catatan langganannya.

Yang perlu disimpan di catatan langganan: `billing_cycle` (`monthly`/`yearly`),
`starts_at`, `ends_at`, dan harga yang **dikunci saat berlangganan** — kalau
harga paket naik, client yang sedang berjalan tidak boleh ikut berubah di tengah
periode.

### Tidak ada trial, tidak ada Free

Ditetapkan pemilik produk 2026-08-11. Free dinonaktifkan sampai ada modal untuk
menanggung biayanya, dan masa percobaan tidak pernah diadakan.

Akibatnya untuk fase ini: **tidak ada status "belum berlangganan" yang sah.**
Setiap client punya paket berbayar sejak dibuat, jadi siklus langganan hanya
punya tiga keadaan — aktif, dalam tenggang, kedaluwarsa.

Nilai `trial` di `companies.status` (dipakai perusahaan #1 di database dev) jadi
tidak bermakna. Tandai untuk dibersihkan.

### Kedaluwarsa: kunci penuh, tenggang 7 hari, pengingat H-14

Ditetapkan pemilik produk 2026-08-11.

| | |
|---|---|
| Pengingat | **H-14** sebelum `ends_at` |
| Masa tenggang | **7 hari** setelah `ends_at` — akses penuh berlanjut |
| Setelah tenggang | **Kunci penuh** — login ditolak |

Aku sempat merekomendasikan "turun ke Free" dan menyarankan agar kunci penuh
dihindari; pemilik produk memutuskan sebaliknya, dan keputusan itu yang berlaku.

Satu hal faktual yang perlu diurus dalam pelaksanaannya, bukan untuk membatalkan
keputusan: pembukuan itu dokumen yang wajib disimpan dan bisa diproduksi ulang
untuk keperluan pajak. Client yang terkunci tidak bisa menariknya. Dua peredam
yang tidak mengubah keputusan:

1. **Admin bisa membuka kunci** dari area admin kapan saja — jalur pemulihan
   untuk client yang membayar terlambat atau butuh datanya untuk pelaporan.
2. **Selama 7 hari tenggang, akses masih penuh**, jadi ada jendela nyata untuk
   menarik data. Ini menguatkan alasan membangun fitur ekspor
   ([data-import Fase 6](../data-import/phase-6-ekspor.md)) sebelum penguncian
   dinyalakan.

Pesan penguncian wajib menyebut cara menghubungi — tautan WhatsApp yang sama
dengan yang dipakai gerbang fitur.

## Keputusan yang masih harus diambil

### 1. Nasib tabel `subscriptions`

Tiga jalan:

- **Pindahkan ke client.** `subscriptions.user_id` menggantikan `company_id`.
  Paling konsisten dengan model sekarang (paket = milik client), tapi mengubah
  tabel yang sudah ada.
- **Tinggalkan, pakai kolom di `users`.** `subscription_starts_at`,
  `subscription_ends_at`, `subscription_status`. Paling murah, tapi tidak
  menyimpan riwayat — tidak bisa menjawab "client ini pernah di paket apa".
- **Biarkan `subscriptions` mati, buat tabel baru.** Paling bersih secara
  konsep, menambah satu tabel lagi.

Rekomendasi: **yang pertama**, kalau riwayat langganan memang dibutuhkan untuk
penagihan. Kalau belum, yang kedua sudah cukup dan bisa ditingkatkan nanti.

### 2. Perpanjangan — manual, tapi mekanismenya belum ditetapkan

Ditetapkan pemilik produk: **manual dulu**, karena belum ada gerbang pembayaran.
Kamu yang memperpanjang lewat area admin setelah pembayaran diterima.

Yang belum diputuskan: apakah memperpanjang berarti **menggeser `ends_at`** pada
baris langganan yang sama, atau **membuat baris baru**. Bergantung pada keputusan
#1 — kalau riwayat langganan disimpan, baris baru; kalau tidak, geser tanggal.

## Pekerjaan (garis besar, menunggu keputusan #1)

- Kolom/tabel sesuai keputusan #1, memuat `billing_cycle`, `starts_at`,
  `ends_at`, dan harga terkunci. Plus migrasi.
- `SubscriptionStatusService` di `app/Shared/Subscription/` — menjawab
  "langganan client ini aktif, dalam tenggang, atau kedaluwarsa".
- **Penguncian di titik login**, bukan di `EnsureCompanyAccess`. Alasannya:
  penguncian berlaku ke client, bukan ke perusahaan, dan menolak di login memberi
  satu tempat untuk menampilkan pesan + tautan WhatsApp. Token yang sudah terbit
  ikut dicabut saat status berpindah ke terkunci — kalau tidak, sesi yang sedang
  berjalan tetap hidup sampai token kedaluwarsa sendiri.
- **Membuka kunci dari area admin** — satu tombol, jalur pemulihan wajib.
- Command terjadwal harian yang memindahkan status dan mengirim pengingat H-14.
  `QUEUE_CONNECTION=database` sudah aktif, tapi **belum ada worker yang berjalan
  di server** — prasyarat yang sama dengan
  [data-import Fase 2](../data-import/phase-2-antrean.md).
- Area admin: tanggal berakhir + sisa hari di daftar client dan tab Langganan.
- Spanduk peringatan di aplikasi client sejak H-14 dan selama masa tenggang.

**Pengingat H-14 lewat apa?** Belum ada pengiriman email sama sekali di aplikasi
ini (`MAIL_MAILER=array` di test, dan tidak ada notifikasi terdaftar). Kalau
pengingat harus sampai ke client, itu pekerjaan tersendiri. Jalur termurah untuk
gelombang pertama: spanduk di dalam aplikasi + daftar "akan jatuh tempo" di area
admin supaya kamu bisa menghubungi manual lewat WhatsApp.

## Yang sudah beres dan tidak perlu diulang

Perilaku **penurunan paket** sudah benar sejak kuota dibangun: perusahaan dan
user yang sudah ada tidak pernah dicabut, hanya penambahan berikutnya yang
ditahan. Flag `over_quota` di payload admin sudah menampilkan keadaan itu sebagai
kondisi sah, bukan error. Sejak keputusan "turun tier tidak mencabut hak baca",
lapis paket berperilaku sama.

**Kedaluwarsa adalah pengecualian dari pola itu** — ia mengunci penuh, bukan
menurunkan. Jadi ia tidak bisa memakai ulang mekanisme penurunan paket; ia
mekanisme tersendiri di titik login.

## Risiko

- **Penguncian penuh tanpa jalur ekspor** membuat client tidak bisa menarik
  pembukuannya untuk keperluan pajak. Tombol buka kunci di area admin adalah
  peredamnya, dan fitur ekspor sebaiknya sudah ada sebelum penguncian menyala.
- **Command terjadwal menyentuh seluruh basis client sekaligus.** Bug di sana
  mengunci semua orang dalam semalam. Wajib punya `--dry-run`, mencatat apa yang
  diubah, dan bisa dibalik.
- **Belum ada worker antrean maupun pengiriman email** di aplikasi ini. Keduanya
  prasyarat operasional, bukan kode semata.
