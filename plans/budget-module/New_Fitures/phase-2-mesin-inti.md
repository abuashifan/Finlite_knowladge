# Phase 2 — Mesin Inti

> Prasyarat: fase 1 selesai.

## Objective

Satu mesin agregasi yang melahirkan **seluruh** view. Ini realisasi teknis dari
"ONE BUDGET ENGINE → MULTIPLE DIMENSIONS → MULTIPLE VIEWS".

Akar cacat G6–G8 adalah **peringatan over-budget dan laporan perbandingan memakai logika
pencocokan yang berbeda**. Perbaikannya struktural: satu logika, dua pemakai.

Menutup **G4, G5** dan menyiapkan penutupan **G6, G7, G8, G9** di fase 3.

---

## New files

Semua di `app/Modules/Budget/Services/`.

### 2.1 `BudgetMatchResolver.php` — tangga spesifisitas

Baris jurnal `(akun A, dept D, proyek P, bulan M)` mengonsumsi anggaran dari baris **paling
spesifik** yang cocok. Berhenti di kecocokan pertama:

| Prioritas | account | department | project | period_month |
|---|---|---|---|---|
| 1 | A | D | P | M |
| 2 | A | D | P | NULL |
| 3 | A | D | NULL | M |
| 4 | A | D | NULL | NULL |
| 5 | A | NULL | P | M / NULL |
| 6 | A | NULL | NULL | M / NULL |

- **G7 tertutup** — baris berproyek kini jatuh ke anggaran umum (prioritas 3–4) bila tidak ada
  anggaran khusus proyek. Sebelumnya pencocokannya asimetris: baris jurnal ber-`project_id`
  hanya dicocokkan ke baris anggaran berproyek sama, jadi belanja proyek lolos dari anggaran
  departemen.
- **G8 tertutup** — `D = NULL` hanya cocok dengan baris anggaran `department_id IS NULL`,
  memakai **`whereNull` eksplisit**. Sebelumnya `when($departmentId, …)` tidak memasang filter
  apa pun saat null, lalu `first()` mengambil baris pertama yang kebetulan ketemu — baris jurnal
  tanpa departemen bisa mencocok anggaran departemen mana pun.

Kontrak:

```php
public function resolve(int $accountId, ?int $departmentId, ?int $projectId, string $periodMonth): ?BudgetLine
```

### 2.2 `BudgetActualService.php` — actual bertanda benar

**Wajib** memakai `ReportQueryService::reportableJournalLinesQuery()` sebagai query dasar.
Method itu sudah memfilter `status='posted' AND is_obsolete=0`; `BudgetComparisonService` lama
membangun querynya sendiri dan **lupa `is_obsolete`** → **G4 tertutup**.

Tanda dibalik per jenis akun dalam satu query → **G5 tertutup**:

```sql
SUM(CASE WHEN coa.account_type = 'revenue'
         THEN jel.credit - jel.debit
         ELSE jel.debit  - jel.credit END) AS actual_amount
```

Sebelumnya `SUM(debit − credit)` untuk semua akun mengasumsikan akun bersaldo debit, jadi
menganggarkan akun pendapatan menghasilkan actual negatif dan `over_budget` tidak pernah menyala.

Grouping bulan memakai `ReportQueryService::applyDateRange()` per rentang tanggal,
**bukan `strftime()`** → **G9 tertutup**, portabel ke MySQL.

Filter dimensi memakai `applyDimensionFilter()` + `ReportDimensionFilter` yang sudah ada.

### 2.3 `BudgetAllocationResolver.php` — alokasi periode (G6)

Satu aturan yang berlaku di peringatan **dan** laporan:

| Jenis baris | Pembanding actual |
|---|---|
| `period_month = '2026-09'` | Actual bulan September saja |
| `period_month = NULL` (tahunan) | Actual **kumulatif** dari `period_from` sampai akhir bulan transaksi |

Anggaran gaji 240 juta setahun kini menyala saat akumulasi Jan–Sep melewati 240 juta — bukan
saat satu bulan melewati 240 juta, yang praktis tidak pernah terjadi.

Di view "Budget by Period", baris tahunan **tidak dipecah menjadi angka bulanan palsu**; ia
muncul di baris "Tahunan (belum dialokasikan)". Pemerataan rata per bulan tersedia sebagai
opsi tampilan `allocation=even` — **SHOULD HAVE, bukan default**. Mesin tetap jujur; pemerataan
adalah keputusan penyajian.

### 2.4 `BudgetAnalysisService.php` — inti mesin

```
GET /budget/analysis
  budget_period_id   (wajib)
  group_by[]         urutan dimensi: department | project | account | period | direction
  department_id, project_id, account_id, account_type, direction   (filter)
  date_from, date_to                                               (partial period)
  version            active (default) | all | {submission_id}
  mode               summary | detail | variance
  allocation         annual_row (default) | even
```

Balasan per baris:

```
{kunci dimensi}, budget_amount, actual_amount, variance, variance_pct,
utilization_pct, state, direction
```

**Drill-down** = panggilan ulang dengan `group_by` lebih panjang dan nilai baris induk sebagai
filter:

| Langkah | Panggilan |
|---|---|
| Total perusahaan | `group_by=[]` |
| ↓ per cost center | `group_by=[department]` |
| ↓ proyek di Kesiswaan | `group_by=[project]&department_id=7` |
| ↓ akun di Class Meeting | `group_by=[account]&department_id=7&project_id=3` |

Angka konsisten di tiap level karena berasal dari agregasi yang sama — bukan dari empat query
berbeda yang kebetulan mirip.

---

## Definisi variance — eksplisit, tanpa ambiguitas

