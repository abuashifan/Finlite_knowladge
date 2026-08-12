# Tutorial Pengecekan Fitur Subscription Tiers

> Panduan untuk admin dalam memeriksa, mengelola, dan menegakkan fitur berdasarkan tier langganan di Finlite ERP.

---

## Daftar Isi

1. [Konsep Dasar](#1-konsep-dasar)
2. [Melihat Daftar Tier & Fitur](#2-melihat-daftar-tier--fitur)
3. [Memeriksa Paket Client](#3-memeriksa-paket-client)
4. [Cara Mengecek Fitur Mana yang Berlaku](#4-cara-mengecek-fitur-mana-yang-berlaku)
5. [Mengelola Siklus Langganan](#5-mengelola-siklus-langganan)
6. [Memahami Editor Role & Izin Terkunci](#6-memahami-editor-role--izin-terkunci)
7. [Menangani Penolakan Fitur](#7-menangani-penolakan-fitur)
8. [Peringatan Jatuh Tempo & Kedaluwarsa](#8-peringatan-jatuh-tempo--kedaluwarsa)
9. [Kuota Penyimpanan per Tier](#9-kuota-penyimpanan-per-tier)
10. [Pertanyaan Umum](#10-pertanyaan-umum)

---

## 1. Konsep Dasar

### Dua sumbu yang terpisah

Finlite memisahkan dua hal yang sering dikacaukan:

| Sumbu | Apa yang diatur | Mengikat siapa |
|---|---|---|
| **Paket / Tier** | Fitur apa yang boleh dipakai perusahaan ini | **Semua orang**, termasuk owner |
| **Permission / Role** | Apa yang boleh disentuh user tambahan | **User tambahan** (owner & admin dikecualikan) |

> 💡 **Intinya:** Paket menentukan "perusahaan ini punya fitur X?", permission menentukan "user ini boleh menyentuh fitur X?". Owner selalu punya semua permission (`*`), tapi **tetap terikat paket** — owner Basic tidak bisa membuat gudang kedua walaupun permission-nya `*`.

### Empat tier

| Tier | Perusahaan | User (termasuk owner) | Cocok untuk |
|---|---|---|---|
| **Basic** | 1 | 3 | UMKM, pembukuan inti, satu gudang |
| **Pro** | 3 | 5 | Multi-gudang, jejak audit, persetujuan transaksi, laporan tersimpan |
| **Enterprise** | 5 | 10 | Anggaran, dimensi departemen/proyek, role kustom |
| **Custom** | Manual | Manual | Fitur = Enterprise, angka disesuaikan |

> ⚠️ **Free dinonaktifkan.** Tidak ada tier gratis. Setiap client wajib memiliki paket berbayar.

---

## 2. Melihat Daftar Tier & Fitur

### Di aplikasi

Buka **Admin → Packages** (atau navigasi setara di area admin) untuk melihat:

- Daftar keempat tier beserta harga bulanan dan tahunan
- Jumlah perusahaan dan user yang termasuk
- Status aktif/nonaktif setiap tier

### Peta fitur lengkap

| Kemampuan | Basic | Pro | Enterprise |
|---|---|---|---|
| Pembukuan, jurnal, COA, tutup buku | ✅ | ✅ | ✅ |
| Penjualan, pembelian, faktur | ✅ | ✅ | ✅ |
| Kas, bank, rekonsiliasi | ✅ | ✅ | ✅ |
| Persediaan satu gudang | ✅ | ✅ | ✅ |
| Aktiva tetap & penyusutan | ✅ | ✅ | ✅ |
| Laporan standar satu periode | ✅ | ✅ | ✅ |
| Impor master data | ✅ | ✅ | ✅ |
| Multi-gudang | — | ✅ | ✅ |
| Jejak audit | — | ✅ | ✅ |
| Laporan tersimpan & berbagi | — | ✅ | ✅ |
| Banding multi-periode | — | ✅ | ✅ |
| Alur persetujuan transaksi | — | ✅ | ✅ |
| Impor transaksi | — | ✅ | ✅ |
| Anggaran | — | — | ✅ |
| Dimensi departemen & proyek | — | — | ✅ |
| Role kustom | — | — | ✅ |

> 💡 **Hak baca tidak pernah dicabut.** Client Enterprise yang turun ke Pro tetap bisa **membaca** anggaran lamanya — yang ditahan hanya **membuat** yang baru. Ini berlaku untuk semua fitur.

---

## 3. Memeriksa Paket Client

### Langkah 1: Buka daftar client

1. Buka **Admin → Client Management**
2. Cari client yang ingin diperiksa

### Langkah 2: Lihat informasi paket

Di baris client, perhatikan kolom:

| Kolom | Arti |
|---|---|
| **Paket** | Tier saat ini (`Basic`, `Pro`, `Enterprise`, `Custom`) |
| **Siklus** | `Bulanan` atau `Tahunan` |
| **Berakhir** | Tanggal berakhir langganan |
| **Sisa Hari** | Hitung mundur ke tanggal berakhir |

### Langkah 3: Buka tab Siklus Langganan

Klik client untuk membuka detail, lalu buka tab **"Siklus Langganan"**:

- Paket dan siklus periode berjalan
- Harga terkunci (harga saat langganan dimulai — tidak berubah walau harga paket naik)
- **Riwayat langganan**: daftar seluruh periode yang pernah dijalani client ini
- Status: **Aktif** / **Tenggang** (H+0 s.d. H+7 setelah berakhir) / **Kedaluwarsa** / **Dibatalkan** / **Belum berlangganan**

---

## 4. Cara Mengecek Fitur Mana yang Berlaku

### Mengecek lewat Editor Role (cara termudah)

1. Buka **Access → Roles**
2. Pilih atau buat role
3. Perhatikan daftar izin:

| Tampilan | Arti |
|---|---|
| Checkbox **aktif** (bisa dicentang) | Izin termasuk dalam paket client |
| Checkbox **terkunci** + ikon 🔒 | Izin **di luar paket** — tidak bisa diberikan ke user |
| Tooltip saat hover di izin terkunci | "Tidak termasuk paket saat ini" |

> 💡 Inilah cara paling cepat untuk tahu fitur apa yang TIDAK bisa dipakai client tertentu. Kalau izin `budgets.submit` terkunci di editor role, client itu tidak bisa mengajukan anggaran — walaupun role-nya diceklis `budgets.*`.

### Mengecek lewat respons API

Setiap request yang ditolak karena paket mengembalikan:

```json
{
  "success": false,
  "code": "FEATURE_NOT_IN_PLAN",
  "message": "Fitur 'Anggaran' tidak termasuk dalam paket Basic Anda. Upgrade ke Enterprise untuk mengakses fitur ini.",
  "upgrade_url": "https://wa.me/628xxxxxx?text=..."
}
```

### Mengecek di frontend — jaring pengaman global

Interceptor axios di frontend menangkap **setiap** respons `FEATURE_NOT_IN_PLAN` dari mana pun di aplikasi, dan otomatis menampilkan toast dengan tombol **"Minta Upgrade"** — tanpa perlu dicek manual satu per satu.

---

## 5. Mengelola Siklus Langganan

### Subscribe — langganan pertama

Untuk client yang **belum pernah** berlangganan (`state: none`):

1. Buka detail client → tab **Siklus Langganan**
2. Klik **"Subscribe"**
3. Pilih paket dan siklus (bulanan/tahunan)
4. Harga otomatis terkunci dari harga paket saat itu
5. Klik **"Simpan"** — baris langganan pertama dibuat

> ⚠️ **Client dengan state `none` TIDAK terkunci login.** Kunci penuh baru berlaku setelah client pernah di-subscribe lalu kedaluwarsa. Ini melindungi client lama yang belum di-backfill.

### Renew — perpanjang

Untuk client yang langganannya akan/sudah berakhir:

1. Buka tab **Siklus Langganan**
2. Klik **"Perpanjang"** (berbeda dari Buka Kunci!)
3. Pilih siklus — opsional: ganti paket (upgrade/downgrade)
4. Baris **baru** dibuat, mulai tepat di `ends_at` baris sebelumnya
5. Harga dikunci dari harga paket **saat ini** (bisa berbeda dari harga baris lama)

> 💡 Riwayat langganan terbentuk otomatis — setiap perpanjangan adalah baris baru, bukan menggeser tanggal baris lama. Kamu bisa melihat seluruh riwayat penagihan client.

### Unlock — buka kunci darurat

Untuk client yang **kedaluwarsa** dan perlu akses segera:

1. Buka tab **Siklus Langganan**
2. Klik **"Buka Kunci"**
3. `ends_at` digeser ke **sekarang** — client masuk masa **tenggang 7 hari**
4. **Tidak** membuat baris riwayat baru (ini jalur darurat, bukan perpanjangan berbayar)

> ⚠️ **Buka Kunci ≠ Perpanjang.** Buka Kunci memberi waktu 7 hari untuk menarik data atau menyelesaikan pembayaran. Perpanjang adalah langganan normal yang membuat baris penagihan baru.

### Cancel — batalkan

1. Buka tab **Siklus Langganan**
2. Klik **"Batalkan"**
3. `cancelled_at` diisi — client **langsung terkunci** (tidak ada tenggang)

> ⚠️ **Hati-hati:** Cancel mengunci seketika, tidak seperti kedaluwarsa yang masih memberi tenggang 7 hari.

---

## 6. Memahami Editor Role & Izin Terkunci

### Kenapa ada izin yang terkunci?

Editor role (modul Access) menampilkan **semua** izin yang ada di sistem — termasuk yang di luar paket client. Izin di luar paket:

- **Tidak bisa dicentang** (checkbox nonaktif)
- Ditandai ikon 🔒
- Tooltip: "Tidak termasuk paket saat ini"
- Ada tombol **"Minta Upgrade"** di header editor (muncul kalau minimal ada satu izin terkunci)

### Kenapa tidak disembunyikan saja?

Dua alasan:

1. **Jujur** — admin perusahaan tahu izin itu ada dan kenapa tidak bisa dipakai. Kalau disembunyikan, admin mengira fiturnya belum dibangun.
2. **Jalur penjualan** — tombol "Minta Upgrade" di sebelah izin terkunci mengarah ke WhatsApp dengan pesan terisi otomatis: nama perusahaan, paket sekarang, dan fitur yang diminta.

### Yang bisa dilihat admin perusahaan

| Yang muncul di editor role | Kenapa |
|---|---|
| Semua izin yang **termasuk** paket | Bisa diberikan ke role |
| Semua izin di **luar** paket | Terkunci + tombol upgrade |
| `access.roles.view` (melihat role) | **Selalu terbuka** — baca tidak digerbangi |
| `access.roles.create` (membuat role) | **Enterprise only** |

---

## 7. Menangani Penolakan Fitur

### Alur penolakan

```
User melakukan aksi → backend memeriksa permission → lolos → backend
memeriksa paket → FITUR TIDAK TERMASUK PAKET →
response "FEATURE_NOT_IN_PLAN" → toast di frontend + tombol WhatsApp
```

### Tiga tempat tombol "Minta Upgrade" muncul

| Tempat | Kapan muncul |
|---|---|
| **Toast global** (interceptor axios) | Setiap respons `FEATURE_NOT_IN_PLAN` di mana pun — otomatis |
| **Editor role** | Header editor menampilkan tombol kalau ada izin terkunci |
| **Layar penolakan fitur** | Kalau UI secara spesifik menampilkan pesan penolakan |

### Isi pesan WhatsApp otomatis

Ketika user mengklik "Minta Upgrade", WhatsApp terbuka dengan pesan:

> *"Halo, saya [Nama Perusahaan] saat ini menggunakan paket [Basic/Pro/Enterprise]. Saya ingin mengakses fitur [nama fitur]. Apakah bisa dibantu untuk upgrade?"*

Nomor WhatsApp diambil dari konfigurasi `SUPPORT_WHATSAPP_NUMBER` di `.env`.

> ⚠️ Kalau nomor belum diisi, tombol "Minta Upgrade" **tidak muncul** — jadi pastikan nomor support sudah dikonfigurasi.

---

## 8. Peringatan Jatuh Tempo & Kedaluwarsa

### Timeline

```
H-14                H+0              H+7
 │                   │                │
 ├── Peringatan ────┤── Tenggang ────┤── Kunci Penuh
 │  (badge topbar)   │  (akses penuh) │  (login ditolak)
 │                   │                │
 └── Hubungi client ─┴── Client harus ┴── Admin bisa buka kunci
     untuk perpanjang   segera bayar      (jalur darurat)
```

### Di aplikasi client

| Status | Yang terlihat |
|---|---|
| **Aktif (H-14 s.d. H-1)** | Badge kuning di topbar: "Langganan berakhir dalam X hari" + tooltip + tautan WhatsApp |
| **Tenggang (H+0 s.d. H+7)** | Badge oranye di topbar: "Masa tenggang, sisa X hari" — akses masih **penuh** |
| **Kedaluwarsa (H+8 dst.)** | **Login ditolak** — pesan: "Langganan Anda telah kedaluwarsa. Hubungi penyedia untuk memperpanjang." + tombol WhatsApp |

### Di area admin

Buka **Admin → Client Management** dan gunakan filter **"Jatuh Tempo 14 Hari"** untuk melihat:

- Client yang H-14 (harus mulai dihubungi)
- Client yang sedang dalam masa tenggang (harus segera ditagih)
- Client yang sudah kedaluwarsa (perlu tindakan)

### Command harian (subscriptions:sweep)

```
php artisan subscriptions:sweep --dry-run   # Lihat dulu — tidak mengubah apa pun
php artisan subscriptions:sweep             # Jalan sungguhan
```

Dua tugas command ini:

1. **Mencabut token** client yang baru melewati tenggang → mereka langsung logout
2. **Menandai** client H-14 dan tenggang untuk daftar "jatuh tempo"

> ⚠️ Command ini **harus** dijalankan harian lewat cron. Tanpa ini, token client kedaluwarsa tetap hidup, dan daftar "jatuh tempo" di admin tidak terbarukan.

---

## 9. Kuota Penyimpanan per Tier

Setiap tier punya batas penyimpanan untuk database tenant dan berkas impor:

| Tier | Kuota |
|---|---|
| Basic | 1 GB |
| Pro | 2 GB |
| Enterprise | 5 GB |
| Custom | Manual |

### Cara mengecek pemakaian

```
php artisan storage:measure
```

Command ini mengukur total ukuran file sqlite tenant + berkas impor untuk setiap perusahaan dan mencatatnya.

### Yang terjadi kalau kuota terlampaui

Kuota ditegakkan **sebelum unggahan impor diterima** — di titik yang paling mungkin melonjak. Kalau client mencoba mengunggah berkas impor dan kuotanya penuh:

```json
{
  "success": false,
  "code": "STORAGE_QUOTA_EXCEEDED",
  "message": "Kuota penyimpanan 1 GB terlampaui. Upgrade ke Pro untuk mendapat 2 GB."
}
```

### Cara mengurangi pemakaian

- Hapus berkas impor yang sudah lewat 30 hari (otomatis disweep)
- Hapus batch impor yang sudah tidak diperlukan
- Hapus data perusahaan yang sudah tidak aktif

---

## 10. Pertanyaan Umum

### Q: Bagaimana cara tahu client ini tier apa?

Buka **Admin → Client Management**, lihat kolom **Paket**. Atau lihat `users.plan_id` di database central — join ke tabel `plans`.

### Q: Client belum di-backfill — apa yang terjadi?

Client yang **belum pernah** di-subscribe (tidak punya baris di `subscriptions`) berstatus `none`. Mereka **tidak terkunci** dan **tidak melihat badge peringatan**. Backfill massal adalah keputusan operasional terpisah — belum dikerjakan.

### Q: Bagaimana kalau client perlu upgrade?

1. Buka detail client → tab **Siklus Langganan**
2. Klik **"Perpanjang"**
3. Pilih paket yang lebih tinggi
4. Harga dikunci dari harga paket saat ini
5. Mulai dari `ends_at` periode sebelumnya

### Q: Bisakah client downgrade?

Bisa — pilih paket yang lebih rendah saat perpanjang. Konsekuensinya:

- **Fitur baru ditahan** — tidak bisa membuat gudang/anggaran/dimensi baru
- **Data lama tetap bisa dibaca** — anggaran dan dimensi yang sudah ada tetap muncul
- **Role kustom tetap ada** — hanya tidak bisa membuat atau mengubah

### Q: Kenapa owner tidak bisa mengakses fitur padahal permission `*`?

Karena **paket mengikat semua orang, termasuk owner**. Kalau owner Basic mencoba membuat gudang kedua, responsnya `FEATURE_NOT_IN_PLAN`, bukan `PERMISSION_DENIED`. Ini sengaja — kalau owner dikecualikan, gerbang paket tidak pernah benar-benar menutup.

### Q: Kenapa staff saya masih bisa login padahal client-nya kedaluwarsa?

Penguncian login berlaku per user — user yang diperiksa adalah user yang sedang login, bukan "pemilik perusahaan tempat dia bekerja". Staff yang bukan pemilik langganan (tidak punya baris `subscriptions` sendiri) tidak terkunci oleh mekanisme ini. Ini batasan yang disadari — kalau nanti mau diubah, sumbunya lewat lapis paket di `company.access`, bukan di titik login.

### Q: Apakah fitur `export_excel_pdf` benar-benar tersedia?

**Belum.** Peta tier menandainya `true` di semua tier, tapi ekspor Excel/PDF **belum dibangun** — tidak ada rute ekspor, tidak ada pustaka ekspor di frontend. Izin `reports.export` adalah "izin hantu" yang diberikan ke role tapi tidak dipakai rute mana pun. Fitur ini sudah dirancang di [Data Import Fase 6](../plans/data-import/phase-6-ekspor.md).

### Q: Bagaimana cara mematikan sementara seluruh penegakan paket?

Setel di `.env`:

```
PLAN_FEATURES_ENFORCE=false
```

Semua gerbang paket akan terbuka — semua tier bisa mengakses semua fitur. **Jangan lupa dinyalakan kembali.** Ini hanya untuk keadaan darurat.
