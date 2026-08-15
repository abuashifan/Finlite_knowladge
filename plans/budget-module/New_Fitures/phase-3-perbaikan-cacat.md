# Phase 3 — Perbaikan 4 Cacat Perilaku

> Prasyarat: fase 2 selesai.

## Objective

Mengalihkan pemakai lama ke mesin fase 2, sehingga peringatan over-budget dan laporan
perbandingan memakai logika yang **sama persis**.

Menutup **G4, G5, G6, G7, G8, G9** di sisi pemakai.

> Tidak ada logika baru di fase ini. Kalau ternyata butuh menulis logika pencocokan atau
> agregasi di sini, berarti fase 2 belum selesai — kembali ke sana.

---

## Empat cacat yang ditutup

Keempatnya tercatat di `../README.md` §"Temuan rancangan yang belum diputuskan", ditemukan
2026-08-09 dan sengaja tidak dikerjakan waktu itu karena menyentuh perilaku bisnis.

| # | Cacat | Perilaku lama | Perilaku baru |
|---|---|---|---|
| 1 | **Anggaran tahunan hampir tidak pernah memicu peringatan** | `BudgetWarningService` menjumlahkan actual **satu bulan** (`strftime('%Y-%m', je.journal_date) = ?`) tapi baris anggaran yang cocok bisa tahunan (`period IS NULL`). Anggaran gaji 240 jt/tahun baru menyala kalau satu bulan tembus 240 jt. | Baris tahunan dibandingkan dengan actual **kumulatif** `period_from` → akhir bulan transaksi (`BudgetAllocationResolver`). |
| 2 | **Transaksi bertanda proyek melewati anggaran umum** | Pencocokan asimetris: baris jurnal ber-`project_id` hanya dicocokkan ke baris anggaran berproyek sama; baris "semua proyek" (`project_id IS NULL`) tidak ikut dipertimbangkan. | Tangga spesifisitas prioritas 3–4 menangkapnya (`BudgetMatchResolver`). |
| 3 | **Baris jurnal tanpa departemen mencocok anggaran departemen mana pun** | `when($departmentId, …)` tidak memasang filter apa pun bila null, lalu `first()` mengambil baris pertama yang ketemu. | `whereNull('department_id')` eksplisit — hanya cocok dengan anggaran tingkat perusahaan. |
| 4 | **Modul dirancang untuk anggaran beban, bukan target pendapatan** | `SUM(debit − credit)` mengasumsikan akun bersaldo debit; menganggarkan akun pendapatan menghasilkan actual negatif sehingga `over_budget` tidak pernah menyala. | Tanda dibalik per `account_type` (`BudgetActualService`), dan variance pendapatan pakai `Actual − Budget` — melampaui target pendapatan adalah kabar baik, bukan pelanggaran. |

Plus catatan portabilitas terkait: `strftime()` adalah fungsi SQLite. Setelah fase ini tidak
ada lagi pemakaiannya di modul Budget.

---

## Existing files affected

### `app/Modules/Budget/Services/BudgetWarningService.php`

Isi lamanya — query mentah dengan `strftime()`, `when()`, dan `SUM(debit − credit)` —
**dihapus seluruhnya**. Diganti komposisi tiga service fase 2:

```php
public function __construct(
    private readonly BudgetMatchResolver $matchResolver,
    private readonly BudgetActualService $actualService,
    private readonly BudgetAllocationResolver $allocationResolver,
) {}
```

`check()` mempertahankan tanda tangannya supaya `JournalEntryController` tidak perlu diubah:

```php
public function check(int $companyId, int $accountId, ?int $departmentId, ?int $projectId, string $period, float $amountToPost): ?array
```

Balasan bertambah field: `state`, `direction`, `matched_scope` (menjelaskan prioritas berapa
yang cocok — berguna saat user bingung kenapa peringatannya muncul).

### `app/Modules/Journal/Controllers/JournalEntryController.php:103-115`

Pemanggilan **tetap** — hanya bentuk balasan warning yang bertambah field. Sudah terdaftar di
`ModuleBoundariesTest::KNOWN_MODULE_COUPLING` sebagai
`'Journal → App\Modules\Budget\Services\BudgetWarningService'`, tidak perlu ditambah.

---

## Database changes

Tidak ada.

## API / service changes

Bentuk `meta.warnings[]` pada `POST /journals/{id}/post` bertambah tiga field. Aditif,
tidak merusak pemanggil lama.

## Frontend changes

`frontend/src/modules/accounting/types/journalEntry.types.ts` — interface `BudgetWarning`
bertambah `state`, `direction`, `matched_scope` (opsional supaya build lama tetap jalan).
Toast di `JournalFormPage.tsx:231-234` bisa dipertajam memakai `matched_scope`, tapi itu
opsional dan boleh ditunda ke fase 7.

---

## Dependencies

Fase 2.

---

## Risks

