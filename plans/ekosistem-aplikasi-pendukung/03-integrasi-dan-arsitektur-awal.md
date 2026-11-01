# Arsitektur dan Integrasi — Hipotesis Awal

**Status: rancangan eksploratif, belum keputusan teknis.**

## Pola awal

Satu backend Laravel modular dapat menjadi titik awal bila audit kode membuktikan cocok; frontend aplikasi dapat dipisah berdasarkan persona (Accounting, POS, WMS, Workspace, CRM). Jangan mengunci microservice sebelum ada kebutuhan skala/deployment yang nyata.

## Arah terbaru (2026-11-01)

Setiap produk lengkap tanpa produk lain; integrasi hanya tambahan. Backend dan database mengikuti Finlite: satu backend modular, tenant per perusahaan, dan pemilik sebagai pemegang langganan. Yang dibagi antarproduk hanya identitas (Finlite ID), keanggotaan perusahaan, dan langganan; **produk tidak berbagi tabel**, karena tenant dibuat per perusahaan per produk (satu schema per produk) saat produk diaktifkan. Rinciannya, termasuk skala tenant, ada di [07-keputusan-platform-segmen-dan-model-data.md](07-keputusan-platform-segmen-dan-model-data.md).

## Kepemilikan domain

| Domain | Kandidat system of record |
| --- | --- |
| GL, COA, jurnal, periode, saldo, pembayaran | Finlite Accounting |
| Master barang, persediaan akuntansi, valuation | Finlite ERP/Inventory |
| Shift kasir, cart, receipt kasir | POS |
| Bin, picking, packing, stock count fisik | WMS |
| Proposal, approval, RAB, LPJ, tugas proyek | Workspace |
| Lead, opportunity, aktivitas pelanggan | CRM |
| Identitas, keanggotaan perusahaan, langganan per produk | Basis data pusat Finlite (dimensi produk ditambahkan; dokumen 07) |
| Struktur departemen, jabatan, atasan/approver | Workspace (data organisasi internal produk itu sendiri) |

## Kontrak integrasi

- API versioned dan events untuk state changes penting.
- Idempotency key, correlation ID, retry, dead-letter/reconciliation queue bila async.
- Outbox pattern dipertimbangkan untuk memastikan konsistensi penerbitan event.
- Validasi tenant, company, permission, dan ownership pada sisi server.
- Audit log: actor, timestamp, before/after, alasan, sumber aplikasi.
- Jangan menulis langsung ke database tenant aplikasi lain.
- Rekonsiliasi antara dokumen sumber, transaksi Finlite, dan status integrasi.

## Integrasi contoh

- POS sale → sales transaction/payment di Finlite; retur dan shift close harus punya aturan reversal.
- WMS receipt/pick/count → inventory movement yang tervalidasi; selisih opname memerlukan approval.
- Workspace approved request → budget reservation; payment/advance di Accounting; LPJ verified → transaksi/penyelesaian resmi; actual dibaca dari financial core.
- CRM won opportunity → optional sales quotation/order, dengan mapping customer dan permission.

## Risiko arsitektur

1. Multi-unit sekolah tidak selalu sepadan dengan tenant/company.
2. Pengguna portal jauh lebih banyak daripada staf Accounting; entitlement dan SSO perlu desain khusus.
3. Budget Finlite yang sudah ada bisa tumpang tindih dengan RAB/approval Workspace.
4. POS dipastikan online-only (dokumen 06), sehingga risiko sinkronisasi offline tidak berlaku; risiko yang tersisa adalah transaksi ganda akibat pengiriman ulang antarproduk, ditangani dengan idempotency.
5. WMS harus membedakan kuantitas fisik, reserved stock, dan valuation akuntansi.
6. Data pegawai dan lampiran membutuhkan kebijakan privasi, retention, dan akses.
7. Pola tenant per schema perlu diuji bebannya untuk POS (transaksi sering) dan harus siap dipecah ke beberapa database; kode produk tidak boleh mengasumsikan semua tenant berada di satu database.
8. Langganan saat ini menempel ke pengguna pemilik tanpa dimensi produk; menambah dimensi produk pada paket, langganan, tenant, dan izin adalah perubahan fondasi yang harus selesai sebelum produk baru.

## Audit sebelum implementasi

Periksa kode aktual Laravel/React: Budget module, Organization/company model, permission & auth, transaction policy, inventory, API response contracts, event/outbox, dan skema tenant. Dokumentasi historis saja tidak cukup untuk menyimpulkan readiness.
