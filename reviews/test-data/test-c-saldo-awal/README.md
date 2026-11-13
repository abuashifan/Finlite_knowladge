# Data uji Test C: saldo awal dan aset tetap awal

Berkas impor untuk Test C pada template COA **Perdagangan Umum**. Pada test ini
saldo awal **tidak bisa diinput manual**; seluruhnya lewat impor, termasuk
kartu aset tetap (sama seperti praktik di lapangan).

| Berkas | Profil impor | Isi |
| --- | --- | --- |
| [`saldo-awal-perdagangan-umum.xlsx`](saldo-awal-perdagangan-umum.xlsx) | Saldo Awal (`opening_balance`) | Neraca saldo 19 baris, debit = kredit = Rp 1.777.500.000 |
| [`aset-tetap-awal-perdagangan-umum.xlsx`](aset-tetap-awal-perdagangan-umum.xlsx) | Aset Tetap Awal (`fixed_asset_opening`) | 10 kartu aset |
| [`buat-berkas-impor.py`](buat-berkas-impor.py) | | Skrip pembuat kedua berkas, tanggal saldo awal bisa diganti |

> **Semua angka dan nama aset adalah data contoh karangan**, bukan data klien.

## Asumsi

- **Tanggal saldo awal perusahaan: 31/12/2025.** Akumulasi penyusutan dihitung
  garis lurus sampai tanggal itu. Kalau tanggal saldo awal di perusahaan uji
  berbeda, buat ulang berkasnya:
  `python3 buat-berkas-impor.py . 2026-01-01` (butuh `openpyxl`). Tanpa itu,
  pratinjau memberi peringatan "menyimpang dari perkiraan garis lurus" (hanya
  peringatan; baris tetap masuk).
- COA perusahaan memakai template **Perdagangan Umum**. Kode akun harus ada dan
  berupa akun daun: 1100, 1110, 1120, 1131, 1132, 1140, 1500, 1510, 1511, 1520,
  1521, 1530, 1531, 1540, 1541, 2100, 2130, 3100, 3200.
- Modul **Aktiva Tetap** aktif (Pengaturan → Modul). Kalau mati, semua baris
  berkas aset tetap gagal. Template Perdagangan Umum menyalakannya.

## Isi berkas saldo awal

| Akun | Nama | Debit | Kredit |
| --- | --- | ---: | ---: |
| 1100 | Kas | 15.000.000 | |
| 1110 | Bank | 185.000.000 | |
| 1120 | Piutang Usaha | 62.500.000 | |
| 1131 | Persediaan Barang Dagang A | 96.000.000 | |
| 1132 | Persediaan Barang Dagang B | 54.000.000 | |
| 1140 | Uang Muka Pembelian | 10.000.000 | |
| 1500 | Tanah | 400.000.000 | |
| 1510 | Kendaraan | 245.000.000 | |
| 1511 | Akumulasi Penyusutan Kendaraan | | 109.895.833 |
| 1520 | Gedung | 600.000.000 | |
| 1521 | Akumulasi Penyusutan Gedung | | 157.500.000 |
| 1530 | Peralatan | 86.000.000 | |
| 1531 | Akumulasi Penyusutan Peralatan | | 49.083.333 |
| 1540 | Perangkat Lunak | 24.000.000 | |
| 1541 | Akumulasi Amortisasi Perangkat Lunak | | 9.500.000 |
| 2100 | Hutang Usaha | | 78.000.000 |
| 2130 | Uang Muka Penjualan | | 5.000.000 |
| 3100 | Modal Pemilik | | 500.000.000 |
| 3200 | Laba Ditahan | | 868.520.834 |

Laba ditahan dijadikan penyeimbang, jadi akun perantara 3900 tidak terpakai
(saldonya nol).

## Isi berkas aset tetap

