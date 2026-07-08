# Fase 7 — Buku Besar: Pisah Ringkasan/Rincian + Jurnal per Modul

**Prioritas:** B (design-I2 §7 "Buku Besar: pisah ringkasan vs rincian, tambah jurnal per modul"; §3.1)
**Estimasi:** sedang–besar — bisa butuh sedikit backend + frontend.

## Tujuan

Menutup gap terbesar design-I2 §3.1 (Buku Besar, 15 dari 17 belum ada). Fokus item berdampak tinggi:
- **Buku Besar - Rincian** (saat ini ringkasan+rincian tergabung di `/reports/general-ledger`).
- **Semua Jurnal / Jurnal Transaksi** — daftar semua entri jurnal per periode.
- **Jurnal Penjualan / Jurnal Pembelian / Jurnal Umum** — jurnal difilter per sumber/modul.

## Prasyarat

- Fase 0 ✅.
- Baca `00-conventions.md` §1–3, §8.
- Cek endpoint jurnal existing: `route:list | grep -Ei 'journal'`. Modul **Journal** (`app/Modules/Journal/`). Cek apakah ada endpoint list journal entries dengan filter periode + source_type/source_module.
- Cek `AccountLedgerPage` + endpoint `/reports/account-ledger/{account}` — ini sudah "buku besar rincian per akun". Klarifikasi gap: yang belum = **rincian semua akun sekaligus** dan **daftar jurnal**.

## Daftar tugas

### T7.1 — Buku Besar Rincian (semua akun)
Keputusan: `/reports/general-ledger` saat ini = ringkasan per akun. "Rincian" = daftar baris jurnal per akun.
- [ ] Cek apakah backend GL bisa mengembalikan mode rincian (param `mode=detail`). Jika perlu, tambah dukungan `mode` di `GeneralLedgerQueryService` + FormRequest (backend kecil). Bila tidak, arahkan user ke `AccountLedgerPage` per akun dan tandai "rincian semua akun" sebagai `comingSoon` dengan alasan.
- [ ] Frontend: bila mode rincian didukung, tambah toggle di `GeneralLedgerPage` (Ringkasan/Rincian) atau halaman terpisah `GeneralLedgerDetailPage`. Adapter menormalkan lines.

### T7.2 — Semua Jurnal / Jurnal Transaksi — `GET /reports/journals` (atau reuse `/journals`)
- [ ] Bila endpoint list journal entries sudah ada & bisa difilter periode → buat halaman `JournalListReportPage` (read-only) yang konsumsi endpoint itu via adapter. Kolom: no jurnal, tanggal, deskripsi, total debit, total kredit, sumber.
- [ ] Bila belum ada endpoint yang cocok, tambah `GET /reports/journals` di modul Reports (service query journal_entries + lines, filter periode + source_type opsional). FormRequest + controller + route + feature test.
- [ ] Route frontend `/reports/journals`; katalog kategori `gl`.

### T7.3 — Jurnal Penjualan / Pembelian / Umum
- [ ] Reuse endpoint T7.2 dengan filter `source_type` (mis. sales_invoice → Jurnal Penjualan, vendor_bill → Jurnal Pembelian, manual → Jurnal Umum). Bisa satu halaman dengan filter, ATAU 3 entri katalog yang pre-set filter.
- [ ] Default: **satu halaman `JournalListReportPage` dengan filter sumber**, 3 entri katalog `gl` yang membuka halaman itu dengan query param sumber berbeda (mis. `/reports/journals?source=sales`). Halaman baca query param → set filter awal.

### T7.4 — Katalog & struktur
- [ ] Tambah entri kategori `gl`: "Buku Besar - Rincian" (bila didukung), "Semua Jurnal", "Jurnal Penjualan", "Jurnal Pembelian", "Jurnal Umum".
- [ ] `struktur_frontend.md` daftarkan page baru.

## Peta File

> Sebagian kondisional — tergantung apakah endpoint jurnal existing sudah memadai. Cek Prasyarat dulu.

**➕ Tambah — Backend** *(kondisional: bila belum ada endpoint journal list yang cocok)*
- `laravel_backend/app/Modules/Reports/Services/JournalListReportService.php`
- `laravel_backend/app/Modules/Reports/Requests/JournalListReportRequest.php`
- `laravel_backend/app/Modules/Reports/Controllers/JournalListReportController.php`
- `laravel_backend/tests/Feature/Reports/JournalListReportTest.php`

**➕ Tambah — Frontend**
- `react_frontend/src/modules/reports/pages/JournalListReportPage.tsx` — daftar jurnal + filter sumber (baca query param `?source=`).
- `react_frontend/src/modules/reports/pages/GeneralLedgerDetailPage.tsx` — **(kondisional: bila memilih halaman terpisah, bukan toggle di GL existing)**.

**✏️ Ubah — Backend** *(kondisional)*
- `laravel_backend/app/Modules/Reports/Services/GeneralLedgerQueryService.php` — dukung `mode=detail` (T7.1).
- `laravel_backend/app/Modules/Reports/Requests/GeneralLedgerRequest.php` — validasi `mode`.
- `laravel_backend/app/Modules/Reports/Routes/api.php` — route `/reports/journals` bila endpoint baru.

**✏️ Ubah — Frontend**
- `react_frontend/src/modules/reports/types/reports.types.ts` — `JournalListReport` (+ mode detail GL bila ada).
- `react_frontend/src/modules/reports/services/reportsApi.ts` — adapter journal list (+ GL detail).
- `react_frontend/src/modules/reports/pages/GeneralLedgerPage.tsx` — **(kondisional)** toggle Ringkasan/Rincian bila tidak pakai halaman terpisah.
- `react_frontend/src/modules/reports/routes.tsx` — `/reports/journals` (+ detail bila terpisah).
- `react_frontend/src/modules/reports/constants/reportCategories.ts` — kategori `gl`: entri Rincian, Semua Jurnal, Jurnal Penjualan/Pembelian/Umum.
- `react_frontend/docs/struktur_frontend.md` — daftarkan page baru.

**🗑️ Hapus** — Tidak ada.

## Checklist Verifikasi

- [ ] `npm run build` 0 error, `npm run lint` 0 error.
- [ ] Bila backend diubah: `php artisan test --filter=Journal` (atau nama test baru) hijau; `pint --test` hijau; route count naik.
- [ ] Runtime company 2: daftar jurnal render, total debit=kredit per jurnal; filter sumber mempersempit hasil dengan benar.

## Git Checkpoint

- Commit backend (bila ada): `feat(reports): journal list report endpoint + GL detail mode (phase 7)`.
- Commit frontend: `feat(reports): GL detail & journal reports (phase 7)`.
- Update ledger Fase 7 → ✅.
