# Fase 4 — Profil Pembelian & Jurnal Umum

**Status: ⬜ Belum dikerjakan. Bergantung pada Fase 3.**

Dua profil transaksi berikutnya, mengikuti pola yang sudah ditetapkan Fase 3.
Sebagian besar pekerjaannya adalah pemakaian ulang; yang ditulis di sini hanya
perbedaannya.

## Tier

**Pro ke atas**, sama seperti faktur penjualan.

## 4a. Pembelian — `VendorBillService` (34,1 KB)

Cerminan hampir persis dari faktur penjualan:

| | Faktur penjualan | Tagihan pembelian |
|---|---|---|
| Service | `SalesInvoiceService` | `VendorBillService` |
| Kontak | Pelanggan | Pemasok |
| Buku pembantu | Piutang (AR) | Utang (AP) |
| Pemetaan akun | `SalesAccountResolverService` | `PurchaseAccountResolverService` |
| Kalkulasi | `SalesCalculationService` | `PurchaseCalculationService` |
| Arah stok | Keluar | Masuk |

Pengelompokan baris, validasi pratinjau, idempotensi, dan penomoran identik
dengan Fase 3.

**Satu perbedaan yang perlu diperhatikan:** stok **masuk**, jadi tidak ada
risiko stok minus. Sebaliknya muncul pertanyaan harga pokok — apakah impor
tagihan ikut memperbarui harga pokok rata-rata? Jawabannya harus sama dengan
form biasa, dan itu sudah ditangani `VendorBillService`. Selama importer lewat
service, tidak ada yang perlu diputuskan ulang.

## 4b. Jurnal umum — `JournalEntryService` (20,6 KB)

Paling sederhana secara akuntansi — tidak ada stok, tidak ada piutang/utang,
tidak ada kontak wajib — tapi punya satu syarat keras yang tidak dimiliki dua
profil lain.

### Keseimbangan debit-kredit per entri

Satu jurnal harus seimbang. Karena satu jurnal = beberapa baris berkas, ini
adalah **validasi tingkat kelompok** yang tidak boleh dilewati:

| ref | tanggal | akun | debit | kredit |
|---|---|---|---|---|
| JV-001 | 2026-08-11 | 1-1100 | 500.000 | |
| JV-001 | 2026-08-11 | 4-1000 | | 500.000 |

Kalau jumlah debit ≠ kredit dalam satu `ref`, seluruh kelompok ditandai galat di
pratinjau. `JournalValidationService` (10,6 KB) sudah memegang aturannya —
panggil itu, jangan menghitung ulang.

### Yang wajib divalidasi di pratinjau

| Pemeriksaan | Sumber |
|---|---|
| Debit = kredit per `ref` | `JournalValidationService` |
| Akun ada dan aktif | `ChartOfAccountService` |
| Akun bukan akun induk | `ChartOfAccountService` — posting ke akun induk merusak laporan |
| Periode masih terbuka | `TransactionDateGuardService` |
| Dimensi dikenal (kalau diisi) | `DepartmentService`, `ProjectService` |

### Dimensi — bersinggungan dengan tier

Jurnal umum bisa membawa `department_id` dan `project_id`. Keduanya **fitur
Enterprise** di [peta tier](../subscription-tiers/phase-2-peta-tier-dan-peluncuran.md#1-peta-tier-yang-disetujui).

Jadi berkas impor yang memuat kolom dimensi, diunggah client Pro, harus:

- **ditolak dengan pesan yang jelas** ("kolom departemen tidak termasuk paket
  Anda"), **bukan** diam-diam mengabaikan kolomnya

Mengabaikan diam-diam menghasilkan jurnal yang terlihat masuk tapi kehilangan
informasi yang dikira tersimpan — bentuk kerusakan data yang paling sulit
dilacak.

## Test

Selain yang setara dengan Fase 3:

**Pembelian**
- Tagihan terbentuk lewat `VendorBillService`, utang bertambah, stok masuk
- Pemasok tidak dikenal → galat per baris

**Jurnal umum**
- Debit ≠ kredit dalam satu `ref` → seluruh kelompok ditandai galat di pratinjau,
  nol jurnal terbentuk
- Posting ke akun induk → ditolak
- Akun nonaktif → ditolak
- Kolom dimensi diisi oleh client Pro → **ditolak dengan pesan paket**, bukan
  diabaikan
- Kolom dimensi diisi oleh client Enterprise → tersimpan dan muncul di laporan
  per departemen

## Risiko

- **Jurnal umum adalah pintu paling langsung ke buku besar.** Tidak ada dokumen
  sumber, tidak ada validasi bisnis di atasnya — apa pun yang lolos importer
  langsung jadi angka di laporan keuangan. Validasi pratinjau di sini bukan
  kenyamanan.
- **Impor jurnal bisa dipakai membetulkan kesalahan impor sebelumnya**, dan itu
  menumpuk. Pastikan `import_rows.document_id` benar-benar terisi supaya jejak
  balik ke batch asalnya tidak putus.
