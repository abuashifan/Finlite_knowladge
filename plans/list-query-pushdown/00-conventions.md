# Konvensi — List Query Pushdown

> Wajib dibaca sebelum mengerjakan fase mana pun. Berisi pola kode, kontrak
> response, daftar kolom pencarian, dan definition-of-done.

## 1. Bentuk akhir yang dituju

**Sebelum** (semua baris ke memori, lalu dipotong):

```php
// Controller
return $this->listResponse($this->service->list($request->query()), $request, '...');

// Service
public function list(array $filters = []): Collection
{
    $query = SalesInvoice::query()->with('customer', 'paymentTerm');
    if (! empty($filters['status'])) { $query->where('status', (string) $filters['status']); }

    return $query->orderByDesc('invoice_date')->orderByDesc('id')->get();
}
```

**Sesudah** (semua kerja di SQL, satu halaman keluar):

```php
// Controller — TIDAK BERUBAH
return $this->listResponse($this->service->list($request->query()), $request, '...');

// Service
use App\Shared\Api\AppliesListQuery;

class SalesInvoiceService
{
    use AppliesListQuery;

    /** Kolom yang boleh dicari lewat kotak pencarian. Lihat 00-conventions §4. */
    protected array $listSearchable = ['invoice_number'];

    /** Relasi + kolomnya yang ikut dicari. */
    protected array $listSearchableRelations = ['customer' => ['name', 'contact_code']];

    protected string $listDateColumn = 'invoice_date';

    /** @var array<int,string> Urutan default bila `sort_by` tidak dikirim. */
    protected array $listDefaultSort = ['invoice_date' => 'desc', 'id' => 'desc'];

    /** @return LengthAwarePaginator|Collection<int,SalesInvoice> */
    public function list(array $filters = []): LengthAwarePaginator|Collection
    {
        $query = SalesInvoice::query()->with('customer', 'paymentTerm');

        // Filter khusus modul tetap di sini.
        if (! empty($filters['customer_id'])) {
            $query->where('customer_id', (int) $filters['customer_id']);
        }

        return $this->applyListQuery($query, $filters);
    }
}
```

`applyListQuery()` mengerjakan search, status, rentang tanggal, sort — semua
di SQL — lalu memutuskan `->paginate()` atau `->get()` (lihat ⚠️ di bawah).

> ⚠️ **Wajib deklarasikan SEMUA properti, termasuk yang nilainya sama di semua
> modul** (mis. `$listStatusColumn = 'status'`). Trait `AppliesListQuery`
> sengaja **tidak** memberi nilai default apa pun — PHP menolak kalau trait dan
> kelas pemakai mendeklarasikan properti bertipe sama dengan default berbeda
> (fatal error: *"definition differs and is considered incompatible"*),
> bahkan kalau trait-nya sendiri tidak punya default. Diverifikasi Fase 0
> lewat reproduksi minimal — lihat `tests/Feature/Shared/AppliesListQueryTest.php`.
> Kalau satu properti lupa dideklarasikan, errornya baru muncul saat runtime
> ("Typed property must not be accessed before initialization"), bukan saat
> menulis kode — jadi jangan copy-paste sebagian dari service lain.

