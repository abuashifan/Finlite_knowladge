# Fase 3 — Purchase (7 endpoint)

## Prasyarat

```bash
cd /workspace/laravel_backend
rtk grep -rl "AppliesListQuery" app/Modules/Sales/Services/ | wc -l   # harus 8
```

## Cakupan

| Service | Kolom sendiri | Relasi | Kolom tanggal |
|---|---|---|---|
| `PurchaseRequestService` | `request_number` | — | `request_date` |
| `PurchaseOrderService` | `order_number`, `vendor_quote_number` | vendor | `order_date` |
| `GoodsReceiptService` | `receipt_number` | vendor | `receipt_date` |
| `VendorBillService` | `bill_number`, `vendor_invoice_number`, `notes` | vendor | `bill_date` |
| `PurchaseReturnService` | `return_number` | vendor | `return_date` |
| `VendorDepositService` | `deposit_number` | vendor | `deposit_date` |
| `VendorPaymentService` | `payment_number` | vendor | `payment_date` |

Relasi vendor dicari lewat `['name', 'contact_code']`.

> **VendorBillService** (AP) — `notes` ditambahkan setelah dikonfirmasi
> 2026-08-06, simetris dengan `SalesInvoiceService` di Fase 2 (lihat catatan
> di sana). Filter vendor sudah bekerja server-side hari ini, tidak perlu
> disentuh fase ini.

## Tugas

Ikuti pola Fase 1 untuk tiap service. Lihat `phase-2-sales.md` §Tugas untuk
langkah detailnya — identik.

### Perhatian khusus

**`PurchaseRequestService`** — tabelnya **belum punya index `status`**
(satu-satunya modul transaksi yang begitu). Index ini seharusnya sudah
ditambahkan di Fase 0; verifikasi ada sebelum mulai:

```bash
php -r '$d=new PDO("sqlite:database/tenants/company_000001.sqlite");
foreach($d->query("PRAGMA index_list(purchase_requests)") as $i) echo $i["name"],"\n";'
```

**`VendorBillService`** — tercatat punya perhitungan sisa/alokasi deposit
(`withAvailableDepositSummary` atau sejenisnya di `find()`). Cek apakah `list()`
juga melakukannya. Bila ya, jalankan atas `$paginator->getCollection()`, jangan
dipaksa ke SQL di fase ini.

**`VendorPaymentService`** — punya relasi ke `vendor_bill`; kalau daftar
menampilkan nomor tagihan, pertimbangkan menambahkannya ke
`$listSearchableRelations` (`vendorBill` → `bill_number`). Konfirmasi dulu ke
pemilik produk sebelum menambah di luar daftar `00-conventions.md` §4.

## Checklist Verifikasi

- [ ] Perbandingan baseline vs sesudah untuk tiap dari 7 endpoint
- [ ] `php artisan test tests/Feature/Purchase` hijau
- [ ] `php artisan test tests/Feature/Reports` hijau
- [ ] `./vendor/bin/pint --test <file diubah>` hijau
- [ ] Frontend tidak diubah; `npm run build` hijau

## Git Checkpoint

```
perf(purchase): push list query into SQL for 7 endpoints
```

## Setelah selesai

Update ledger `README.md`: Fase 3 → `✅ Selesai` + hash commit.
