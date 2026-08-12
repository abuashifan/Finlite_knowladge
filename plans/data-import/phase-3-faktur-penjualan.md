# Fase 3 — Profil Faktur Penjualan

**Status: ✅ Selesai — 2026-08-12.**

Profil transaksi pertama, dan **inti dari kenapa rencana ini ada**: ratusan
faktur ke pelanggan tetap, setiap hari.

Fase ini yang paling sulit. Pola yang ditetapkan di sini diikuti dua modul
berikutnya, jadi kesalahan rancangan di sini terbawa tiga kali.

## Tier

**Pro ke atas.**

## Dua aturan tunggal

**1. Importer wajib lewat `SalesInvoiceService`** (38,7 KB). Service itu yang
memegang kalkulasi, penomoran, dan — saat posting — jurnal serta piutang.
Menulis ke tabel langsung menghasilkan faktur yang tampak benar di layar tapi
tidak pernah masuk buku besar, dan itu baru ketahuan saat tutup buku.

Konsekuensinya: importer **tidak boleh** punya logika akuntansi sendiri. Ia hanya
menerjemahkan baris berkas jadi payload yang sama persis dengan yang dikirim form
faktur, lalu memanggil service.

**2. Impor selalu menghasilkan `TransactionStatus::DRAFT`. Tidak pernah
memposting.** Keputusan pemilik produk 2026-08-11: user memeriksa hasil impor
lebih dulu, lalu memposting lewat bulk action terpisah.

Ini menyederhanakan hampir semuanya:

- **Membatalkan batch = menghapus draft.** Tidak ada jurnal yang pernah
  terbentuk, jadi tidak ada yang perlu di-void atau dibalik.
- **Periode tertutup** tidak lagi jadi penghalang saat impor — ia diperiksa saat
  posting, oleh `TransactionDateGuardService` yang sudah dipanggil jalur normal.
- **Stok tidak bergerak** saat impor, jadi risiko stok minus di tengah batch
  hilang.
- **Beban antrean turun drastis** — membuat draft jauh lebih ringan daripada
  memposting.

## Bulk post — pekerjaan baru

Terverifikasi: **tidak ada aksi bulk post** di modul mana pun (nol rute bulk di
Sales). Ini dibangun di sini dan dipakai ulang Fase 4.

Bentuknya:

```
POST /sales/invoices/bulk-post     { ids: [...] }  atau  { import_batch_id: ... }
```

Aturan yang tidak boleh dilonggarkan:

- Memposting **satu per satu lewat `SalesInvoiceService`**, bukan operasi massal
  di database. Setiap faktur tetap melewati penjaga periode, pemeriksaan stok,
  dan penomoran yang sama dengan posting manual.
- **Sebagian boleh berhasil.** Faktur yang gagal diposting tetap draft, dengan
  alasannya dilaporkan per baris. Batch tidak dibatalkan seluruhnya karena satu
  faktur bermasalah.
- Lewat antrean kalau jumlahnya besar — memakai kerangka Fase 2.

Aksi ini berguna di luar impor juga: memposting sekumpulan draft adalah
kebutuhan sehari-hari yang selama ini harus dilakukan satu per satu.

## Satu faktur, beberapa baris berkas

Faktur punya banyak baris barang, sementara berkas Excel/CSV datar. Jadi
beberapa baris berkas = satu faktur.

Perlu **kolom pengelompokan** — biasanya nomor referensi eksternal:

| ref | tanggal | pelanggan | produk | qty | harga |
|---|---|---|---|---|---|
| INV-001 | 2026-08-11 | PT Alfa | Barang A | 2 | 50.000 |
| INV-001 | 2026-08-11 | PT Alfa | Barang B | 1 | 75.000 |
| INV-002 | 2026-08-11 | PT Beta | Barang A | 5 | 50.000 |

Dua baris pertama jadi satu faktur dua baris barang.

Akibatnya untuk mesin Fase 0: validasi tidak murni per baris lagi. Ada validasi
**tingkat baris** (produk dikenal? qty angka?) dan **tingkat kelompok** (semua
baris satu `ref` punya tanggal dan pelanggan yang sama?). Pratinjau harus
menampilkan keduanya, dikelompokkan per faktur — bukan daftar datar 500 baris.

