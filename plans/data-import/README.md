# Data Import — Index & Progress Ledger

> **Agent: baca file ini PERTAMA setiap sesi.** Ia menentukan fase mana yang
> sedang berjalan.

## Konteks — kenapa rencana ini ada

Ditanyakan saat menyusun skema tier 2026-08-11: skema langganan menandai
`data_import` sebagai fitur Pro, tapi audit menemukan **impor tidak ada sama
sekali** di aplikasi ini.

Pemilik produk memutuskan fitur ini **harus dibangun**, dengan alasan yang
mengubah bentuknya sepenuhnya:

> *"Fitur import adalah fitur yang harus ditambahkan, itu penting untuk transaksi
> berulang yang harus di input setiap hari seperti faktur penjualan ke ratusan
> customer tetap per hari."*

Ini **bukan impor migrasi**. Impor migrasi dijalankan sekali, boleh lambat, dan
hanya menyentuh master data. Yang diminta adalah **jalur operasional harian** —
ratusan dokumen per hari yang harus jadi jurnal, piutang/utang, dan mutasi stok.
Perbedaan itu menentukan hampir seluruh isi rencana ini: antrean, idempotensi,
pratinjau, dan pelaporan galat per baris semuanya wajib, bukan penyempurnaan.

## Keputusan yang sudah diambil

| Topik | Keputusan |
|---|---|
| Format berkas | **`.xlsx` dan CSV**, keduanya |
| Modul gelombang pertama | **Tiga**: faktur penjualan (Sales), pembelian (Purchase), jurnal umum (Journal) |
| Sumber data | Unggahan berkas, **bukan** API |
| **Hasil impor** | **Selalu draft. Tidak pernah auto-post.** Lihat di bawah — ini keputusan paling berpengaruh di rencana ini. |
| Posting | **Bulk action manual** setelah user memeriksa hasil impor |
| Batas berkas | **1.000 baris** |
| Impor bersamaan | Satu batch aktif per perusahaan |
| Tier — impor master data | **Basic** ke atas. Kebutuhan pindah masuk; client baru tidak boleh dipaksa mengetik ulang data lamanya. |
| Tier — impor transaksi | **Pro** ke atas. Alat operasional harian, dan menuntut worker antrean. |
| Ekspor | **Masuk rencana ini** ([Fase 6](phase-6-ekspor.md)), bukan rencana terpisah — ia memakai pustaka pembaca/penulis berkas yang sama. |

### Draft-only — keputusan yang paling menyederhanakan

Ditetapkan pemilik produk 2026-08-11:

> *"Import harus draft, tidak boleh auto post. Auto post dilakukan manual secara
> bulk action, tujuannya user cek dulu hasil importnya sudah benar atau belum
> kalau ada kesalahan bisa di batalkan."*

`TransactionStatus::DRAFT` sudah ada di
`app/Shared/TransactionLifecycle/TransactionStatus.php`, jadi keputusan ini
memakai siklus dokumen yang sudah berjalan — bukan membuat keadaan baru.

Dampaknya besar dan hampir seluruhnya meringankan:

| | Kalau auto-post | Draft-only |
|---|---|---|
| Membatalkan batch salah | Void ratusan dokumen terposting, dengan jurnal balik | **Hapus draft** — tidak ada jurnal yang pernah terbentuk |
| Periode tertutup | Harus ditolak saat impor | Baru relevan saat posting |
| Beban antrean | Berat: tiap dokumen memicu posting jurnal | Jauh lebih ringan |
| Kesalahan harga/kuantitas | Sudah masuk buku besar | Masih bisa diperbaiki |

**Yang jadi pekerjaan baru:** aplikasi ini **belum punya aksi bulk post** —
terverifikasi, nol rute bulk di modul Sales. Itu dibangun di
[Fase 3](phase-3-faktur-penjualan.md) dan dipakai ulang dua modul berikutnya.

## Keadaan terverifikasi 2026-08-11

### Yang sudah ada dan wajib dipakai ulang

| Modul | Service | Ukuran |
|---|---|---|
| Sales | `SalesInvoiceService` | 38,7 KB |
| Purchase | `VendorBillService` | 34,1 KB |
| Journal | `JournalEntryService` + `JournalValidationService` | 20,6 + 10,6 KB |
| Master data | `ContactService`, `ProductService`, `ChartOfAccountService` | 3,4 / 10,7 / 12,7 KB |
| Penomoran | `App\Shared\DocumentNumbering\DocumentNumberService` | 8,4 KB |
| Penjaga periode | `TransactionDateGuardService`, `TransactionPolicyService` | 5,3 + 8,2 KB |
| Jatuh tempo | `PaymentTermDueDateService` | 2,3 KB |

> **Aturan tunggal yang tidak boleh dilanggar di seluruh rencana ini:**
> importer **wajib** lewat service dokumen di atas, tidak boleh menulis ke tabel
> secara langsung. Service itu yang memegang posting jurnal, piutang/utang,
> mutasi stok, dan penomoran. Menulis langsung menghasilkan dokumen yang tampak
> benar di layar tapi tidak pernah masuk buku besar — dan itu baru ketahuan saat
> tutup buku.