| Konteks | Variance | Favorable bila | Utilization |
|---|---|---|---|
| Expense / Cost | `Budget − Actual` | `> 0` (hemat) | `Actual / Budget × 100` |
| Revenue / Sales | `Actual − Budget` | `> 0` (target terlampaui) | `Actual / Budget × 100` |
| Project Profit | `Actual Profit − Budget Profit` | `> 0` | `Actual Cost / Budget Cost × 100` |
| Cash (ending) | `Actual Ending − Budget Ending` | `> 0` | tidak berlaku |

Karena `BudgetActualService` sudah membalik tanda pendapatan, kedua rumus utilization identik
dan hasilnya selalu positif. Tidak ada rumus khusus per view.

**Budget = 0** → `utilization_pct = null`. Jangan bagi nol, jangan kembalikan `INF`, jangan
kembalikan 0 (menyesatkan: 0% terbaca "belum terpakai").

State baris memakai satu enum di `app/Modules/Budget/Support/BudgetState.php`:

| State | Arti |
|---|---|
| `on_budget` | Actual = Budget (toleransi 0.0001) |
| `under_budget` | Favorable menurut tabel di atas |
| `over_budget` | Unfavorable menurut tabel di atas |
| `no_budget` | Ada actual, anggaran 0 atau tidak ada |
| `no_actual` | Ada anggaran, actual 0 |

**Reversal, refund, credit note, debit note, penyesuaian negatif** tidak butuh penanganan
khusus — semuanya sudah menjadi jurnal balik yang ter-*post*, jadi otomatis mengurangi actual.
Jurnal ber-`is_obsolete = 1` dikecualikan `reportableJournalLinesQuery()`.

**Partial period** ditangani filter `date_from`/`date_to` di sisi actual, sementara sisi
anggaran tetap penuh. Tandai `is_partial_period: true` di `meta` supaya UI bisa memberi catatan
— membandingkan actual separuh bulan dengan anggaran sebulan penuh tanpa penanda itu menyesatkan.

---

## Existing files affected

| File | Perubahan |
|---|---|
| `app/Modules/Budget/Services/BudgetComparisonService.php` | Jadi pembungkus tipis `BudgetAnalysisService` dengan preset `group_by=[account]&mode=variance`. Logika lamanya **dibuang**, bukan dibiarkan hidup berdampingan. |
| `app/Modules/Budget/Services/BudgetConsolidationService.php` | Jadi pembungkus dengan preset `group_by=[department]` / `[project]` / `[project,department]`. Bentuk balasan dipertahankan supaya `BudgetConsolidationTable.tsx` tidak rusak. |
| `tests/Feature/Architecture/ModuleBoundariesTest.php` | + `'Budget → App\Modules\Reports\Services\ReportQueryService'` ke `KNOWN_MODULE_COUPLING` |

---

## API / service changes

Endpoint `GET /budget/analysis` ditambahkan di fase 6 bersama view turunan lainnya. Fase ini
hanya lapis service — supaya bisa diuji unit sebelum dibuka ke HTTP.

---

## Frontend changes

Tidak ada.

---

## Dependencies

Fase 1.

---

## Risks

| Risiko | Mitigasi |
|---|---|
| `ModuleBoundariesTest` gagal karena impor lintas modul baru | Budget → `Reports\Services\ReportQueryService` **wajib** ditambahkan ke `KNOWN_MODULE_COUPLING`. Preseden sudah ada: `Reports → Budget\Services\BudgetComparisonService`. |
| Query agregasi lambat pada ledger besar | Index sudah ada di `journal_entry_lines.(account_id, department_id, project_id)` dan `journal_entries.journal_date`. Agregasi selalu dibatasi rentang `budget_periods.period_from..period_to`. |
| Membuang logika `BudgetComparisonService` lama mengubah angka yang sudah dilihat user | Modul belum pernah dipakai dengan data nyata (`budget_periods` = 0). Tidak ada angka historis yang perlu dipertahankan. |
| `group_by` bebas membuka pintu SQL injection | Allowlist dimensi di service, tolak nilai di luar daftar — pola sama dengan `$listSortable` di `AppliesListQuery`. |

---

## Testing

`tests/Unit/Budget/` untuk resolver, `tests/Feature/Budget/` untuk service:

- Tangga spesifisitas: 6 test, satu per prioritas, plus satu memastikan prioritas 1 menang atas 2
- `D = NULL` **tidak** mencocok anggaran dengan `department_id` terisi
- Tanda actual pendapatan positif untuk akun `revenue`
- Jurnal `is_obsolete = 1` tidak terhitung sebagai actual
- Jurnal `status != 'posted'` tidak terhitung
- Konsistensi drill-down: `Σ(group_by=[department])` = `group_by=[]`
- Budget = 0 → `utilization_pct` null, state `no_budget`
- Actual = 0 → state `no_actual`
- Toleransi `on_budget` 0.0001
- Partial period menandai `meta.is_partial_period`
- `group_by` dengan nilai tak dikenal → 422, bukan SQL error

```bash
cd /workspace/laravel_backend
vendor/bin/pint --test
php artisan test tests/Unit/Budget tests/Feature/Budget tests/Feature/Architecture
```

---

## Acceptance criteria

1. `BudgetAnalysisService` menghasilkan angka **sama** dengan `BudgetComparisonService` lama
   untuk kasus akun-saja dengan akun beban — bukti tidak ada regresi.
2. Dan menghasilkan angka **benar** untuk kasus yang dulu salah: akun pendapatan, jurnal
   obsolete, dimensi NULL.
3. Drill-down empat level menjumlah konsisten ke induknya.
4. Tidak ada `strftime()` dan tidak ada query mentah ke `journal_entry_lines` yang tersisa di
   `BudgetAnalysisService` / `BudgetActualService`.
