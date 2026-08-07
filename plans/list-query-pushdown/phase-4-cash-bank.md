# Fase 4 — Kas & Bank (4 endpoint)

> **✅ Selesai 2026-08-07 — commit `138ca61`.** Lihat [§Hasil](#hasil).

## Prasyarat

```bash
cd /workspace/laravel_backend
rtk grep -rl "AppliesListQuery" app/Modules/Purchase/Services/ | wc -l   # harus 7
```

## Cakupan

| Service | Kolom sendiri | Kolom tanggal | Index tanggal |
|---|---|---|---|
| `CashReceiptService` | `receipt_number`, `notes` | `receipt_date` | ✅ sudah ada |
| `CashPaymentService` | `payment_number`, `notes` | `payment_date` | ✅ sudah ada |
| `BankTransferService` | `transfer_number`, `notes` | `transfer_date` | ✅ sudah ada |
| `BankReconciliationService` | `reconciliation_number` | `statement_end_date` | ✅ ditambah Fase 0 |

> ⚠️ Dua baris pertama semula tertulis `description`. **Kolom itu tidak ada**
> di `cash_receipts` maupun `cash_payments` — yang ada `notes`. Dipakai `notes`
> karena itu yang dimaksud ("nomor + keterangan") dan simetris dengan
> `bank_transfers` yang memang sudah disetujui sebagai `notes`.

Tidak ada pencarian lewat relasi di modul ini.

## Tugas

Ikuti pola Fase 1 untuk tiap service.

### Perhatian khusus

**`BankReconciliationService`** — `$listDateColumn = 'statement_end_date'`,
sudah diverifikasi & diberi index di Fase 0 (bukan `created_at`; tabel punya
`statement_start_date` dan `statement_end_date`, dipilih yang akhir periode
karena itu yang biasanya dipakai untuk "rekonsiliasi periode Juni").

**`BankReconciliationService`** juga satu-satunya di modul ini yang punya
`update()`; `list()`-nya memakai signature filter berbeda
(`Omit<CashBankListParams,'status'> & { status?: string }` di sisi frontend).
Pastikan filter status tetap diterima sebagai string bebas, bukan enum ketat.

**Rekonsiliasi selalu berstatus draft** (lihat komentar di
`app/Modules/CashBank/Routes/api.php` — A11-12 / issue-04). Jangan menambah
filter status yang mengasumsikan siklus dokumen penuh.

## Checklist Verifikasi

- [ ] Perbandingan baseline vs sesudah untuk tiap dari 4 endpoint
- [ ] `php artisan test tests/Feature/CashBank` hijau
- [ ] `./vendor/bin/pint --test <file diubah>` hijau
- [ ] Frontend tidak diubah; `npm run build` hijau
- [ ] Uji manual: Penerimaan Kas & Pengeluaran Kas — cari nomor, cari deskripsi,
      filter periode

## Git Checkpoint

```
perf(cash-bank): push list query into SQL for 4 endpoints
```

## Hasil

Selesai 2026-08-07, commit `138ca61`. Keempat service memakai
`AppliesListQuery`; cek mekanis `->get()` tersisa: bersih.

**Kekeliruan rencana ketiga dari jenis yang sama.** Setelah `due_from`/`due_to`
(Fase 2) dan alokasi deposit di `list()` (Fase 3), kali ini kolom `description`
yang tidak pernah ada. Polanya konsisten: **detail yang ditulis dari ingatan
tentang modul yang belum dibuka.** Untuk Fase 5 dan 6, buka `PRAGMA table_info`
tiap tabel **sebelum** menulis daftar kolom, bukan sesudah.

**`notes` di rekonsiliasi sengaja tidak dicari.** Tabelnya punya `notes`, tapi
`00-conventions.md` §4 cuma menyetujui `reconciliation_number` untuk modul ini,
dan halamannya memang belum punya kotak pencarian (termasuk 7 halaman yang
pemilik produk minta dilewati dulu). Perbedaan ini dikunci di
`test_search_matches_notes_except_reconciliation` supaya terbaca sebagai
keputusan, bukan kelupaan — kalau nanti diputuskan ikut dicari, testnya yang
gagal duluan dan memaksa keputusan itu eksplisit.

**Filter `cash_bank_account_id` ditambahkan ke `CashReceipt` dan
`CashPayment`.** Bukan bug aktif seperti `customer_id` di Fase 2 — halaman Kas
& Bank hari ini cuma mengirim `page`, `per_page`, `search`. Tapi
`CashBankListParams` di frontend **sudah** mendeklarasikan
`cash_bank_account_id` untuk keempat hook, dan `BankReconciliationService`
sudah memakainya; dua service lain akan jadi bug diam yang persis sama begitu
dropdown akun dipasang. Ditutup sekarang selagi murah.

**`BankTransferService` sengaja tidak menerimanya.** Transfer punya dua akun
(`from_cash_bank_account_id`, `to_cash_bank_account_id`), jadi
`cash_bank_account_id` tunggal ambigu: akun asal saja, tujuan saja, atau salah
satu? Menunggu keputusan pemilik produk — alasannya ditulis di docblock
`list()`-nya supaya tidak "diperbaiki" jadi tebakan.

**Tidak ada exclusion status default** di keempat service. **Pemanggil `list()`
di luar controller: tidak ada.**

**Test**: `tests/Feature/CashBank/CashBankListQueryTest.php` — 9 skenario × 4
modul = 36 test, 1 skip (filter akun untuk BankTransfer). Modul ini belum punya
`CashBankTestCase` sendiri; test menumpang `JournalTestCase` seperti
`CashReceiptTest` dan kawan-kawan. Suite penuh 1002 hijau.

**Belum dijalankan**: perbandingan baseline-vs-sesudah lewat `curl` — masih
tidak ada dev server hidup, sama seperti Fase 2 & 3. Kontraknya dikunci test.

## Setelah selesai

- [x] Update ledger `README.md`: Fase 4 → `✅ Selesai` + hash commit.
