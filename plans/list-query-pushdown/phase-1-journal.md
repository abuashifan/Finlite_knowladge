# Fase 1 — Pilot: Jurnal Umum

**Endpoint: 1** (`GET /api/journals`).

Dipilih sebagai pilot karena datanya paling banyak di sistem (33 record saat
audit, terbanyak dibanding modul lain), index `journal_date` + `status` sudah
ada sejak awal, dan tidak punya relasi yang ikut dicari — jadi perubahan
perilaku pencariannya paling mudah dinilai.

## Prasyarat

```bash
cd /workspace/laravel_backend
test -f app/Shared/Api/AppliesListQuery.php && echo "OK: Fase 0 selesai"
rtk grep -c "LengthAwarePaginator" app/Shared/Api/ApiResponse.php   # harus > 0
rtk grep -n "return \$query" app/Modules/Journal/Services/JournalEntryService.php
# ^ harus masih ->get()
```

⚠️ **Jangan mulai** sebelum daftar kolom pencarian di `00-conventions.md` §4
disetujui pemilik produk. Fase ini yang pertama mengubah perilaku terlihat.

## Konteks modul

`JournalEntryService::list()` saat ini (lihat file untuk versi terkini):

```php
public function list(array $filters = []): Collection
{
    $query = JournalEntry::query();

    $includeVoid = filter_var($filters['include_void'] ?? false, FILTER_VALIDATE_BOOLEAN);
    if (! $includeVoid) { $query->where('status', '!=', 'void'); }

    $includeObsolete = filter_var($filters['include_obsolete'] ?? false, FILTER_VALIDATE_BOOLEAN);
    if (! $includeObsolete) { $query->where('is_obsolete', false); }
    // ... lalu ->get()
}
```

Dua filter khusus ini (`include_void`, `include_obsolete`) **tetap tinggal di
service** — hanya search/status/tanggal/sort/paginate yang pindah ke trait.

⚠️ **Interaksi `status` — INI BUG, BUKAN PERILAKU YANG DIPERTAHANKAN.**
Draf awal rencana ini menganggap "status=void selalu kosong tanpa
include_void" sebagai perilaku lama yang harus dipertahankan apa adanya.
**Salah** — ditemukan dari laporan user nyata (2026-08-06): void satu jurnal
lewat UI, filter status "Void" di sidebar, jurnalnya tidak muncul. Root
cause: `where('status', '!=', 'void')` diterapkan tanpa syarat, lalu
`AppliesListQuery` menambah `whereIn('status', ['void'])` di atasnya —
kontradiksi SQL yang selalu 0 baris. UI tidak pernah mengirim
`include_void=true`, cuma `status=void`.

**Perbaikan yang benar**: exclusion default HANYA berlaku saat tidak ada
filter status sama sekali (`empty($filters['status'])`). Begitu user
memfilter status secara eksplisit — apa pun nilainya, termasuk `void` —
filter itu yang menang. Lihat implementasi final di
`JournalEntryService::list()` dan test
`test_status_void_filter_works_without_include_void_flag`.

**Untuk fase 2-6**: cek tiap modul apakah punya pola serupa (kolom status
yang disembunyikan default kecuali flag khusus — mis. `cancelled`,
`obsolete`, dokumen yang di-void/dibatalkan). Kalau ada, terapkan aturan
yang sama: exclusion default hanya jalan saat filter status kosong.

## Tugas

### 1.1 — Pindahkan service

Di `app/Modules/Journal/Services/JournalEntryService.php`:

```php
use App\Shared\Api\AppliesListQuery;

class JournalEntryService
{
    use AppliesListQuery;

    protected array $listSearchable = ['journal_number', 'description'];
    protected string $listDateColumn = 'journal_date';
    protected string $listStatusColumn = 'status';
    protected array $listDefaultSort = ['journal_date' => 'desc', 'id' => 'desc'];
    protected array $listSortable = ['journal_number', 'journal_date', 'status', 'created_at'];
```

