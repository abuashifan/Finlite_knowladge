# Roadmap Eksplorasi dan Keputusan Terbuka

**STATUS: RENCANA BARU — belum dijadwalkan, belum diimplementasikan.**

## Tahap 0 — Discovery

- Wawancara 3–5 organisasi calon pengguna (misalnya sekolah/yayasan).
- Petakan alur proposal, RAB, approval, pencairan, LPJ, dan laporan yang dipakai sekarang.
- Audit modul Budget/Project/Inventory/Permissions di Finlite aktual.
- Pilih satu skenario pilot dengan kriteria keberhasilan terukur.

## Tahap 1 — Workspace MVP (usulan prioritas)

- Organization model dan akses pegawai.
- Pengajuan RAB + approval + lampiran.
- Budget check/reservation terintegrasi.
- Pencairan/uang muka dan LPJ dengan referensi ke transaksi Accounting.
- Dashboard serapan dan outstanding serta audit trail.

## Tahap 2 — POS (opsi berikutnya)

Kasir, shift, closing, retur, sinkronisasi ke Sales/Inventory, uji perangkat dan kebutuhan offline.

## Tahap 3 — WMS (opsi berikutnya)

Lokasi/bin, inbound/outbound, picking, transfer, opname, reconciliation stok.

## Tahap 4 — CRM (opsi berikutnya)

Leads, pipeline, account/contact, activity, customer service, integrasi ke Sales.

**Urutan bukan janji waktu atau roadmap yang sudah disetujui.** Evaluasi ulang setelah pilot dan estimasi engineering.

## Keputusan terbuka

1. Workspace: lisensi per organisasi, per active employee, atau paket unit?
2. Shared login/SSO: satu akun untuk beberapa aplikasi dan company?
3. Hierarki yayasan → sekolah → departemen: bagaimana dipetakan ke tenant dan company Finlite?
4. Sumber pagu: Budget module saat ini atau perlu perluasan?
5. Approval: per role, posisi, nominal, kategori, atau kombinasi?
6. Apakah pengajuan membuat reservasi saat submitted atau approved?
7. Apa definisi actual untuk pengeluaran uang muka, AP, dan transaksi yang belum posted?
8. Apakah POS harus offline-first?
9. Apakah WMS harus mendukung barcode, batch/lot, expiry, serial?
10. Kapan CRM benar-benar diperlukan dibanding portal internal?

## Definisi siap dibangun

Sebuah fitur baru boleh masuk implementasi setelah ada: pemilik domain, user story, permission matrix, diagram status, kontrak API/event, aturan akuntansi, migrasi data, skenario gagal/retry, dan acceptance test.
