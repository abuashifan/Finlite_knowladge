# Fase 4 — Kas & Bank (4 endpoint)

## Prasyarat

```bash
cd /workspace/laravel_backend
rtk grep -rl "AppliesListQuery" app/Modules/Purchase/Services/ | wc -l   # harus 7
```

## Cakupan

| Service | Kolom sendiri | Kolom tanggal | Index tanggal |
|---|---|---|---|
| `CashReceiptService` | `receipt_number`, `description` | `receipt_date` | ✅ sudah ada |
| `CashPaymentService` | `payment_number`, `description` | `payment_date` | ✅ sudah ada |
| `BankTransferService` | `transfer_number`, `notes` | `transfer_date` | ✅ sudah ada |
| `BankReconciliationService` | `reconciliation_number` | `created_at` | ❌ ditambah Fase 0 |

Tidak ada pencarian lewat relasi di modul ini.

## Tugas

Ikuti pola Fase 1 untuk tiap service.

### Perhatian khusus

**`BankReconciliationService`** — kolom tanggalnya `created_at`, bukan kolom
tanggal dokumen. Cek dulu apakah tabel punya kolom tanggal periode
(`statement_date`, `period_end`, atau sejenis) yang lebih tepat untuk filter:

```bash
php -r '$d=new PDO("sqlite:database/tenants/company_000001.sqlite");
foreach($d->query("PRAGMA table_info(bank_reconciliations)") as $c) echo $c["name"],"\n";'
```

Kalau ada, itu yang dipakai sebagai `$listDateColumn` — dan index Fase 0 perlu
disesuaikan. Catat temuannya.

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

## Setelah selesai

Update ledger `README.md`: Fase 4 → `✅ Selesai` + hash commit.