Ubah `list()` agar mengembalikan `LengthAwarePaginator` lewat
`$this->applyListQuery($query, $filters)`. Pertahankan `include_void` dan
`include_obsolete` sebelum pemanggilan itu.

Sesuaikan tipe balik di signature dan PHPDoc.

### 1.2 — Cek pemanggil lain `list()`

**Penting.** `list()` mungkin dipanggil bukan hanya oleh controller:

```bash
rtk grep -rn "journalEntryService->list\|JournalEntryService.*->list(" app/ tests/
```

Kalau ada pemanggil yang mengharapkan `Collection` (mis. laporan atau ekspor),
**jangan** paksa mereka ikut berubah. Pilihan:
- pemanggil itu memakai `->getCollection()` dari paginator, **atau**
- tambahkan method terpisah `listAllForReport()` yang tetap `->get()`.

Catat pilihan yang diambil di commit message.

### 1.3 — Kolom `journal_date` nullable?

Cek: `PRAGMA table_info(journal_entries)`. Bila `journal_date` boleh `NULL`,
putuskan apakah baris `NULL` ikut tersaring keluar oleh filter periode
(perilaku SQL) atau tetap disertakan (perilaku in-memory lama). Catat
keputusannya di file ini dan di commit message.

### 1.4 — Test

`tests/Feature/Journal/JournalListQueryTest.php`:

- pencarian menemukan lewat `journal_number`
- pencarian menemukan lewat `description`
- pencarian **tidak** lagi menemukan lewat kolom lain (mis. `source_number`) —
  kunci perubahan perilaku ini secara eksplisit supaya regresi ketahuan
- `status=posted` menyaring benar
- `include_void=true` + `status=void` berperilaku sama seperti sebelum perubahan
- rentang tanggal inklusif
- `sort_by=journal_number&sort_direction=asc` berlaku
- `sort_by=kolom_ngawur` diabaikan → urutan default
- paginasi: `total` benar, halaman terakhir benar, `page=999` → `from`/`to` null

## Checklist Verifikasi

- [ ] Perbandingan baseline vs sesudah (`00-conventions.md` §7) untuk kombinasi:
      tanpa filter, `search=`, `status=`, rentang tanggal, `sort_by=`,
      halaman terakhir, `page=999`
- [ ] `php artisan test tests/Feature/Journal` hijau
- [ ] `php artisan test tests/Feature/Reports` hijau — laporan sering memakai
      service jurnal; ini area risiko utama fase ini
- [ ] `./vendor/bin/pint --test <file diubah>` hijau
- [ ] Frontend tidak diubah; `npm run build` hijau
- [ ] Bukti pushdown: minta `per_page=1` harus **lebih murah** dari tanpa
      paginasi. Rekam ulang tabel waktu seperti di `README.md`

## Git Checkpoint

```
perf(journal): push list search/filter/sort/paginate into SQL

Endpoint daftar jurnal tidak lagi memuat seluruh tabel ke memori untuk
memotong satu halaman. Search dibatasi ke journal_number dan description
(sebelumnya memindai semua field termasuk id dan tanggal, sehingga mengetik
angka bisa memunculkan dokumen tak terduga).

include_void dan include_obsolete tetap di service; hanya search/status/
tanggal/sort/paginate yang pindah ke AppliesListQuery.

Bentuk response tidak berubah — diverifikasi dengan perbandingan baseline
untuk 7 kombinasi filter.
```

## Setelah selesai

1. Update ledger `README.md`: Fase 1 → `✅ Selesai` + hash commit.
2. **Minta pemilik produk mencoba kotak pencarian Jurnal Umum** sebelum Fase 2.
   Ini gerbang keputusan: kalau cakupan pencarian barunya terasa kurang,
   perbaiki daftar kolom di `00-conventions.md` §4 **sekarang** — sebelum pola
   yang sama disalin ke 31 endpoint lain.
