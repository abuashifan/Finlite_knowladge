# Visi dan Batas Produk — KONSEP BARU

**Status:** Usulan, belum implementasi.

## Pola ekosistem

- **Finlite Accounting/ERP (sudah ada):** sumber kebenaran keuangan, GL, COA, invoice, kas/bank, AP/AR, budget control sesuai implementasi aktual.
- **Finlite POS (rencana):** UI kasir, cart, shift, closing, retur; online-only (keputusan 2026-10-30, lihat dokumen 06); dapat dipakai tanpa Accounting, dan menyinkronkan penjualan ke Accounting bila keduanya dimiliki organisasi yang sama.
- **Finlite WMS (rencana):** workflow fisik gudang, bin, picking/packing, receiving, stock count; penyesuaian stok sah melalui aturan Inventory.
- **Finlite Workspace (rencana):** portal pegawai, struktur organisasi, pengajuan, approval, RAB, proyek/kegiatan, LPJ, monitoring. **Berdiri sendiri** (keputusan 2026-11-01): memiliki data anggaran sendiri dan tidak bergantung pada Accounting; integrasi dengan Accounting bersifat opsional.
- **Finlite CRM (rencana):** relasi pelanggan, leads, sales pipeline, customer service; bukan nama untuk portal internal pegawai.

## Contoh segmen sekolah/yayasan

Satu organisasi dapat memiliki beberapa unit (SMP, SMK, pesantren, kantor yayasan), departemen (kurikulum, sarpras, keuangan), jabatan, pegawai, proyek, dan sumber anggaran. Pemetaan unit ke company/tenant Finlite **belum diputuskan**: jangan mengasumsikan satu unit selalu sama dengan satu company.

## Pengalaman pengguna

- Pegawai mengakses Workspace dengan hak akses per orang dan lisensi yang berbeda dari Accounting.
- Kepala departemen menyetujui proposal dan memantau aktivitas tim.
- Keuangan memvalidasi anggaran, pencairan, pertanggungjawaban, dan rekonsiliasi dengan Accounting.
- Manajemen melihat konsolidasi sesuai hak akses, tanpa membuka data tenant yang tidak berwenang.

## Non-goals awal

Tidak membangun ulang GL, membuat ledger paralel, atau otomatis mem-posting dokumen pengajuan sebagai jurnal. Tidak mengasumsikan semua produk harus menjadi microservice sejak hari pertama.

## Hipotesis bisnis

Workspace dapat menjadi produk pertama untuk organisasi dengan banyak pegawai tetapi sedikit staf akuntansi, termasuk yang belum memakai Accounting. Validasi melalui wawancara pengguna dan pilot sebelum menentukan harga, skema lisensi, atau prioritas final. Segmen pelanggan dan skema langganan dirinci pada dokumen 07.