| Risiko | Mitigasi |
|---|---|
| **Peringatan menjadi jauh lebih sering menyala** setelah cacat 1–3 diperbaiki | Itu benar secara bisnis — sebelumnya peringatan nyaris tidak pernah muncul, jadi user belum terbiasa. Peringatan tetap **non-blocking** (`meta.warnings`), tidak pernah menolak posting. **Perilaku non-blocking ini jangan diubah** — memblokir posting karena anggaran adalah keputusan bisnis tersendiri yang belum diambil. |
| Anggaran pendapatan kini bisa menyala `over_budget` | Untuk pendapatan, "melampaui" berarti target terlampaui = favorable. Pastikan UI memberi warna hijau, bukan merah. Definisinya ada di fase 2. |
| Perubahan `BudgetWarningService` merusak test lama | `BudgetFlowTest` tidak menguji warning sama sekali (tercatat di audit). Test baru harus ditulis, bukan disesuaikan. |

---

## Testing

Test baru di `tests/Feature/Budget/BudgetWarningTest.php` (extends `BudgetTestCase`):

- Anggaran tahunan 240 jt: jurnal bulan ke-9 yang membuat kumulatif jadi 250 jt **menyala**;
  jurnal bulan tunggal 20 jt **tidak** menyala
- Jurnal ber-`project_id` tanpa anggaran proyek → kena anggaran umum departemen (prioritas 3–4)
- Jurnal ber-`project_id` **dengan** anggaran proyek → kena anggaran proyek (prioritas 1–2),
  bukan yang umum
- Jurnal tanpa `department_id` → **tidak** mencocok anggaran departemen mana pun
- Jurnal tanpa `department_id` → mencocok anggaran `department_id IS NULL`
- Anggaran pendapatan: actual di atas target menyala dengan `direction=revenue` dan
  `state=under_budget` (favorable), bukan `over_budget`
- Jurnal `is_obsolete` tidak ikut dihitung sebagai actual
- Posting **tidak pernah ditolak** karena warning — status 200 dengan `meta.warnings`

Regresi:

```bash
cd /workspace/laravel_backend
vendor/bin/pint --test
php artisan test tests/Feature/Budget tests/Feature/Journal
grep -rn "strftime" app/Modules/Budget/    # harus kosong
```

---

## Hasil implementasi — 2026-08-14

Status: **selesai**.

**Sebagian besar sudah terjadi di fase 2, bukan karena melompat langkah.**
`BudgetWarningService` mem-query kolom `budget_lines.period` yang dihapus fase 1 — dibiarkan
berarti posting jurnal error. Ia karenanya dipindah ke `BudgetMatchResolver` +
`BudgetAllocationResolver` + `BudgetActualService` saat itu juga, dan cacat 1–4 ikut tertutup.

Yang ditambahkan di fase ini:

- Payload peringatan bertambah `state`, `direction`, dan `matched_scope`
  (mis. `department:7|project:all|period:annual`) — menjawab pertanyaan pertama user:
  "peringatan ini dari anggaran yang mana?".
- `frontend/.../journalEntry.types.ts` — `BudgetWarning` + 3 field **opsional** dan tipe
  `BudgetWarningState`, supaya respons backend lama tetap bertipe benar.
- `tests/Feature/Budget/BudgetWarningTest.php` — 11 test, satu per kasus di §Testing.

### Verifikasi acceptance criteria

| # | Kriteria | Bukti |
|---|---|---|
| 1 | Empat cacat tertutup, dibuktikan test | `BudgetWarningTest` + `BudgetMatchResolverTest` + `BudgetAnalysisTest` |
| 2 | `grep -rn "strftime" app/Modules/Budget/` nol hasil | ✅ hanya 3 komentar yang menjelaskan kenapa dihindari — nol pemakaian |
| 3 | `BudgetWarningService` tidak query `journal_entry_lines` sendiri | ✅ `grep journal_entry_lines app/Modules/Budget/` hanya menemukan README |
| 4 | Posting tidak pernah diblokir anggaran | `test_posting_a_journal_is_never_blocked_by_a_budget_warning` — 200 + `meta.warnings` terisi |
| 5 | `../README.md` diperbarui | ✅ keempat temuan ditandai selesai dengan tautan ke fase ini |

### Yang belum

Mempertajam toast di `JournalFormPage.tsx` memakai `matched_scope` — rencana menandainya
opsional dan boleh ditunda; belum dikerjakan.

---

## Acceptance criteria

1. Empat cacat yang tercatat di `../README.md` tertutup, dibuktikan test masing-masing.
2. `grep -rn "strftime" app/Modules/Budget/` mengembalikan nol hasil.
3. `BudgetWarningService` tidak lagi membangun query ke `journal_entry_lines` sendiri.
4. Posting jurnal tetap tidak pernah diblokir oleh anggaran.
5. `../README.md` diperbarui: keempat temuan ditandai selesai dengan tautan ke fase ini.
