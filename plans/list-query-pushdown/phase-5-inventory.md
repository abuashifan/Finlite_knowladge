# Fase 5 — Persediaan (3 endpoint)

## Prasyarat

```bash
cd /workspace/laravel_backend
rtk grep -rl "AppliesListQuery" app/Modules/CashBank/Services/ | wc -l   # harus 4
```

## Cakupan

| Service | Kolom sendiri | Kolom tanggal | Index tanggal |
|---|---|---|---|
| `StockMovementService` | `movement_number`, `description` | `movement_date` | ✅ sudah ada |
| `StockAdjustmentService` | `adjustment_number` | `adjustment_date` | ✅ sudah ada |
| `StockOpnameService` | `opname_number` | `opname_date` | ✅ sudah ada |

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

## Setelah selesai

Update ledger `README.md`: Fase 5 → `✅ Selesai` + hash commit.
