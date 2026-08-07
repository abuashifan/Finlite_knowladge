# Fase 5 — Persediaan (3 endpoint)

> **✅ Selesai 2026-08-07 — commit `9749b35`.** Lihat [§Hasil](#hasil).

## Prasyarat

```bash
cd /workspace/laravel_backend
rtk grep -rl "AppliesListQuery" app/Modules/CashBank/Services/ | wc -l   # harus 4
```

## Cakupan

| Service | Kolom sendiri | Kolom tanggal | Index tanggal |
|---|---|---|---|
| `StockMovementService` | `movement_number`, `source_number`, `description` | `movement_date` | ✅ sudah ada |
| `StockAdjustmentService` | `adjustment_number`, `reason` | `adjustment_date` | ✅ sudah ada |
| `StockOpnameService` | `opname_number` | `opname_date` | ✅ sudah ada |

> ⚠️ Kolom pertama dan kedua diperluas saat pengerjaan agar cocok dengan
> **placeholder** tiap halaman — `00-conventions.md` §4 hanya menyebut
> `movement_number` + `description` dan `adjustment_number`. Lihat §Hasil.

## Tugas

Ikuti pola Fase 1 untuk tiap service.

### Perhatian khusus

**`StockMovementService`** — punya filter `movement_type` di samping `status`.
Filter itu tetap tinggal di `list()` (tabelnya punya index `movement_type`).
Jangan gabungkan ke `$listStatusColumn`.

**Mutasi stok punya index unik komposit** `source_type + source_id + movement_type`.
Jangan menambah `orderBy` yang bertabrakan dengan asumsi keunikan itu; urutan
default tetap `movement_date desc, id desc`.

**Pencarian lewat produk/gudang.** Daftar mutasi & penyesuaian menampilkan
produk dan gudang per baris, tapi itu ada di tabel **baris**, bukan header.
Mencarinya berarti `whereHas('lines.product', ...)` — subquery bersarang yang
mahal dan mudah menghasilkan duplikat. **Jangan** ditambahkan tanpa permintaan
eksplisit; kalau diminta, buat fase tersendiri dengan pengukuran.

## Checklist Verifikasi

- [ ] Perbandingan baseline vs sesudah untuk tiap dari 3 endpoint
- [ ] `php artisan test tests/Feature/Inventory` hijau
- [ ] `./vendor/bin/pint --test <file diubah>` hijau
- [ ] Frontend tidak diubah; `npm run build` hijau

## Git Checkpoint

```
perf(inventory): push list query into SQL for 3 endpoints
```

## Hasil

Selesai 2026-08-07, commit `9749b35`. Cek mekanis `->get()` tersisa: bersih.

**Modul paling maju dari semua fase.** Tidak seperti Sales/Purchase/Kas & Bank,
ketiga service ini **sudah** memfilter status comma-separated dan rentang
tanggal di SQL sebelum fase ini, dan ketiga halaman frontend-nya **sudah**
mengirim `status`/`date_from`/`date_to` ke server — jadi masalah `FILTER_HINT`
di `00-conventions.md` §8 tidak berlaku di sini. Yang benar-benar pindah:
pencarian, sort, paginasi.

Konsekuensinya untuk `plans/list-filters-frontend/`: **tiga halaman Persediaan
tidak masuk scope Pola C**, karena tidak pernah rusak. Yang tersisa di sana
sekarang 9 halaman minus Persediaan — verifikasi ulang daftarnya sebelum mulai.

**Daftar kolom §4 tidak cocok dengan placeholder — placeholder yang menang.**
§4 sendiri menyatakan prinsipnya "tepati apa yang dijanjikan placeholder,
karena itulah kontrak yang sudah dilihat pengguna", tapi daftarnya untuk modul
ini ditulis lebih sempit dari janji UI:

| Halaman | Placeholder | §4 | Dipakai |
|---|---|---|---|
| Mutasi Stok | "Nomor, sumber..." | nomor + `description` | nomor + `source_number` + `description` |
| Penyesuaian Stok | "Nomor, alasan..." | nomor | nomor + `reason` |
| Opname Stok | "Nomor opname..." | nomor | nomor ✅ cocok |

`source_number` di Mutasi Stok adalah **kebalikan** dari keputusan Fase 1:
di sana `JournalListQueryTest` justru menguji `source_number` **tidak** dicari.
Bukan inkonsistensi — placeholder Jurnal berbunyi "Cari nomor jurnal atau
deskripsi...", memang tidak menjanjikan sumber. Aturannya satu, hasilnya beda
karena janjinya beda. Kedua test itu saling merujuk supaya tidak ada yang
"menyeragamkan" salah satunya nanti.

**Yang tetap tinggal di service**: `movement_type` (tidak digabung ke
`$listStatusColumn`), `warehouse_id` — dan perhatikan mutasi stok memakai
`orWhereHas('lines', ...)`, bukan kolom header saja, karena gudang bisa berbeda
per baris — serta `product_id`. Ketiganya dikunci test.

**`withCount('lines')`** di `StockAdjustment` dan `StockOpname` ikut jalan lewat
`->paginate()`; ada test yang memeriksa `lines_count` masih terkirim, karena
inilah satu-satunya modul yang memakainya.

**Blok `date_from`/`date_to` manual dihapus** dari ketiga service — trait sudah
mengerjakannya. Efek sampingnya alias `start_date`/`end_date` ikut diterima,
konsisten dengan modul lain.

**Tidak ditambahkan** (sesuai §Perhatian khusus): pencarian lewat produk/gudang
di tabel baris. Butuh `whereHas('lines.product', ...)` bersarang — mahal dan
mudah menghasilkan duplikat. Kalau diminta, buat fase tersendiri dengan
pengukuran.

**Test**: `tests/Feature/Inventory/InventoryListQueryTest.php` — 32 test, 2 skip
(kolom teks kedua untuk Opname, `withCount` untuk Mutasi). Suite penuh 1034
hijau.

## Setelah selesai

- [x] Update ledger `README.md`: Fase 5 → `✅ Selesai` + hash commit.
