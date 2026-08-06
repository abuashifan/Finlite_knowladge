# Fase 7 — Pembersihan: buang jalur in-memory

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

## Setelah selesai

1. Update ledger `README.md`: Fase 7 → `✅ Selesai` + hash commit.
2. Tandai rencana ini **SELESAI** di `Finlite_knowladge/README.md` §Plans,
   mengikuti format entri Laravel Modularization.
3. Catat angka pengukuran akhir di `README.md` rencana ini sebagai bukti hasil.