> ⚠️ **`applyListQuery()` mengembalikan `LengthAwarePaginator` ATAU
> `Collection`, tergantung `$filters`.** Ditemukan di Fase 1 lewat 2 test yang
> gagal (`JournalEntryTest::test_journal_index_hides_void_by_default`,
> `JournalVoidTest::test_void_journal_not_visible_in_index_by_default`) —
> keduanya memanggil `/api/journals` **tanpa** `page`/`per_page`, mengandalkan
> kontrak lama "tidak ada page/per_page = kirim semua tanpa paginasi"
> (§2 di bawah). Draft awal trait ini selalu memanggil `->paginate()` apa pun
> isi `$filters`, sehingga `listResponse`'s early-return branch menerima objek
> `LengthAwarePaginator` mentah alih-alih array — Laravel men-JSON-kan objek
> itu dengan ~13 key metanya sendiri (`current_page`, `data`, `links`, ...),
> bukan daftar record. Perbaikannya: `applyListQuery()` mengecek
> `array_key_exists('page', $filters) || array_key_exists('per_page', $filters)`
> — kalau tidak ada satupun, `->get()` (Collection, konsisten dengan
> `listResponse`'s `$request->hasAny(['page','per_page'])`); kalau ada,
> `->paginate()`. **Tipe balik `list()` di tiap service wajib union**
> (`LengthAwarePaginator|Collection`), bukan `LengthAwarePaginator` saja.

## 2. Kontrak `listResponse` selama transisi

`listResponse` harus menerima **dua bentuk**:

| Masukan | Perlakuan |
|---|---|
| `LengthAwarePaginator` | Sudah terfilter & terpaginasi di SQL — langsung dipetakan ke bentuk response. **Tidak boleh** difilter ulang. |
| `Collection` | Jalur lama: filter in-memory + `slice` seperti sekarang — tapi kalau `Collection` ini datang dari `applyListQuery()` (bukan `->get()` mentah tanpa filter), search/status/tanggal/sort-nya **sudah** benar dari SQL; filter in-memory di atasnya jadi no-op, bukan re-filter yang salah. |

Cabang "tanpa `page`/`per_page` → kirim semua" (`$request->hasAny([...])`)
**wajib dipertahankan** — dipakai beberapa pemanggil internal, dan **wajib
disimetriskan** dengan pengecekan yang sama persis di `applyListQuery()`
(lihat ⚠️ di atas) supaya kedua sisi sepakat kapan paginasi terjadi.

Bentuk response **wajib identik** dengan sekarang:

```json
{ "data": [...], "current_page": 1, "per_page": 25, "total": 33,
  "last_page": 2, "from": 1, "to": 25 }
```

`from`/`to` bernilai `null` saat `total === 0`. Uji ini di tiap fase.

## 3. Perilaku lama yang harus disadari (dan diputuskan)

Tiga perilaku jalur in-memory yang **tidak** akan terbawa apa adanya:

1. **Pencarian memindai semua field.** `listItemValues()` mengubah record jadi
   array lalu mencocokkan substring ke setiap nilai skalar — termasuk `id`,
   `metadata`, `notes`, semua kolom tanggal. Setelah pushdown, hanya kolom di
   `$listSearchable` (+ relasi) yang dicari.
2. **Filter tanggal melewatkan record tanpa kolom tanggal dikenal.**
   `applyListDateRange` mengembalikan `true` bila `listDateValue()` kosong —
   record itu lolos filter periode apa pun. Setelah pushdown, `whereBetween`
   pada `$listDateColumn` akan **mengecualikan** baris `NULL`.
   → Untuk modul yang kolom tanggalnya nullable, putuskan eksplisit:
   `orWhereNull` atau memang dikecualikan. Catat keputusannya di file fase.
3. **Filter status berhenti di kunci pertama.** `applyListStatus` melakukan
   `return` di dalam loop `['status','state','is_active']`, jadi tidak bisa
   jatuh ke kunci berikutnya. Setelah pushdown, tiap service menyebut kolomnya
   sendiri (`status` untuk transaksi, `is_active` untuk master data).

Perbedaan **1** terlihat pengguna → butuh persetujuan (§4).
Perbedaan **2** dan **3** adalah perbaikan bug; catat di commit message.

## 4. Kolom pencarian per modul

### Apa yang sebenarnya dicari sekarang (diukur 2026-08-06)

Pada daftar Invoice, kotak pencarian mencocokkan **50 field skalar** — termasuk
`id`, `grand_total`, `paid_amount`, `created_at`, `internal_notes`, `metadata`,
dan semua kolom `*_id`. Bukti empiris pada data demo (6 invoice):

| Ketik | Hasil | Sebab |
|---|---|---|
| `SI-2026` | 4 | benar — cocok `invoice_number` |
| `2026` | 6 (semua) | cocok kolom tanggal |
| `16000` | 4 | cocok `grand_total` |
| `posted` | 3 | cocok kolom `status` |
| `Warung` | **0** | ← relasi tidak pernah dicocokkan |

**Temuan penting: pencarian lewat nama customer/vendor TIDAK berfungsi hari ini.**
`applyListSearch` hanya mencocokkan nilai `is_scalar()`; relasi ter-eager-load
muncul sebagai array bersarang di `toArray()` sehingga selalu dilewati.

Padahal placeholder di UI menjanjikan sebaliknya — mis. `"Cari nomor invoice,
customer..."` di 14 halaman Sales & Purchase. Janji itu tidak ditepati.

### Konsekuensinya untuk rencana ini

Pushdown **bukan** pengurangan cakupan pencarian, melainkan perbaikan:

- Yang hilang: pencocokan ke field yang memang tidak seharusnya dicari
  (id, nominal, timestamp, `internal_notes`, `metadata`).
- Yang bertambah: pencarian relasi mulai bekerja lewat `whereHas` — menepati
  janji placeholder yang selama ini bohong.

Karena itu risiko "pengguna kehilangan sesuatu" jauh lebih kecil dari dugaan
awal. Tetap konfirmasikan daftar di bawah, tapi ini bukan lagi keputusan berat.

### Daftar kolom — ✅ DIKONFIRMASI 2026-08-06

Prinsipnya: **tepati apa yang dijanjikan placeholder**, karena itulah kontrak
yang sudah dilihat pengguna. Placeholder aktual per halaman ada di
`*ListPage.tsx` (`<ListSearchBar placeholder=...>`). Tabel lengkap per modul
ada di tiap file fase (`phase-N-*.md`); prinsip di atas berlaku ke semuanya.

**Keputusan filter AP/AR** (Vendor Bill = AP, Sales Invoice = AR — dua-duanya
punya istilah status "Lunas/Belum Lunas/Belum Dibayar" yang sama):

- Filter = nama lawan transaksi (customer/vendor) + rentang tanggal **dokumen**
  (`invoice_date`/`bill_date`), **bukan** filter akun GL terpisah.
- Filter customer/vendor **sudah bekerja** hari ini — dikirim sebagai
  `customer_id`/`vendor_id` dan sudah dipakai service. Bukan bagian yang rusak.
- Tanggal dokumen, bukan `created_at` — konsisten dengan `$listDateColumn` yang
  sudah dipilih tiap fase sejak awal. Tidak ada perubahan desain di sini.
- Search satu kotak gabungan, kolom dibatasi (bukan field terpisah per kolom
  seperti nomor faktur/nomor PO dua kotak beda) — konsisten dengan
  `$listSearchable` yang sudah dirancang. Tidak ada perubahan desain di sini.

**Yang tidak disentuh rencana ini** (lihat §8): filter status & tanggal yang
sekarang cuma berlaku ke 1 halaman karena frontend tidak mengirimnya ke
server. Backend menyiapkan; perbaikan frontend-nya ada di
`plans/list-filters-frontend/README.md`.

### Transaksi

| Modul | Kolom sendiri | Lewat relasi |
|---|---|---|
| Jurnal Umum | `journal_number`, `description` | — |
| Quotation | `quotation_number` | customer: `name`, `contact_code` |
| Sales Order | `order_number`, `customer_po_number` | customer: `name`, `contact_code` |
| Proforma | `proforma_number` | customer: `name`, `contact_code` |
| Delivery Order | `delivery_number` | customer: `name`, `contact_code` |
| Invoice Penjualan | `invoice_number` | customer: `name`, `contact_code` |
| Retur Penjualan | `return_number` | customer: `name`, `contact_code` |
| Deposit Customer | `deposit_number` | customer: `name`, `contact_code` |
| Penerimaan Penjualan | `receipt_number` | customer: `name`, `contact_code` |
| Purchase Request | `request_number` | — |
| Purchase Order | `order_number`, `vendor_quote_number` | vendor: `name`, `contact_code` |
| Penerimaan Barang | `receipt_number` | vendor: `name`, `contact_code` |
| Tagihan Vendor | `bill_number`, `vendor_invoice_number` | vendor: `name`, `contact_code` |
| Retur Pembelian | `return_number` | vendor: `name`, `contact_code` |
| Deposit Vendor | `deposit_number` | vendor: `name`, `contact_code` |
| Pembayaran Vendor | `payment_number` | vendor: `name`, `contact_code` |
| Penerimaan Kas | `receipt_number`, `description` | — |
| Pengeluaran Kas | `payment_number`, `description` | — |
| Transfer Bank | `transfer_number`, `notes` | — |
| Rekonsiliasi Bank | `reconciliation_number` | — |
| Mutasi Stok | `movement_number`, `description` | — |
| Penyesuaian Stok | `adjustment_number` | — |
| Opname Stok | `opname_number` | — |

### Master Data

| Modul | Kolom |
|---|---|
| Akun (COA) | `account_code`, `account_name` |
| Kontak | `contact_code`, `name`, `email`, `phone` |
| Produk | `product_code`, `product_name` |
| Satuan | `code`, `name` |
| Gudang | `code`, `name` |
| Departemen | `code`, `name` |
| Proyek | `code`, `name` |
| Syarat Bayar | `name` |
| Kategori Produk | `name` |

**Catatan:** pencarian lewat relasi memakai `whereHas`, yang menjadi subquery.
Pastikan kolom relasi yang dicari ber-index (`contacts.name`, `contacts.contact_code`).
Bila belum, tambahkan di migrasi Fase 0.

## 5. Index yang dibutuhkan

Audit 2026-08-06 pada `company_000001.sqlite`. **15 tabel belum punya index pada
kolom tanggal utamanya** — ini wajib ditambal di Fase 0, karena sort default
seluruh modul transaksi memakai kolom itu.

Sudah punya index tanggal: `cash_receipts`, `cash_payments`, `bank_transfers`,
`stock_movements`, `stock_adjustments`, `stock_opnames`, `journal_entries`.

Belum punya (perlu migrasi):

```
sales_quotations.quotation_date      purchase_requests.request_date
sales_orders.order_date              purchase_orders.order_date
proforma_invoices.proforma_date      goods_receipts.receipt_date
delivery_orders.delivery_date        vendor_bills.bill_date
sales_invoices.invoice_date          purchase_returns.return_date
sales_returns.return_date            vendor_deposits.deposit_date
customer_deposits.deposit_date       vendor_payments.payment_date
sales_receipts.receipt_date          bank_reconciliations.created_at
```

`purchase_requests` juga belum punya index `status`.

> `sales_invoices` punya komposit `customer_id,invoice_date`, tapi kolom
> pertamanya `customer_id` — tidak terpakai untuk sort tanggal saja. Tetap perlu
> index `invoice_date` berdiri sendiri.

## 6. Definition of Done per fase

Sebuah fase selesai bila **semua** ini terpenuhi:

- [ ] Service modul mengembalikan `LengthAwarePaginator`, bukan `Collection`
- [ ] Tidak ada `->get()` tersisa di `list()` modul itu
- [ ] Controller **tidak berubah**
- [ ] Bentuk response identik — dibuktikan dengan tes perbandingan (§7)
- [ ] `php artisan test tests/Feature/{Modul}` hijau
- [ ] `./vendor/bin/pint --test <file yang diubah>` hijau
- [ ] Frontend **tidak diubah sama sekali**; `npm run build` tetap hijau
- [ ] Ledger di `README.md` diperbarui + commit

## 7. Cara membuktikan response tidak berubah

Sebelum mengubah service, rekam baseline:

```bash
TOK=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@example.com","password":"password"}' \
  | python3 -c 'import sys,json;print(json.load(sys.stdin)["data"]["token"])')

curl -s "http://localhost:8000/api/journals?page=1&per_page=25" \
  -H "Authorization: Bearer $TOK" -H 'X-Company-Id: 1' > /tmp/before.json
```

Sesudah diubah, ambil `/tmp/after.json` dengan perintah sama lalu:

```bash
python3 -c "
import json
a=json.load(open('/tmp/before.json')); b=json.load(open('/tmp/after.json'))
for k in ['current_page','per_page','total','last_page','from','to']:
    assert a['data'][k]==b['data'][k], (k, a['data'][k], b['data'][k])
ida=[r['id'] for r in a['data']['data']]; idb=[r['id'] for r in b['data']['data']]
assert ida==idb, ('urutan berubah', ida[:5], idb[:5])
print('identik:', len(ida), 'baris')
"
```

Ulangi untuk kombinasi: tanpa filter, `search=`, `status=`, rentang tanggal,
`sort_by=` + `sort_direction=`, halaman terakhir, dan halaman kosong
(`page=999` → `from`/`to` harus `null`).

## 8. Di luar scope — pekerjaan terpisah

Saat menyusun rencana ini ditemukan **masalah berbeda** yang tidak diselesaikan
di sini. Jangan dicampur; catat di sini supaya tidak hilang.

**Filter status & tanggal hanya berlaku pada halaman yang sedang tampil.**
Frontend tidak mengirim `status`/`date_from`/`date_to` ke server sama sekali —
ia menyaring 25 baris hasil di browser:

```ts
// SalesInvoiceListPage.tsx
const { data } = useSalesInvoiceList({ page, per_page: 25, search, customer_id })
const visibleRows = rows.filter((invoice) => {
  const matchesStatus = filterStatuses.length === 0 || filterStatuses.includes(invoice.status)
  const matchesDate = isDateInRange(invoice.date, dateRange.from, dateRange.to)
  return matchesStatus && matchesDate
})
```

Tercatat jujur di UI sebagai `FILTER_HINT` — *"Filter multi-select dan tanggal
berlaku pada data halaman yang sedang dimuat."* — muncul di **9 halaman daftar**.

Akibatnya: mencentang "Posted" tidak menampilkan dokumen posted di halaman lain.

**Kenapa terpisah:** pushdown backend memperbaiki **beban**, dan itu selesai
tanpa menyentuh frontend. Memperbaiki **cakupan filter** butuh frontend mulai
mengirim parameternya — perubahan UI tersendiri, dengan desain filter/search
per-field (referensi: panel Pencarian/Pelanggan/Tanggal/Status bergaya Accurate
yang diberikan pemilik produk).

Urutannya benar: backend dulu (rencana ini), baru frontend menyusul. Setelah
Fase 2 & 3 selesai, backend sudah **siap** menerima `status`/tanggal — frontend
tinggal mengirimnya.

## 9. Yang TIDAK boleh dilakukan

- ❌ Mengubah bentuk response atau nama field — frontend bergantung padanya
- ❌ Menambah `->limit()` sebagai peredam tanpa paginasi jujur
- ❌ Menyentuh `/{resource}/adjacent` — sudah efisien, di luar scope
- ❌ Merapikan modul lain "sekalian" — lihat `laravel_backend/AGENTS.md`:
  *"Do not refactor unrelated modules unless the task explicitly requires it"*
- ❌ Menghapus jalur `Collection` di `listResponse` sebelum Fase 7
