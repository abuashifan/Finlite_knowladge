# Fase 3 — Purchase (7 endpoint)

> **✅ Selesai 2026-08-06 — commit `c4a67f2`.** Lihat [§Hasil](#hasil).

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
> di sana).
>
> ⚠️ *"Filter vendor sudah bekerja server-side hari ini"* benar untuk
> `VendorBillService`, tapi **tidak untuk semua** — lihat §Hasil.

`PurchaseRequestService` tidak punya relasi vendor karena tabel
`purchase_requests` memang tidak punya kolom `vendor_id`: PR adalah dokumen
permintaan internal, vendornya baru ditentukan di PO. Filter `department_id`
dan `project_id`-nya tetap di service.

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

**`VendorBillService`** — ~~cek perhitungan sisa/alokasi deposit di `list()`~~.
**Sudah dicek: tidak ada.** Perhitungan itu memang ada, tapi di `find()`, bukan
`list()`. Ketujuh `list()` Purchase murni query + `->get()`.

**`VendorPaymentService`** — punya relasi ke `vendor_bill`; kalau daftar
menampilkan nomor tagihan, pertimbangkan menambahkannya ke
`$listSearchableRelations` (`vendorBill` → `bill_number`). **Belum ditambahkan**
— di luar daftar `00-conventions.md` §4 yang sudah disetujui, jadi menunggu
konfirmasi pemilik produk dulu.

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

## Hasil

Selesai 2026-08-06, commit `c4a67f2`. Ketujuh service memakai
`AppliesListQuery`; tidak ada `->get()` tersisa di `list()` mana pun.

**`vendor_id` diabaikan 2 dari 7 service** — `PurchaseReturnService` dan
`VendorPaymentService`. Lima lainnya (`PurchaseOrder`, `GoodsReceipt`,
`VendorBill`, `VendorDeposit`, dan `PurchaseRequest` yang memang tidak punya
kolomnya) sudah benar. Lebih baik dari Sales yang 7 dari 8 rusak, tapi tetap
tidak seragam — sudah diperbaiki.

**`VendorBillService` unik**: sebelum fase ini ia satu-satunya yang menyerahkan
filter status sepenuhnya ke `listResponse` (ada komentar eksplisit tentang itu
di kodenya), bukan memfilter di query. Sekarang seragam di SQL bersama enam
lainnya.

**Tidak ada exclusion status default** di modul Purchase, sama seperti Sales.
**Pemanggil `list()` di luar controller: tidak ada.**

**Kesalahan yang tertangkap test, bukan review**: saat memindahkan
`PurchaseRequestService`, blok `if (! empty($filters['status']))` dihapus dan
tipe baliknya diubah, tapi baris `return $query->orderByDesc(...)->get()` di
ujung method **ikut tertinggal** — service tetap mengembalikan `Collection`,
jadi `listResponse` diam-diam jatuh ke jalur in-memory lama. Tidak ada error,
tidak ada warning; satu-satunya gejala adalah `from` = `24951` alih-alih `null`
di `page=999`, yang persis diperiksa `test_pagination_shape_is_unchanged`.
Pelajaran: setelah tiap fase jalankan
`awk '/public function list\(/{p=1} p&&/->get\(\)/{print FILENAME": "NR} p&&/^    }/{p=0}'`
atas service yang diubah — pengecekan mekanis, bukan mengandalkan mata.

**Test**: `tests/Feature/Purchase/PurchaseListQueryTest.php` — 9 skenario × 7
modul = 63 test, 2 di antaranya skip (kasus vendor untuk `purchase_requests`).
Suite penuh backend 966 hijau.

**Pint**: satu temuan tersisa di `PurchaseReturnService.php`
(`unary_operator_spaces` dkk). Sudah ada sebelum fase ini — diverifikasi dengan
`git stash` lalu `pint --test` — dan tidak disentuh, sesuai `AGENTS.md`
("do not refactor unrelated modules").

## Setelah selesai

- [x] Update ledger `README.md`: Fase 3 → `✅ Selesai` + hash commit.
