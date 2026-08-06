# Fase 2 — Sales (8 endpoint)

## Prasyarat

```bash
cd /workspace/laravel_backend
rtk grep -c "AppliesListQuery" app/Modules/Journal/Services/JournalEntryService.php  # harus > 0
```

⚠️ Fase 1 harus sudah **dinilai pemilik produk**, bukan sekadar selesai teknis.
Fase ini menyalin pola yang sama ke 8 endpoint sekaligus.

## Cakupan

| Service | Kolom sendiri | Relasi | Kolom tanggal |
|---|---|---|---|
| `SalesQuotationService` | `quotation_number` | customer | `quotation_date` |
| `SalesOrderService` | `order_number`, `customer_po_number` | customer | `order_date` |
| `ProformaInvoiceService` | `proforma_number` | customer | `proforma_date` |
| `DeliveryOrderService` | `delivery_number` | customer | `delivery_date` |
| `SalesInvoiceService` | `invoice_number`, `notes` | customer | `invoice_date` |
| `SalesReturnService` | `return_number` | customer | `return_date` |
| `CustomerDepositService` | `deposit_number` | customer | `deposit_date` |
| `SalesReceiptService` | `receipt_number` | customer | `receipt_date` |

Relasi customer dicari lewat `['name', 'contact_code']`.

> **SalesInvoiceService** (AR) — `notes` ditambahkan setelah dikonfirmasi
> 2026-08-06: modul AR cukup dicari lewat nomor + catatan; tabel tidak punya
> kolom `description` (hanya `notes`/`internal_notes` — yang disertakan cuma
> `notes`, `internal_notes` tetap privat). Filter customer **sudah** dikirim
> dan dipakai backend hari ini (`customer_id` di query) — bukan bagian yang
> rusak, tidak perlu disentuh fase ini.

## Tugas

Untuk **tiap** service di atas, ikuti pola Fase 1:

1. `use AppliesListQuery` + deklarasikan properti (`$listSearchable`,
   `$listSearchableRelations`, `$listDateColumn`, `$listDefaultSort`,
   `$listSortable`).
2. Pertahankan filter khusus modul (`customer_id`, `due_from`/`due_to`, dsb)
   di dalam `list()` sebelum memanggil `applyListQuery()`.
3. Ubah tipe balik ke `LengthAwarePaginator`.
4. Cari pemanggil `list()` di luar controller (`rtk grep -rn "Service->list("`);
   tangani seperti Fase 1 §1.2.

### Perhatian khusus

**`SalesInvoiceService`** — punya filter `due_from`/`due_to` di samping
`date_from`/`date_to`. Keduanya harus tetap bekerja bersamaan. `due_date` tidak
ber-index; kalau daftar invoice sering difilter jatuh tempo, tambahkan index
`due_date` di fase ini.

**`SalesOrderService`** — response melewati adapter `toSalesOrder()` di frontend
yang memetakan `order_number` → `number`. Pastikan field mentah tetap dikirim
apa adanya; jangan "membantu" merapikan di backend.

**`CustomerDepositService`** dan **`SalesReceiptService`** — cek apakah
`list()`-nya menghitung sesuatu setelah `->get()` (mis. sisa alokasi). Kalau ya,
perhitungan itu **tidak boleh** dipindah ke SQL secara terburu-buru; biarkan
berjalan atas `$paginator->getCollection()` supaya hasilnya identik.

## Checklist Verifikasi

- [ ] Perbandingan baseline vs sesudah untuk **tiap** dari 8 endpoint,
      minimal kombinasi: tanpa filter, `search=`, `status=`, rentang tanggal
- [ ] `php artisan test tests/Feature/Sales` hijau
- [ ] `php artisan test tests/Feature/Reports` hijau
- [ ] `./vendor/bin/pint --test <file diubah>` hijau
- [ ] Frontend tidak diubah; `npm run build` hijau
- [ ] Uji manual: daftar Invoice → cari nomor invoice, cari nama customer,
      filter status, filter periode, ganti halaman

## Git Checkpoint

```
perf(sales): push list query into SQL for 8 endpoints

Pola sama dengan Fase 1 (commit <hash-fase-1>). Pencarian kini dibatasi ke
nomor dokumen + nama/kode customer; sebelumnya memindai seluruh field.
```

## Setelah selesai

Update ledger `README.md`: Fase 2 → `✅ Selesai` + hash commit.
