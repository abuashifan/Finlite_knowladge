# Fase 7 — Pembersihan: buang jalur in-memory

> **✅ Selesai 2026-08-07 — commit `a72edf7`.** Lihat [§Hasil](#hasil).
> Angka penutup rencana ada di `README.md` §Hasil akhir.

**Endpoint diubah: 0.** Fase ini hanya membuang kode mati setelah 32 endpoint
pindah. Perilaku aplikasi tidak boleh berubah.

## Prasyarat

Semua fase 1–6 `✅ Selesai` di ledger, **dan** tidak ada lagi service yang
mengembalikan `Collection` ke `listResponse`:

```bash
cd /workspace/laravel_backend
# harus 32 — semua service list sudah memakai trait
rtk grep -rl "AppliesListQuery" app/Modules/*/Services/ | wc -l

# harus 0 — tidak ada lagi list() yang diakhiri ->get()
rtk grep -rn -B2 "public function list" app/Modules/*/Services/*.php | rtk grep -c "Collection"
```

Kalau salah satu tidak cocok, **berhenti** — ada modul yang terlewat. Kembali ke
ledger dan temukan mana.

## Tugas

### 7.1 — Buang helper in-memory

Di `app/Shared/Api/ApiResponse.php`, hapus:

- `applyListSearch()`
- `applyListStatus()`
- `applyListDateRange()`
- `applyListSort()`
- `listDateValue()`
- `listItemValues()`

dan cabang `Collection` di `listResponse()`.

⚠️ **Jangan hapus** cabang paling atas:

```php
if (! $request->hasAny(['page', 'per_page'])) {
    return $this->successResponse($items, $message, $status);
}
```

Cabang ini dipakai pemanggil yang memang ingin semua record tanpa paginasi.
Verifikasi dulu siapa saja yang bergantung padanya sebelum menyentuhnya:

```bash
rtk grep -rn "listResponse" app/Modules/*/Controllers/ | wc -l
```

### 7.2 — Verifikasi tidak ada pemanggil tersisa

```bash
rtk grep -rn "applyListSearch\|applyListStatus\|applyListDateRange\|applyListSort\|listItemValues\|listDateValue" app/ tests/
```

Harus kosong.

### 7.3 — Perbarui dokumentasi

- `Finlite_knowladge/reference/backend-directory-tree.md` — tambahkan
  `app/Shared/Api/AppliesListQuery.php`
- Catat di `laravel_backend/docs/` bila ada dokumen yang menjelaskan pola
  list/pagination lama

## Checklist Verifikasi

- [ ] `php artisan test` **seluruh suite** hijau
- [ ] `./vendor/bin/pint --test` pada file yang diubah hijau
- [ ] Frontend tidak diubah; `npm run build` hijau
- [ ] Ukur ulang tabel waktu di `README.md` — sekarang `per_page=1` **harus**
      jauh lebih murah daripada tanpa paginasi. Catat angkanya di README
      sebagai penutup rencana.

## Git Checkpoint

```
refactor(shared): drop in-memory list filtering from ApiResponse

Seluruh 32 endpoint daftar sudah memfilter, mengurutkan, dan memaginasi di SQL
(fase 1-6), sehingga helper in-memory di listResponse menjadi kode mati.

Cabang "tanpa page/per_page kirim semua" dipertahankan — masih dipakai
pemanggil internal.
```

## Hasil

Selesai 2026-08-07, commit `a72edf7`. `ApiResponse.php` turun **245 → 104
baris**; enam helper in-memory dihapus.

**Prasyarat diverifikasi, bukan diasumsikan.** 32 controller memanggil
`listResponse`, 32 service memakai `AppliesListQuery` — cocok. Sempat terlihat
34 pemanggilan, tapi dua di antaranya cuma penyebutan di komentar
`AppliesListQuery.php` sendiri.

**Lima service di luar 32 masih mengakhiri `list()` dengan `->get()`** —
`BudgetPeriodService`, `BudgetSubmissionService`, `FixedAssetService`,
`AccountMappingStorageService`, `OpeningBalanceBatchService`. Semuanya dicek
satu per satu: kelimanya memakai `successResponse`, **bukan** `listResponse`,
jadi tidak terpengaruh. Kalau nanti salah satunya dipindah ke `listResponse`,
ia harus ikut memakai trait dulu.

**Bentuk non-paginator kini melempar `LogicException`, bukan diam-diam jatuh
ke jalur lambat.** Ini keputusan sengaja: justru jalur cadangan itu yang
menyembunyikan masalah aslinya selama ini — service yang belum dipindah tetap
"jalan", hanya lambat, jadi tidak ada yang tahu. Sekarang kesalahan seperti itu
gagal keras di test pertama, dengan pesan yang menyebut trait mana yang kurang.

**Cabang "tanpa page/per_page kirim semua" dipertahankan** dan harus tetap
simetris dengan pengecekan yang sama di `applyListQuery()`. Kalau salah satu
sisi diubah tanpa yang lain, cabang di bawahnya menerima bentuk yang tidak
diharapkan — persis kegagalan yang muncul di Fase 1.

### 7.3 — sub-tugas yang tidak berlaku

Rencana meminta menambahkan `app/Shared/Api/AppliesListQuery.php` ke
`reference/backend-directory-tree.md`. **Tidak dilakukan**: dokumen itu
di-generate `tree -a -d` (lihat perintahnya di baris 10 dokumen) sehingga
isinya **hanya direktori**, tidak ada satu pun entri file. Menambah satu baris
file akan membuatnya tidak lagi cocok dengan perintah generatornya. Folder
`Shared/Api` sendiri sudah terdaftar, dan fase ini tidak menambah direktori
baru sehingga dokumen itu tidak perlu di-generate ulang.

Pointer ke trait-nya sudah ada di tempat yang tepat: `00-conventions.md` §1 dan
README rencana ini.

### Alat ukur

Ditambahkan `tests/Feature/Journal/ListQueryBenchmarkTest.php` — menyeed 3000
jurnal, mencatat waktu/baris/memori untuk 5 bentuk permintaan, dan memastikan
paginasi benar-benar terjadi di SQL. Laporan hanya ditulis bila `BENCHMARK_OUT`
diset supaya suite normal tidak meninggalkan file. Angkanya ada di README
rencana ini.

Catatan lingkungan: `echo`/`printf` dari phpunit tersaring RTK di sini, jadi
laporannya ditulis ke file, bukan dicetak.

## Setelah selesai

- [x] Update ledger `README.md`: Fase 7 → `✅ Selesai` + hash commit.
- [x] Tandai rencana ini **SELESAI** di `Finlite_knowladge/README.md` §Plans.
- [x] Catat angka pengukuran akhir di `README.md` rencana ini.