Kolom pengelompokan ini sekaligus jadi `external_ref` untuk idempotensi.

## Yang wajib divalidasi di pratinjau, bukan saat menulis

| Pemeriksaan | Sumber | Kenapa di pratinjau |
|---|---|---|
| Periode masih terbuka | `TransactionDateGuardService` | Faktur bertanggal periode tertutup harus ditolak sebelum satu pun jurnal terbentuk |
| Pelanggan dikenal | `ContactService` | Salah ketik nama pelanggan di 300 baris lebih murah diperbaiki di berkas |
| Produk & satuan dikenal | `ProductService` | idem |
| Akun terpetakan | `SalesAccountResolverService` | Faktur tanpa pemetaan akun akan gagal di tengah batch |
| Termin & jatuh tempo | `PaymentTermDueDateService` | |
| `external_ref` belum dipakai | unique index Fase 0 | Mencegah faktur ganda |

Aturannya: **apa pun yang bisa diketahui sebelum menulis, diketahui di
pratinjau.** Yang tersisa saat commit hanyalah kegagalan yang benar-benar tidak
bisa diramalkan.

## Penomoran di bawah konkurensi ⚠️ perlu diperiksa lebih dulu

`DocumentNumberService` (8,4 KB) memberi nomor urut dokumen. Impor 500 faktur
dalam satu job memanggilnya 500 kali berturut-turut.

**Sebelum fase ini dikerjakan, periksa apakah service itu aman terhadap
balapan.** Kalau ia membaca nomor terakhir lalu menambah satu tanpa penguncian,
dua job yang berjalan bersamaan (dua perusahaan, atau dua batch) bisa
menghasilkan nomor kembar — dan nomor faktur kembar adalah masalah pajak, bukan
sekadar bug.

Kalau ternyata belum aman, memperbaikinya **mendahului** importer.

## Sebagian atau semua-atau-tidak — keputusan terbuka

Kalau baris ke-300 dari 500 gagal:

- **Sebagian masuk** — 299 faktur terbentuk, sisanya dilaporkan. Lebih berguna
  untuk operasi harian: pekerjaan hari itu tidak berhenti karena satu baris
  salah.
- **Semua-atau-tidak** — rollback penuh. Lebih bersih untuk rekonsiliasi, tapi
  satu salah ketik membatalkan pekerjaan setengah hari.

Rekomendasi: **sebagian masuk**, karena kasus pemakaiannya harian dan pratinjau
sudah menyaring mayoritas kesalahan lebih dulu. Tapi ini keputusan pemilik
produk — ia memengaruhi cara rekonsiliasi dibaca.

Apa pun pilihannya, `import_rows` mencatat per baris apa yang terjadi, jadi
keadaannya selalu bisa dibaca setelahnya.

## Test

- Berkas valid → faktur terbentuk lewat `SalesInvoiceService`, jurnal terposting,
  piutang bertambah
- Beberapa baris satu `ref` → satu faktur dengan banyak baris barang
- Baris satu kelompok punya tanggal berbeda → ditandai galat kelompok di
  pratinjau
- Tanggal di periode tertutup → ditolak **di pratinjau**, nol jurnal terbentuk
- Pelanggan/produk tidak dikenal → galat per baris menyebut nilainya
- `external_ref` sudah dipakai → ditolak, tidak membuat faktur kedua
- Batch diulang setelah gagal sebagian → tidak ada faktur ganda
- Nomor faktur berurutan tanpa kembar untuk 100 faktur dalam satu batch

## Risiko

- **Penomoran kembar** — lihat di atas. Periksa sebelum mulai.
- **Stok minus.** Faktur penjualan memicu mutasi stok. 500 faktur sekaligus bisa
  menghabiskan stok di tengah batch; perilakunya harus sama dengan form biasa
  (mengikuti kebijakan yang sudah ada), bukan dilonggarkan demi impor.
- **Pratinjau yang terlalu lambat.** Validasi 500 baris memanggil beberapa
  service per baris. Kalau pratinjau sendiri jadi lambat, ia perlu ikut masuk
  antrean — bentuknya sudah ada sejak Fase 2.
