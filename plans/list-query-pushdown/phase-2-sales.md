# Fase 2 — Sales (8 endpoint)

> **✅ Selesai 2026-08-06 — commit `3d44803`.** Catatan hasil ada di
> [§Hasil](#hasil) di bawah; baca itu sebelum mengerjakan Fase 4–6, karena dua
> asumsi di rencana awal ternyata keliru.

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
> `notes`, `internal_notes` tetap privat).
>
> ⚠️ Kalimat berikutnya di draf awal — *"filter customer sudah dikirim dan
> dipakai backend hari ini, tidak perlu disentuh"* — **salah**, lihat §Hasil.

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

**`SalesInvoiceService`** — ~~punya filter `due_from`/`due_to`~~. **Tidak ada.**
`rtk grep -rn "due_from\|due_to" app/` nihil di seluruh backend; ini dugaan yang
tidak pernah diverifikasi saat menyusun rencana. `due_date` tetap dimasukkan ke
`$listSortable` karena kolomnya ada dan wajar diurut, tapi tidak ada filter
jatuh tempo yang perlu dijaga.

**`SalesOrderService`** — response melewati adapter `toSalesOrder()` di frontend
yang memetakan `order_number` → `number`. Pastikan field mentah tetap dikirim
apa adanya; jangan "membantu" merapikan di backend.

**`CustomerDepositService`** dan **`SalesReceiptService`** — cek apakah
`list()`-nya menghitung sesuatu setelah `->get()` (mis. sisa alokasi). **Sudah
dicek: tidak ada.** Kedelapan `list()` Sales murni query + `->get()`, tidak ada
agregat pasca-fetch, jadi tidak perlu jalur `$paginator->getCollection()`.

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

## Hasil

Selesai 2026-08-06, commit `3d44803`. Kedelapan service memakai
`AppliesListQuery`; tidak ada `->get()` tersisa di `list()` mana pun.

**Dua asumsi rencana yang ternyata salah** — periksa hal yang sama di Fase 4–6
sebelum menulis "sudah bekerja" tentang modul yang belum dibaca:

1. **`customer_id` diabaikan 7 dari 8 service.** Hanya `SalesQuotationService`
   yang memfilternya, padahal kedelapan halaman frontend mengirimkannya sejak
   awal. Dropdown filter Customer di 7 halaman diam-diam tidak berpengaruh —
   tidak error, tidak kosong, cuma tidak menyaring. Bug diam seperti ini tidak
   akan pernah muncul dari membaca frontend saja; ketahuan karena kedelapan
   `list()` dibaca satu per satu. Sudah diseragamkan.
2. **`due_from`/`due_to` tidak pernah ada** (lihat §Perhatian khusus).

**Pemanggil `list()` di luar controller: tidak ada** untuk kedelapan service
(`rtk grep -rn "\->list("` — semuanya lewat `listResponse` di controller
masing-masing). Jadi tidak perlu `listAllForReport()` terpisah seperti yang
diantisipasi Fase 1 §1.2. `SourceDocumentPickerController` memang memanggil
`->list()`, tapi ke `SourceDocumentPickerService` — bukan salah satu dari
kedelapan ini.

**Tidak ada exclusion status default** di modul Sales (tidak seperti `void` di
Jurnal), jadi jebakan `00-conventions.md` §3 item 4 tidak berlaku di sini.

**Test**: `tests/Feature/Sales/SalesListQueryTest.php` — 9 skenario × 8 modul =
72 test lewat satu data provider. Sengaja tiap endpoint benar-benar dipanggil,
bukan satu jadi perwakilan: properti trait yang lupa dideklarasikan baru meledak
saat runtime ("Typed property must not be accessed before initialization"), jadi
kalau cuma satu modul yang dites, tujuh sisanya bisa lolos rusak.

**Yang belum bisa dilakukan**: perbandingan baseline-vs-sesudah lewat `curl`
(§7) tidak dijalankan — tidak ada dev server hidup saat fase ini dikerjakan.
Kontrak yang sama dikunci lewat test sebagai gantinya:
`test_pagination_shape_is_unchanged` memeriksa ketujuh key paginasi plus
`from`/`to` = `null` di halaman kosong, dan
`test_without_page_params_returns_unpaginated_list` menjaga cabang tanpa
`page`/`per_page`.

## Setelah selesai

- [x] Update ledger `README.md`: Fase 2 → `✅ Selesai` + hash commit.
