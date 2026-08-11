# Fase 1 — Profil Master Data

**Status: ⬜ Belum dikerjakan. Bergantung pada Fase 0.**

Profil impor pertama: **kontak, produk, dan COA**. Sinkron, tanpa antrean.

Dikerjakan lebih dulu bukan karena paling penting, melainkan karena **paling
aman**. Master data tidak menyentuh buku besar: kalau pemetaan kolom atau
pratinjau ternyata salah di sini, akibatnya baris kontak yang keliru — bukan
ratusan jurnal yang harus di-void satu per satu.

Fase ini yang membuktikan mesin Fase 0 benar-benar bekerja sebelum dipercaya
memegang transaksi.

## Tier

**Basic ke atas.** Impor master data adalah kebutuhan **pindah masuk** — client
baru tidak boleh dipaksa mengetik ulang seluruh data lamanya hanya karena
berlangganan Basic.

## Tiga profil

Semuanya lewat service yang sudah ada. **Jangan** menulis model langsung.

| Profil | Service | Catatan |
|---|---|---|
| `contact` | `ContactService` (3,4 KB) | Pelanggan & pemasok |
| `product` | `ProductService` (10,7 KB) | Perlu kategori & satuan sudah ada lebih dulu |
| `chart_of_account` | `ChartOfAccountService` (12,7 KB) | Paling rawan — lihat di bawah |

### Kenapa COA paling rawan

COA punya **hierarki induk-anak** dan **tipe akun** yang menentukan arah saldo.
Dua akibatnya untuk importer:

- **Urutan baris penting.** Akun induk harus ada sebelum anaknya. Importer perlu
  mengurutkan sendiri berdasarkan kode/level, bukan mengandalkan urutan di
  berkas.
- **Impor ke COA yang sudah terisi berbahaya.** Perusahaan yang sudah melewati
  wizard onboarding sudah punya COA dari templat. Mengimpor di atasnya bisa
  menghasilkan akun ganda atau hierarki rusak.

Usulan: profil COA hanya mengizinkan **penambahan akun baru**, dan menolak baris
yang kodenya sudah ada — bukan menimpanya. Kalau nanti perlu "perbarui yang
sudah ada", itu mode terpisah yang dinyatakan eksplisit di layar.

## Templat unduhan

Satu templat `.xlsx` per profil, dengan header yang sudah benar dan satu baris
contoh. Ini jalur yang dipakai mayoritas client, dan ia membuat pemetaan kolom
otomatis.

Templat ikut memuat kolom wajib vs opsional secara visual (misal header wajib
dicetak tebal) — murah dibuat, banyak menghemat dukungan.

## Sinkron, bukan antrean

Ratusan baris master data tanpa posting jurnal selesai dalam hitungan detik.
Antrean baru masuk di Fase 2 untuk transaksi.

Konsekuensinya: batas ukuran berkas di fase ini lebih ketat daripada nanti.
Kalau ada client mengunggah 5.000 produk, ia akan menabrak batas waktu request —
dan pesan yang muncul harus menjelaskan itu, bukan galat 500.

## Test

- Tiga profil, masing-masing: berkas valid → data masuk lewat service, bukan
  langsung ke tabel
- Baris duplikat (kode/nama sudah ada) → ditandai `invalid` di pratinjau, tidak
  menggagalkan berkas
- COA: anak sebelum induk di berkas → tetap masuk dengan hierarki benar
- COA: kode sudah ada → ditolak, tidak menimpa
- Produk: kategori/satuan tidak dikenal → galat per baris yang menyebut nilainya
- Batch selesai → `import_rows.document_id` terisi, bisa ditelusuri balik

## Risiko

- **Mengimpor COA ke perusahaan yang sudah jalan** bisa merusak laporan keuangan
  yang sudah benar. Kalau ragu, batasi profil COA ke perusahaan yang belum
  memfinalisasi setup — `SetupWizardService` sudah tahu keadaan itu.
