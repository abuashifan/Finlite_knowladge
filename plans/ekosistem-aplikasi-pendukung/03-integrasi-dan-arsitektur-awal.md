# Arsitektur dan Integrasi — Hipotesis Awal

**Status: rancangan eksploratif, belum keputusan teknis.**

## Pola awal

Satu backend Laravel modular dapat menjadi titik awal bila audit kode membuktikan cocok; frontend aplikasi dapat dipisah berdasarkan persona (Accounting, POS, WMS, Workspace, CRM). Jangan mengunci microservice sebelum ada kebutuhan skala/deployment yang nyata.

## Kepemilikan domain

| Domain | Kandidat system of record |
| --- | --- |
| GL, COA, jurnal, periode, saldo, pembayaran | Finlite Accounting |
| Master barang, persediaan akuntansi, valuation | Finlite ERP/Inventory |
| Shift kasir, cart, receipt kasir | POS |
| Bin, picking, packing, stock count fisik | WMS |
| Proposal, approval, RAB, LPJ, tugas proyek | Workspace |
| Lead, opportunity, aktivitas pelanggan | CRM |
| Identitas, organisasi, departemen, keanggotaan | Shared identity/organization domain (desain perlu validasi) |

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
4. Sinkronisasi offline POS dapat menyebabkan transaksi duplikat atau stok negatif.
5. WMS harus membedakan kuantitas fisik, reserved stock, dan valuation akuntansi.
6. Data pegawai dan lampiran membutuhkan kebijakan privasi, retention, dan akses.

## Audit sebelum implementasi

Periksa kode aktual Laravel/React: Budget module, Organization/company model, permission & auth, transaction policy, inventory, API response contracts, event/outbox, dan skema tenant. Dokumentasi historis saja tidak cukup untuk menyimpulkan readiness.