### Yang belum ada

- **Nol pustaka pembaca berkas.** `composer.json` tidak memuat `phpspreadsheet`,
  `maatwebsite/excel`, maupun pembaca CSV.
- **`app/Jobs/` tidak ada sama sekali.** Belum ada satu pun pekerjaan latar di
  aplikasi ini. Tabel antreannya sendiri sudah ada
  (`0001_01_01_000002_create_jobs_table.php`, database pusat) dan
  `QUEUE_CONNECTION=database` sudah aktif — tapi **tidak pernah dipakai**.
  Impor transaksi akan jadi beban asinkron pertama.
- **Tidak ada worker antrean yang berjalan di server.** Ini kebutuhan
  operasional baru, bukan sekadar kode.
- **Tidak ada aksi bulk post** di modul mana pun.
- `FILESYSTEM_DISK=local` — belum ada pola penyimpanan berkas unggahan
  per perusahaan.
- **SQLite tenant tidak disetel untuk penulisan bersamaan.** Koneksi `tenant` di
  `config/database.php` tidak menyebut `journal_mode` maupun `busy_timeout`, jadi
  ia memakai mode `DELETE` bawaan — penulis memblokir pembaca, dan akses yang
  bentrok langsung dapat `SQLITE_BUSY` alih-alih menunggu. Selama ini aman karena
  semua penulisan datang dari request web yang pendek; worker antrean mengubah
  itu. Lihat [Fase 2](phase-2-antrean.md#penguncian-sqlite).
  *(Catatan: `PRAGMA synchronous = OFF` dan `journal_mode = MEMORY` di
  `TenantConnectionManager` **hanya berjalan di environment testing** — produksi
  tidak menanggung risiko korupsi itu.)*

## Fase

| Fase | Isi | Status |
|---|---|---|
| [0](phase-0-mesin-impor.md) | Mesin impor: unggah, baca `.xlsx`/CSV, pemetaan kolom, validasi, pratinjau. Sinkron, belum menulis dokumen apa pun. | ✅ Selesai |
| [1](phase-1-master-data.md) | Profil master data (kontak, produk, COA). Membuktikan mesin pada data berisiko rendah. Tier Basic. | ✅ Selesai |
| [2](phase-2-antrean.md) | Antrean: `app/Jobs` pertama, progres, penanganan gagal, pengikatan koneksi tenant di dalam job. | ✅ Selesai |
| [3](phase-3-faktur-penjualan.md) | Profil transaksi pertama. Yang paling sulit — menetapkan pola untuk dua modul berikutnya. | ⬜ Belum |
| [4](phase-4-pembelian-dan-jurnal.md) | Pembelian (`VendorBillService`) dan jurnal umum (`JournalEntryService`). | ⬜ Belum |
| [5](phase-5-gerbang-tier.md) | Kunci izin `*.import`, pemetaan ke tier, integrasi ke rencana subscription-tiers. | ⬜ Belum |
| [6](phase-6-ekspor.md) | Ekspor Excel/PDF untuk halaman daftar dan laporan. | ⬜ Belum |

Urutannya disengaja: **master data lebih dulu**, karena ia menguji mesin tanpa
menyentuh buku besar. Kalau pemetaan kolom atau pratinjau salah di sana,
akibatnya baris kontak yang keliru — bukan ratusan draft yang harus dihapus.

## Keputusan yang sudah diselesaikan

| Pertanyaan | Jawaban |
|---|---|
| Sebagian atau semua-atau-tidak | **Sebagian masuk** + laporan baris gagal. Diperkuat draft-only: yang "masuk" hanyalah draft. |
| Batas ukuran berkas | **1.000 baris** |
| Impor bersamaan dalam satu perusahaan | **Ditolak** — satu batch aktif per perusahaan. Ikut meredam penguncian SQLite. |
| Kunci idempoten | Aturan + templatnya diserahkan ke penyusun rencana — ditetapkan di [Fase 0](phase-0-mesin-impor.md#idempotensi--aturan-yang-ditetapkan) |

## Keputusan yang masih terbuka

Tidak ada yang menghalangi Fase 0–1. Yang tersisa muncul di fase transaksi:

1. **Apakah draft memakan nomor dokumen** (Fase 3). Kalau nomor diberikan saat
   draft dibuat, batch yang dihapus meninggalkan lubang di urutan nomor. Kalau
   diberikan saat posting, urutannya rapat tapi draft tidak punya identitas yang
   stabil untuk ditunjukkan ke user. **Perlu diperiksa dulu bagaimana form biasa
   melakukannya** — importer harus mengikuti, bukan memutuskan sendiri.

## Ketergantungan dengan rencana lain

Rencana ini **memasok** dua baris yang masih ⏳ di peta tier
[subscription-tiers Fase 2](../subscription-tiers/phase-2-peta-tier-dan-peluncuran.md#1-peta-tier-yang-disetujui).
Sebaliknya, subscription-tiers **tidak menunggu** rencana ini — enam entri
lainnya bisa dinyalakan lebih dulu.
