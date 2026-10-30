# RENCANA BARU — Ekosistem Aplikasi Pendukung Finlite

> **STATUS: KONSEP / PROPOSAL PENGEMBANGAN BARU — BELUM DIIMPLEMENTASIKAN**
>
> Dibuat: 2026-10-30. Dokumen di folder ini adalah usulan arah produk masa depan, **bukan** dokumentasi fitur Finlite yang telah tersedia, bukan keputusan arsitektur final, dan bukan backlog yang sudah disetujui.

## Visi

Finlite Accounting/ERP tetap menjadi **financial core saat pelanggan mengaktifkannya**, tetapi bukan prasyarat aplikasi lainnya. Accounting, POS, WMS, Workspace, dan CRM direncanakan sebagai **produk yang dapat dibeli dan dipakai mandiri**, serta bisa ditambahkan ke organisasi yang sudah berlangganan produk lain atau dijual dalam bundle. Integrasi antaraplikasi bersifat opsional, melalui kontrak yang terkontrol.

| Calon produk | Sasaran | Cakupan awal |
| --- | --- | --- |
| Finlite Workspace | Sekolah, pesantren, yayasan, organisasi multi-unit/departemen | Portal pegawai, pengajuan anggaran/RAB, approval, proyek/kegiatan, pencairan, LPJ, tracking dan realisasi |
| Finlite POS | Minimarket, toko ATK/buku, koperasi, retail barang fisik | Kasir online, shift, retur, pembayaran, stok outlet, printer/Device Bridge; integrasi opsional |
| Finlite WMS | Gudang, distributor, organisasi multi-lokasi | Penerimaan, putaway, bin, picking, transfer, opname |
| Finlite CRM | Tim penjualan dan layanan pelanggan | Prospek, pipeline, aktivitas, tiket layanan |

**Catatan terminologi:** portal internal pegawai dan pengelolaan anggaran/proyek dinamai sementara **Workspace**, bukan CRM. CRM adalah domain hubungan pelanggan yang terpisah. Nama produk belum final.

## Keputusan terbaru untuk Finlite POS (2026-10-30)

- Fokus tahap awal: retail barang fisik, minimarket, toko ATK/buku, dan koperasi; **restoran, kitchen, manajemen meja dan workflow F&B dikeluarkan dari MVP**.
- POS **online-only**: transaksi resmi difinalisasi di server, tanpa mode transaksi offline.
- **Finlite Device Bridge wajib tersedia pada MVP**, melayani printer struk thermal, printer label barcode dan cash drawer; scanner barcode HID dapat dipakai langsung pada browser kompatibel.
- Antarmuka kasir dan backoffice berbasis web untuk laptop/tablet, dengan pengujian perangkat dan browser terpilih.
- POS standalone dapat dipakai tanpa Accounting; integrasi Accounting/WMS/CRM bersifat opsional.
- Baca [06-finlite-pos-konsep-dan-roadmap.md](06-finlite-pos-konsep-dan-roadmap.md) untuk segmen pasar, batas fitur, desain hardware, roadmap, dan risiko.

## Prinsip rancangan awal

1. Jangan menduplikasi general ledger, saldo keuangan, atau aturan posting Finlite.
2. Pertahankan batas tenant/perusahaan dan otorisasi yang eksplisit di setiap integrasi.
3. Bedakan identitas pengguna, keanggotaan organisasi, role, dan hak akses per aplikasi. Pegawai portal tidak otomatis menjadi pengguna Accounting.
4. Pemilik data (system of record) ditentukan per domain; hindari dua sumber kebenaran.
5. Integrasi memakai API/event terverifikasi, idempotency key, audit trail, dan rekonsiliasi; jangan mengakses database tenant aplikasi lain secara langsung.
6. Semua perubahan status keuangan mengikuti kebijakan approval, posting, period lock, dan void di Finlite.
7. Mulai dari arsitektur modular yang memanfaatkan backend yang ada bila layak; pemisahan service fisik memerlukan evaluasi teknis.

## Urutan eksplorasi (belum disetujui)

1. **Workspace**: validasi kebutuhan sekolah/yayasan, audit modul Budget yang sudah ada, desain organisasi dan workflow.
2. **POS**: validasi kebutuhan retail dan integrasi Sales/Inventory/Payment.
3. **WMS**: validasi operasi gudang dan hubungan dengan master stok.
4. **CRM**: eksplorasi terpisah setelah kebutuhan dan segmentasi pasar teruji.

Urutan ini merupakan hipotesis prioritas, **bukan komitmen jadwal**.

## Dokumen dalam folder

- [01-visi-dan-batas-produk.md](01-visi-dan-batas-produk.md) — batas domain dan hubungan aplikasi.
- [02-workspace-anggaran-proyek.md](02-workspace-anggaran-proyek.md) — konsep portal sekolah/organisasi, pengajuan sampai LPJ.
- [03-integrasi-dan-arsitektur-awal.md](03-integrasi-dan-arsitektur-awal.md) — ownership data, keamanan, integrasi.
- [04-roadmap-dan-pertanyaan-terbuka.md](04-roadmap-dan-pertanyaan-terbuka.md) — validasi, MVP, risiko, keputusan yang belum dibuat.
- [06-finlite-pos-konsep-dan-roadmap.md](06-finlite-pos-konsep-dan-roadmap.md) — konsep POS retail online-only dan Device Bridge dari MVP.

## Referensi kondisi saat ini

Baca dokumen pada `reference/` untuk keadaan Finlite yang sudah ada. Terutama arsitektur backend/frontend, Budget, penyimpanan tenant, dan permission. Jangan memperlakukan konsep di folder ini sebagai fitur yang sudah rilis.
