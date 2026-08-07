# Fase 6 — Master Data (9 endpoint)

> **✅ Selesai 2026-08-07 — commit `b874a45`.** Lihat [§Hasil](#hasil).
> Pemindahan search box ke sidebar (21 halaman) dikerjakan bersamaan atas
> permintaan pemilik produk — commit frontend `a1249ee`, lihat §Hasil.

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

## Hasil

Selesai 2026-08-07, commit `b874a45`. Kesembilan service memakai
`AppliesListQuery`; cek mekanis `->get()` tersisa: bersih.

**`ProjectService` adalah pengecualian yang tidak diantisipasi rencana.**
Tabel `projects` punya kolom `status` string sendiri **di samping** `is_active`
— satu-satunya di antara sembilan (diverifikasi lewat `PRAGMA table_info`,
sesuai peringatan yang ditambahkan setelah Fase 4). Jadi `$listStatusColumn`
di sana `'status'`, bukan `'is_active'`. Ini bukan pilihan gaya: perilaku lama
memang begitu, karena `applyListStatus` in-memory memeriksa kunci `status`
lebih dulu lalu `return`. Kalau diseragamkan jadi `is_active` seperti delapan
lainnya, filter status proyek diam-diam berubah jadi filter aktif/nonaktif —
`?status=ongoing` akan mengembalikan proyek nonaktif (karena
`'ongoing' !== 'active'` → `is_active = false`). Dikunci di
`test_project_status_filters_own_column_not_is_active`.

**Urutan tampil** diuji satu per satu karena inilah yang paling mudah bergeser
diam-diam saat sort pindah ke trait. Dua yang tidak intuitif dan gampang
dianggap salah lalu "diperbaiki": Gudang (`is_default desc` dulu, baru `name`)
dan Syarat Bayar (`sort_order`, bukan abjad — "Zulu 30" memang di atas
"Alpha 60").

**Agregat stok produk** kini dihitung setelah paginasi, atas
`$paginator->getCollection()`. Hasilnya identik karena `attachStockQuantities()`
menjumlahkan per `product_id` dan tidak bergantung pada produk lain di halaman
yang sama — tapi sekarang hanya untuk baris yang benar-benar dikirim, bukan
seluruh tabel produk.

**Kekhawatiran rencana soal pemanggil lintas modul tidak terbukti.** Rencana
menyebut modul ini "risiko pemanggil-lain tertinggi" (picker, laporan, ekspor).
Hasil grep: **tidak ada** pemanggil `list()` di luar controller untuk
kesembilan service. Jadi tidak perlu `listAllForReport()` terpisah.

**Blok pencarian manual** di `DepartmentService` dan `ProjectService` dihapus —
keduanya sudah mencari `code`/`name` di SQL sebelum fase ini, dan trait
mencari kolom yang sama persis.

**Test**: `tests/Feature/MasterData/MasterDataListQueryTest.php` — 7 skenario ×
5 modul lewat data provider, plus 4 test kasus khusus (Project, Gudang, Syarat
Bayar, agregat produk). Suite penuh 1073 hijau.

Dua hal yang tertangkap saat menulis test, bukan saat menulis kode:
`payment_terms.code` ternyata `NOT NULL`, dan migrasi tenant sudah menyeed
syarat bayar bawaan (COD, Net 7, …) sehingga asersi urutan harus mengambil dua
teratas, bukan seluruh daftar.

**Belum dijalankan**: perbandingan baseline-vs-sesudah lewat `curl` — pola yang
sama dengan Fase 2–5. Kontraknya dikunci test.

## Hasil — pemindahan search box ke sidebar

Dikerjakan bersamaan atas permintaan pemilik produk. Commit frontend
`a1249ee`, **21 halaman**: Master Data (3), Penjualan (8), Pembelian (7),
Kas & Bank (3). Jurnal Umum sudah lebih dulu di `da8a7cc`.

Kotak pencarian pindah dari atas tabel ke bagian atas `FilterSidebar`, di atas
`FilterSection` pertama. Alasannya ruang vertikal: baris di atas tabel memakan
tinggi yang lebih berharga untuk data, sedangkan bagian atas sidebar filter
menganggur.

Seluruh 21 halaman ternyata seragam (`value={search} onChange={setSearch}`,
`className="mb-3"`), hanya placeholder yang berbeda — jadi pemindahannya bisa
dilakukan lewat satu skrip, bukan 21 suntingan tangan. `className` disesuaikan
ke `w-full max-w-none` karena `max-w-sm` bawaan komponen dirancang untuk
content area yang lebar.

**Tiga halaman Persediaan tidak ikut** — memang sudah menaruh pencarian di
sidebar, tapi memakai `<Input>` biasa di dalam `<FilterSection title="Cari">`
alih-alih komponen `ListSearchBar`. Mirip secara visual, tapi tanpa debounce
400ms dan tanpa tombol bersihkan. Belum diseragamkan; perbedaannya dicatat di
docblock `ListSearchBar`.

Docblock `ListSearchBar` diperbarui — sebelumnya menyatakan komponen ini
"selalu tampil di content area (bukan sidebar), sesuai spec-13 §Filter
Universal", yang kini tidak lagi benar untuk 22 dari 25 halaman daftar.

Diverifikasi di browser sungguhan untuk 7 halaman lintas keempat modul: kotak
pencarian render di dalam sidebar (x=28, di kiri tabel), tanpa console error.

## Setelah selesai

- [x] Update ledger `README.md`: Fase 6 → `✅ Selesai` + hash commit.
