# Fase 6 — Ekspor Excel & PDF

**Status: ✅ Selesai (Excel) — 2026-08-12. PDF ditunda.**

Dimasukkan ke rencana ini atas keputusan pemilik produk 2026-08-11, bukan jadi
rencana terpisah — ia memakai pustaka berkas yang sama dengan importer, dan
keduanya adalah dua arah dari pintu yang sama.

## Kenapa mendesak

Tiga alasan yang saling menguatkan:

1. **Skema tier menjanjikannya di semua tier.** `export_excel_pdf` ditandai
   `true` mulai Basic, padahal terverifikasi **nol rute ekspor, nol pustaka
   ekspor di frontend**, dan `reports.export` tidak disebut satu kali pun di
   seluruh `frontend/src`. Izin itu diberikan tiga role dan tidak menjaga apa
   pun — izin hantu.
2. **Client yang mengimpor ratusan faktur pasti ingin menariknya keluar.** Impor
   tanpa ekspor adalah jalan satu arah.
3. **Penguncian saat kedaluwarsa** ([subscription-tiers Fase 3](../subscription-tiers/phase-3-siklus-langganan.md))
   memutus akses client sepenuhnya setelah masa tenggang. Selama 7 hari tenggang
   itu, satu-satunya cara client menyelamatkan pembukuannya untuk keperluan pajak
   adalah mengekspornya. **Ekspor sebaiknya sudah ada sebelum penguncian
   dinyalakan.**

Alasan ketiga yang membuatnya bukan sekadar kenyamanan.

## Tier

**Semua tier**, termasuk Basic. Ini penerapan aturan yang sudah berlaku: apa pun
yang dibutuhkan agar client memegang pembukuannya sendiri tidak digerbangi.

Izin `reports.export` yang sudah ada dipakai apa adanya — tidak perlu kunci baru,
dan **tidak dipetakan ke tier**.

## Cakupan

| Jenis | Format | Catatan |
|---|---|---|
| Halaman daftar (jurnal, faktur, kontak, produk, …) | Excel | Menghormati filter yang sedang aktif — mengekspor 25 baris yang tampak di layar adalah jebakan klasik |
| Laporan keuangan (neraca, laba rugi, buku besar, neraca saldo) | Excel + PDF | PDF perlu tata letak, bukan sekadar tabel mentah |
| Hasil impor | Excel | Baris yang gagal, supaya bisa diperbaiki lalu diunggah ulang |

Poin pertama adalah yang paling mudah salah: ekspor harus menjalankan ulang
kueri dengan filter yang sama **tanpa paginasi**, bukan menyalin halaman yang
sedang tampil. Modul daftar sudah memindahkan filter ke query builder lewat
rencana *List Query Pushdown*, jadi fondasinya sudah benar.

## Pilihan teknis

**Excel** — `phpoffice/phpspreadsheet` yang sama dengan Fase 0. Ekspor besar
memakai `fromArray` bertahap atau penulis berbasis aliran, bukan merakit seluruh
lembar di memori.

**PDF** — belum ada pustaka apa pun. Dua jalur:

- **Server** (`barryvdh/laravel-dompdf` atau sejenis): tata letak konsisten,
  bisa dijadwalkan, tapi menambah pustaka dan beban CPU.
- **Klien** (cetak browser dengan CSS `@media print`): nol pustaka baru, tapi
  hasilnya bergantung browser.

Rekomendasi: **PDF di server** untuk laporan keuangan, karena hasilnya sering
dilampirkan ke pihak ketiga (bank, kantor pajak, auditor) dan harus terlihat
sama di mana pun.

## Ekspor besar lewat antrean

Ekspor buku besar setahun bisa puluhan ribu baris. Memakai kerangka antrean
Fase 2: batch ekspor, unduhan tersedia setelah selesai, berkas dihapus setelah
masa simpan.

Untuk daftar biasa yang beberapa ratus baris, sinkron sudah cukup — jangan
mengantrekan apa yang selesai dalam dua detik.

## Test

- Ekspor daftar menghormati filter aktif dan mengabaikan paginasi
- Ekspor 10.000 baris tidak menghabiskan memori
- Berkas hasil ekspor tersimpan per perusahaan, tidak bisa diambil perusahaan
  lain
- Laporan PDF memuat identitas perusahaan, periode, dan tanggal cetak
- Berkas terhapus setelah masa simpan

## Risiko

- **Isi ekspor adalah data keuangan lengkap.** Berkasnya tersimpan di luar
  database tenant, jadi berlaku aturan yang sama dengan berkas impor: lintasan
  per perusahaan, pemeriksaan kepemilikan, dan penghapusan terjadwal.
- **PDF menambah pustaka baru** dengan permukaan keamanannya sendiri. Kalau ini
  menghambat, kerjakan Excel lebih dulu dan PDF menyusul — Excel sendiri sudah
  menjawab kebutuhan "selamatkan pembukuan saya".
