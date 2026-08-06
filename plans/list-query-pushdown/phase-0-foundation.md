# Fase 0 — Fondasi: trait + kontrak dua-bentuk + index tanggal

**Endpoint diubah: 0.** Fase ini hanya menyiapkan perkakas. Setelah selesai,
aplikasi harus berperilaku **persis sama** seperti sebelumnya.

## Prasyarat

Verifikasi repo ada di titik awal yang benar:

```bash
cd /workspace/laravel_backend
test -f app/Shared/Api/ResolvesAdjacentRecords.php && echo "OK: pola trait ada"
test ! -f app/Shared/Api/AppliesListQuery.php && echo "OK: fase 0 belum dikerjakan"
rtk grep -c "LengthAwarePaginator" app/Shared/Api/ApiResponse.php   # harus 0
```

## Tugas

### 0.1 — Trait `AppliesListQuery`

Buat `app/Shared/Api/AppliesListQuery.php`. Dipakai oleh **service**, bukan controller.

Kontrak minimum:

```php
protected array  $listSearchable = [];            // kolom sendiri
protected array  $listSearchableRelations = [];   // ['customer' => ['name']]
protected string $listDateColumn = '';
protected string $listStatusColumn = 'status';
protected array  $listDefaultSort = ['id' => 'desc'];
protected array  $listSortable = [];              // kolom yang boleh disort klien

protected function applyListQuery(Builder $query, array $filters): LengthAwarePaginator
```

Yang dikerjakan `applyListQuery`, berurutan:

1. **search** — bila `$filters['search']` tidak kosong: bungkus dalam satu
   `where(function ($q) { ... })` supaya `OR`-nya tidak bocor ke kondisi lain.
   `orWhere(col, 'like', "%term%")` untuk tiap `$listSearchable`, lalu
   `orWhereHas(rel, fn)` untuk tiap relasi.
2. **status** — `$filters['status']`; dukung comma-separated (`draft,posted`)
   lewat `whereIn`. Kolomnya dari `$listStatusColumn`.
3. **rentang tanggal** — `date_from`/`start_date` dan `date_to`/`end_date`
   (dua-duanya harus diterima; frontend memakai `date_from`/`date_to`,
   `listResponse` lama juga menerima `start_date`/`end_date`).
   Terapkan ke `$listDateColumn`. **Putuskan dan catat** perlakuan `NULL`
   (lihat `00-conventions.md` §3 poin 2).
4. **sort** — `sort_by`/`sort` + `sort_direction`/`direction`. **Wajib
   divalidasi terhadap `$listSortable`**; kolom di luar daftar diabaikan dan
   jatuh ke `$listDefaultSort`. Jangan pernah memasukkan input mentah ke
   `orderBy` (injeksi kolom).
5. **paginate** — `per_page` di-clamp `max(1, min(100, ...))` persis seperti
   `listResponse` sekarang; `page` `max(1, ...)`. Kembalikan `->paginate()`.

Beri PHPDoc yang menjelaskan **kenapa** trait ini ada (biaya O(n) sebelumnya),
mengikuti gaya `ResolvesAdjacentRecords`.

### 0.2 — `listResponse` menerima paginator

Di `app/Shared/Api/ApiResponse.php`, tambahkan cabang di awal `listResponse`:

- Bila `$items instanceof LengthAwarePaginator` → petakan langsung ke bentuk
  response, **tanpa** memanggil `applyListSearch/Status/DateRange/Sort/slice`.
- Selain itu → jalur lama, **tidak diubah sama sekali**.

Cabang `if (! $request->hasAny(['page', 'per_page']))` di baris paling atas
tetap dipertahankan apa adanya.

Pemetaan paginator → response:

```php
'data'         => $paginator->items(),
'current_page' => $paginator->currentPage(),
'per_page'     => $paginator->perPage(),
'total'        => $paginator->total(),
'last_page'    => $paginator->lastPage(),
'from'         => $paginator->firstItem(),   // null saat kosong
'to'           => $paginator->lastItem(),    // null saat kosong
```

> `firstItem()`/`lastItem()` sudah mengembalikan `null` saat halaman kosong —
> sesuai perilaku lama. Uji ini secara eksplisit.

### 0.3 — Migrasi index tanggal

Buat satu migrasi tenant di `database/migrations/tenant/`, penamaan mengikuti
konvensi yang ada (`YYYY_MM_DD_NNNNNN_*.php`).

Tambahkan index untuk 16 kolom yang tercatat di `00-conventions.md` §5, plus
index `status` pada `purchase_requests`. Pakai pola `Schema::hasColumn` +
pengecekan index seperti migrasi `2026_08_02_000001_add_payment_term_to_orders_table.php`
supaya idempoten.

Sertakan `down()` yang membuang index-index itu.

> Ingat: migrasi tenant **tidak** ikut `php artisan migrate`. Jalankan
> `php artisan tenant:migrate --all`, dan catat itu di commit message —
> deploy yang lupa akan menghasilkan sort lambat tanpa error apa pun.

### 0.4 — Test trait

`tests/Feature/Shared/AppliesListQueryTest.php`. Uji lewat satu modul yang
murah di-setup (ikuti `tests/Feature/MasterData/MasterDataTestCase.php`):

- search cocok di kolom terdaftar, **tidak** cocok di kolom tak terdaftar
- `OR` pencarian tidak bocor: `search=X&status=Y` tetap menghormati status
- status comma-separated
- rentang tanggal inklusif di kedua ujung
- `sort_by` di luar `$listSortable` diabaikan → jatuh ke default
- `per_page` di-clamp ke 100
- halaman kosong → `from`/`to` `null`, `total` benar

## Checklist Verifikasi

- [ ] `php artisan test tests/Feature/Shared/AppliesListQueryTest.php` hijau
- [ ] `php artisan test` **seluruhnya** hijau — belum ada service yang dipindah,
      jadi tidak boleh ada satu pun perilaku berubah
- [ ] `./vendor/bin/pint --test` pada file yang diubah hijau
- [ ] `php artisan tenant:migrate --all` sukses untuk semua tenant
- [ ] Index benar-benar terbentuk:
      `php -r '$d=new PDO("sqlite:database/tenants/company_000001.sqlite"); foreach($d->query("PRAGMA index_list(sales_invoices)") as $i) echo $i["name"],"\n";'`
- [ ] Baseline response direkam untuk Fase 1 (`00-conventions.md` §7)

## Git Checkpoint

```
feat(shared): add AppliesListQuery trait and paginator-aware listResponse

Fondasi untuk memindahkan search/filter/sort/paginate dari memori PHP ke query
builder. Belum ada endpoint yang dipindah — perilaku aplikasi tidak berubah.

listResponse kini menerima LengthAwarePaginator (langsung dipetakan) selain
Collection (jalur lama in-memory), sehingga modul bisa dipindah satu per satu.

Menambah index pada 16 kolom tanggal yang dipakai sort default modul transaksi;
tanpa ini pushdown justru memicu full scan. Jalankan `tenant:migrate --all`.
```

## Setelah selesai

Update ledger `README.md`: Fase 0 → `✅ Selesai` + hash commit.

**Sebelum lanjut ke Fase 1:** pastikan daftar kolom pencarian di
`00-conventions.md` §4 sudah disetujui pemilik produk. Fase 1 adalah titik di
mana perubahan perilaku pertama kali terlihat pengguna.
