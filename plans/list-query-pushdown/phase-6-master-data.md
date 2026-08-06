# Fase 6 — Master Data (9 endpoint)

## Prasyarat

```bash
cd /workspace/laravel_backend
rtk grep -rl "AppliesListQuery" app/Modules/Inventory/Services/ | wc -l   # harus 3
```

## Cakupan

| Service | Kolom pencarian | Kolom status |
|---|---|---|
| `ChartOfAccountService` | `account_code`, `account_name` | `is_active` |
| `ContactService` | `contact_code`, `name`, `email`, `phone` | `is_active` |
| `ProductService` | `product_code`, `product_name` | `is_active` |
| `UnitService` | `code`, `name` | `is_active` |
| `WarehouseService` | `code`, `name` | `is_active` |
| `DepartmentService` | `code`, `name` | `is_active` |
| `ProjectService` | `code`, `name` | `is_active` |
| `PaymentTermService` | `name` | `is_active` |
| `ProductCategoryService` | `name` | `is_active` |

## Perbedaan penting dari modul transaksi

**1. Status memakai `is_active` (boolean), bukan `status` (string).**

Jalur in-memory lama menormalkan boolean → `'active'`/`'inactive'`
(lihat `applyListStatus` di `ApiResponse.php`). Perilaku itu **wajib
dipertahankan**: `?status=active` harus tetap menyaring `is_active = true`.

Set `$listStatusColumn = 'is_active'` dan tangani pemetaan nilainya di trait,
atau override method status di service ini. Pilih satu pendekatan dan pakai
konsisten di 9 service.

**2. Tidak ada kolom tanggal dokumen.**

Filter periode praktis tidak berlaku. Set `$listDateColumn = ''` (atau
`created_at` bila daftar memang menyediakan filter tanggal di UI — **cek dulu
halaman daftarnya**, jangan berasumsi).

**3. Urutan default bukan tanggal.**

- COA: `account_code asc`
- Produk: `product_name asc`
- Kontak: `name asc`
- Sisanya: `name asc` atau `code asc` — **verifikasi dengan urutan yang
  ditampilkan halaman daftar sekarang**, jangan diubah diam-diam.

> Ini penting karena navigasi Prev/Next form sengaja memakai urutan `id`
> (urutan input), **bukan** urutan daftar. Kedua urutan itu memang berbeda dan
> harus tetap berbeda. Jangan "menyelaraskan" keduanya.

**4. Beberapa `list()` menghitung agregat.**

`ProductService::list()` diketahui menyertakan `current_stock` teragregasi
(ada test: `test_product_list_includes_aggregated_current_stock_quantity`).
Agregat itu **tidak boleh** hilang. Jalankan atas `$paginator->getCollection()`
bila perlu, dan pastikan test tersebut tetap hijau.

## Tugas

Ikuti pola Fase 1 untuk tiap service, dengan penyesuaian di atas.

Cari pemanggil `list()` di luar controller — master data banyak dipakai
lintas modul (picker, laporan, ekspor):

```bash
rtk grep -rn "ProductService->list\|ContactService->list\|ChartOfAccountService->list" app/ tests/
```

Ini modul dengan risiko pemanggil-lain tertinggi. Periksa satu per satu.

## Checklist Verifikasi

- [ ] Perbandingan baseline vs sesudah untuk tiap dari 9 endpoint
- [ ] `php artisan test tests/Feature/MasterData` hijau — termasuk
      `test_product_list_includes_aggregated_current_stock_quantity`
- [ ] `php artisan test` **seluruhnya** hijau (master data dipakai lintas modul)
- [ ] `./vendor/bin/pint --test <file diubah>` hijau
- [ ] Frontend tidak diubah; `npm run build` hijau
- [ ] Uji manual: COA & Produk — cari kode, cari nama, filter Aktif/Nonaktif,
      dan **pastikan urutan daftar tidak berubah**

## Git Checkpoint

```
perf(master-data): push list query into SQL for 9 endpoints

Filter status master data memakai is_active (boolean); pemetaan
?status=active|inactive dipertahankan persis seperti jalur in-memory lama.
Urutan tampil tiap daftar tidak berubah.
```

## Setelah selesai

Update ledger `README.md`: Fase 6 → `✅ Selesai` + hash commit.