| Aset | Kategori | Perolehan | Harga | Akumulasi | Umur (thn) |
| --- | --- | --- | ---: | ---: | ---: |
| Tanah Gudang Jl. Industri No. 12 | LAND | 10/05/2019 | 400.000.000 | 0 | |
| Gedung Gudang dan Kantor | BUILDING | 20/08/2020 | 600.000.000 | 157.500.000 | 20 |
| Mitsubishi L300 Pickup B 9123 KJ | VEHICLE | 12/02/2022 | 220.000.000 | 103.125.000 | 8 |
| Honda Vario Motor Operasional B 3456 TX | VEHICLE | 05/09/2023 | 25.000.000 | 6.770.833 | 8 |
| Mesin Kasir dan Printer Struk | OFFICE_EQUIP | 03/01/2024 | 15.000.000 | 6.875.000 | 4 |
| Laptop Lenovo ThinkPad | IT_EQUIP | 15/06/2024 | 14.000.000 | 4.958.333 | 4 |
| Komputer Admin Gudang | IT_EQUIP | 02/03/2023 | 9.000.000 | 6.000.000 | 4 |
| Rak Besi Gudang (set 20 unit) | FURNITURE | 10/10/2022 | 36.000.000 | 27.750.000 | 4 |
| Hand Pallet dan Troli Angkut | MACHINE | 18/07/2023 | 12.000.000 | 3.500.000 | 8 |
| Lisensi Software Kasir dan Stok | SOFTWARE | 01/04/2024 | 24.000.000 | 9.500.000 | 4 |

Total per kelas sama dengan akun di berkas saldo awal (kendaraan 245 jt dengan
akumulasi 109.895.833; peralatan 86 jt dengan akumulasi 49.083.333; dan
seterusnya), jadi rekonsiliasi register aset dengan buku besar harus **selisih
nol**.

## Cara mengimpor

1. Buka halaman **Import**, unggah `saldo-awal-perdagangan-umum.xlsx` dengan
   profil **Saldo Awal**. Periksa pratinjau, lalu commit.
2. Unggah `aset-tetap-awal-perdagangan-umum.xlsx` dengan profil **Aset Tetap
   Awal**. Urutan kedua impor bebas; keduanya tidak saling bergantung.

## Yang diperiksa setelah impor

- Saldo awal menjadi **satu jurnal** bersumber `opening_balance` (kode
  `OpeningBalanceImportCommitter`), langsung terposting. Neraca saldo per tanggal
  saldo awal sama dengan tabel di atas dan akun 3900 bernilai nol.
- Sepuluh kartu aset tetap berstatus **aktif**, lengkap dengan jadwal
  penyusutan sisa umurnya. Tanah tidak punya jadwal (tidak disusutkan).
- Laporan rekonsiliasi aset tetap (`fixedAssetReconciliation`) tidak
  menunjukkan selisih per kelas.
- Impor ulang berkas yang sama diberi peringatan unggahan ganda.
- Impor bisa dibatalkan: jurnal saldo awal di-**void**, bukan dihapus.

## Yang tidak tercakup

- **Stok per barang (kuantitas) tidak masuk lewat berkas ini.** Saldo
  persediaan 1131/1132 hanya mengisi nilai buku besar. Kuantitas stok butuh
  langkah terpisah bila Test C memeriksanya.
- Piutang dan hutang per pelanggan/pemasok juga hanya nilai akun; tidak ada
  rincian per kontak.

## Skenario negatif yang bisa dicoba (belum dibuatkan berkas)

Aturan di bawah ini dari validasi `OpeningBalanceImportCommitter` dan
`FixedAssetOpeningImportCommitter`:

- Akun induk (mis. 1130 atau 15) ditolak: saldo hanya untuk akun daun.
- Akun bertipe pendapatan atau beban ditolak (mis. 4100, 5100, 6100): laba periode lalu masuk lewat akun ekuitas.
- Debit dan kredit terisi sekaligus di satu baris ditolak.
- Akun sama muncul dua kali dalam satu berkas ditolak.
- Umur manfaat di luar 4, 8, 10, 16, 20 tahun ditolak (aset tetap).
- Akumulasi lebih besar dari harga perolehan dikurangi nilai sisa ditolak.
- Kategori yang tidak ada, atau tanggal bukan format `DD/MM/YYYY`, ditolak.
