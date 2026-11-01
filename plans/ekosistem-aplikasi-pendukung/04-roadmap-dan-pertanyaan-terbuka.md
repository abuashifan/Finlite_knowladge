# Roadmap Eksplorasi dan Keputusan Terbuka

**STATUS: RENCANA BARU — belum dijadwalkan, belum diimplementasikan.**

> **Pembaruan 2026-11-01:** urutan tahap di bawah disesuaikan oleh keputusan di [07-keputusan-platform-segmen-dan-model-data.md](07-keputusan-platform-segmen-dan-model-data.md): **Tahap P (platform)** dibangun sebelum Workspace, Workspace berdiri sendiri tanpa Accounting, dan jembatan ke Accounting menjadi tahap tersendiri setelahnya.

## Tahap P — Platform (sebelum produk baru apa pun)

- Finlite ID, organisasi, dan keanggotaan.
- Hak pakai per organisasi per produk (paket, kursi, tanggal); menggantikan paket yang menempel ke pengguna pemilik.
- Perusahaan Accounting yang ada dipindahkan ke struktur organisasi tanpa perubahan perilaku.
- Tes isolasi data antarorganisasi.

## Tahap 0 — Discovery

- Wawancara 3–5 organisasi calon pengguna (misalnya sekolah/yayasan).
- Petakan alur proposal, RAB, approval, pencairan, LPJ, dan laporan yang dipakai sekarang.
- Audit modul Budget/Project/Inventory/Permissions di Finlite aktual.
- Pilih satu skenario pilot dengan kriteria keberhasilan terukur.

## Tahap 1 — Workspace MVP mandiri (usulan prioritas)

- Anggota organisasi dan akses pegawai per orang.
- Kode anggaran sendiri, pengajuan RAB + approval + lampiran.
- Pengecekan dan reservasi anggaran di dalam Workspace.
- Pencairan/uang muka dan LPJ, dicatat di Workspace tanpa memerlukan Accounting.
- Dashboard serapan dan outstanding serta audit trail.

## Tahap 1b — Jembatan Workspace dan Accounting

- Pemetaan kode anggaran ke akun.
- Pesan pencairan dan realisasi dengan idempotency serta antrean rekonsiliasi.

## Tahap 2 — POS (opsi berikutnya)

Kasir, shift, closing, retur, perangkat melalui Device Bridge (online-only, dokumen 06), serta sinkronisasi opsional ke Sales/Inventory bila Accounting dimiliki organisasi yang sama.

## Tahap 3 — WMS (opsi berikutnya)

Lokasi/bin, inbound/outbound, picking, transfer, opname, reconciliation stok.

## Tahap 4 — CRM (opsi berikutnya)

Leads, pipeline, account/contact, activity, customer service, integrasi ke Sales.

**Urutan bukan janji waktu atau roadmap yang sudah disetujui.** Evaluasi ulang setelah pilot dan estimasi engineering.

## Keputusan terbuka

1. Workspace: lisensi per organisasi, per active employee, atau paket unit?
2. ~~Shared login/SSO~~ — **diputuskan 2026-11-01:** satu akun orang (Finlite ID) untuk semua produk. Yang masih terbuka: satu orang di beberapa organisasi.
3. Hierarki yayasan → sekolah → departemen: apakah setiap unit sama dengan satu company berpembukuan sendiri, atau hanya bagian organisasi di Workspace? (masih terbuka; lihat dokumen 07)
4. Sumber pagu bila Workspace dan Accounting tersambung: Workspace atau modul Budget? (Workspace mandiri memakai kode anggaran sendiri.)
5. Approval: per role, posisi, nominal, kategori, atau kombinasi?
6. Apakah pengajuan membuat reservasi saat submitted atau approved?
7. Apa definisi actual untuk pengeluaran uang muka, AP, dan transaksi yang belum posted?
8. ~~Apakah POS harus offline-first?~~ — **diputuskan 2026-10-30:** online-only (dokumen 06).
9. Apakah WMS harus mendukung barcode, batch/lot, expiry, serial?
10. Kapan CRM benar-benar diperlukan dibanding portal internal?

## Definisi siap dibangun

Sebuah fitur baru boleh masuk implementasi setelah ada: pemilik domain, user story, permission matrix, diagram status, kontrak API/event, aturan akuntansi, migrasi data, skenario gagal/retry, dan acceptance test.
