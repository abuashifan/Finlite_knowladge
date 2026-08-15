# Phase 2 — Endpoint Daftar Submission Lintas Periode

**Sisi**: Backend
**Prasyarat**: —
**Membuka**: fase 3

---

## Objective

Satu endpoint daftar submission yang tidak terikat satu periode, supaya halaman
"Daftar Budget" (keputusan **K2**) punya sumber data.

Ini satu-satunya endpoint baru di seluruh rencana ini, dan ia **tidak mengagregasi
apa pun** — hanya mendaftar submission. Semua angka tetap dari
`BudgetAnalysisService`.

---

## 1. Kenapa yang ada sekarang tidak cukup

`GET /budget-periods/{id}/submissions` → `BudgetSubmissionService::list()`:

```php
public function list(BudgetPeriod $period, array $filters = []): Collection
{
    $query = BudgetSubmission::query()
        ->forCompany($companyId)
        ->where('budget_period_id', $period->id)   // ← terkunci satu periode
        ->with('department');

    if (! empty($filters['department_id'])) { ... }  // ← satu-satunya filter

    return $query->orderBy('department_id')->get();   // ← tanpa paginasi
}
```

Tiga keterbatasan, semuanya menghalangi halaman daftar yang layak:

1. **Terkunci satu periode** — tidak bisa "semua anggaran yang menunggu persetujuan saya"
2. **Tanpa paginasi** — `get()` mengembalikan seluruh koleksi
3. **Filter cuma departemen** — tidak ada status, tidak ada pencarian, tidak ada sort

Metode lama **tetap dipertahankan**. `BudgetPeriodDetailPage` memakainya dan
perilakunya benar untuk konteks itu (daftar pendek di dalam satu periode).

---

## 2. Endpoint baru

```
GET /api/budget-submissions          permission: budgets.view
```

Perhatikan: prefix `budget-submissions` sudah ada di
`app/Modules/Budget/Routes/api.php`, tapi hanya berisi rute ber-`{id}`. Rute
indeks ditambahkan di grup yang sama.

### Parameter

| Param | Tipe | Ket |
|---|---|---|
| `budget_period_id` | int? | null = semua periode |
| `department_id` | int? | |
| `status` | string? | `draft,submitted,approved_by_head,approved,rejected,superseded` |
| `is_active` | bool? | `true` = hanya versi aktif — default tampilan |
| `search` | string? | cocokkan nama departemen & `revision_reason` |
| `sort` / `direction` | string? | allowlist: `created_at`, `version_no`, `status`, `budget_period_id` |
| `page` / `per_page` | int? | paginasi standar |

### Bentuk baris

Daftar butuh nominal total per submission, dan itu **bukan** pekerjaan
`BudgetAnalysisService` — tidak ada perbandingan actual di sini, hanya jumlah baris
anggaran. Cukup satu subquery agregat:

```php
->withSum('lines as total_amount', 'amount')
```

Kalau nanti kolom "Realisasi" diminta di daftar ini, **jangan** menambah query
sendiri — panggil `/budget/analysis` dari halaman detail. Daftar tidak perlu tahu
realisasi.

Setiap baris mengembalikan: `id`, `budget_period_id`, `budget_period_name`,
`department_id`, `department_name`, `status`, `version_no`, `is_active`,
`revision_number`, `total_amount`, `submitted_at`, `created_at`.

---

## 3. Implementasi

Pakai trait `AppliesListQuery` seperti service master data lain. Modul Budget belum
memakainya sama sekali — ini pemakaian pertama, jadi ikuti `ProjectService` sebagai
contoh bentuk (`$listSearchable`, `$listSortable`, `$listDefaultSort`).

```
app/Modules/Budget/Services/BudgetSubmissionService.php
  + listAll(array $filters): LengthAwarePaginator
  + properti trait: $listSearchable, $listSortable, $listDefaultSort, $listStatusColumn

app/Modules/Budget/Controllers/BudgetSubmissionController.php
  + indexAll(Request $request): JsonResponse   // pakai $this->listResponse()

app/Modules/Budget/Requests/
  + ListBudgetSubmissionsRequest.php           // allowlist status & sort

app/Modules/Budget/Routes/api.php
  + Route::get('/', [BudgetSubmissionController::class, 'indexAll'])
        ->middleware('permission:budgets.view');
```

### Dua hal yang mudah keliru

**Scope company.** `forCompany($this->tenantContext->companyId())` wajib, sama
seperti `list()`. Tanpa itu daftar bocor lintas perusahaan dalam satu tenant DB.

**Default `is_active`.** Tanpa filter, daftar akan menampilkan setiap versi lama
dari setiap submission yang pernah direvisi — pengguna melihat duplikat yang
membingungkan. Default `is_active=true`; versi lama dilihat lewat halaman Revision
(fase 3) atau dengan mematikan filter secara eksplisit.

---

## Existing files affected

| File | Perubahan |
|---|---|
| `app/Modules/Budget/Services/BudgetSubmissionService.php` | + `listAll()`, + properti trait. `list()` lama tidak disentuh |
| `app/Modules/Budget/Controllers/BudgetSubmissionController.php` | + `indexAll()` |
| `app/Modules/Budget/Routes/api.php` | + 1 rute |

## New files

| File |
|---|
| `app/Modules/Budget/Requests/ListBudgetSubmissionsRequest.php` |
| `tests/Feature/Budget/BudgetSubmissionListTest.php` |

## Database changes

Tidak ada. Index yang dibutuhkan sudah dibuat fase 1 rencana sebelumnya
(`budget_submissions` punya index pada `budget_period_id`, `department_id`,
`is_active`).

---

## Risks

| Risiko | Mitigasi |
|---|---|
| `withSum` menimbulkan N+1 kalau salah tulis | Ini subquery tunggal, bukan relasi ter-load. Verifikasi lewat test yang menghitung jumlah query |
| Daftar bocor lintas company | Test khusus: dua company, masing-masing hanya melihat miliknya |
| Sort dari input pengguna masuk SQL | Allowlist `$listSortable`; nilai di luar itu diabaikan trait |

---

## Testing

`tests/Feature/Budget/BudgetSubmissionListTest.php`:

1. Mengembalikan submission lintas periode
2. Filter `budget_period_id` mempersempit dengan benar
3. Filter `status` mempersempit dengan benar
4. Default hanya versi aktif; `is_active=false` memunculkan yang `superseded`
5. `total_amount` sama dengan jumlah `budget_lines` submission itu
6. Paginasi menghormati `per_page`
7. Sort di luar allowlist diabaikan, tidak error
8. Company lain tidak melihat submission milik company ini
9. Tanpa `budgets.view` → 403

Perintah:

```bash
rtk php artisan test tests/Feature/Budget
vendor/bin/pint --test app/Modules/Budget tests/Feature/Budget
```

---

## Acceptance criteria

- [ ] `GET /api/budget-submissions` mengembalikan daftar terpaginasi lintas periode
- [ ] Default hanya versi aktif
- [ ] `total_amount` cocok dengan jumlah baris anggaran
- [ ] Endpoint lama `GET /budget-periods/{id}/submissions` masih berperilaku sama persis
- [ ] Seluruh suite Budget hijau, Pint bersih

---

## Hasil implementasi — 2026-08-15

### Yang dibuat/diubah

| File | Perubahan |
|---|---|
| `Services/BudgetSubmissionService.php` | + trait `AppliesListQuery` + 6 properti, + `listAll()`. `list()` lama tidak disentuh |
| `Controllers/BudgetSubmissionController.php` | + `indexAll()` |
| `Requests/ListBudgetSubmissionsRequest.php` | **Baru** |
| `Routes/api.php` | + `GET /budget-submissions` |
| `tests/Feature/Budget/BudgetSubmissionListTest.php` | **Baru** — 11 test |

### Penyimpangan

- **P3** — `'is_active' => ['nullable', 'boolean']` menolak `?is_active=false`
  dengan 422. Aturan `boolean` Laravel hanya menerima `1/0/"1"/"0"/true/false`,
  bukan string `"true"`/`"false"`, sedangkan query string tidak punya tipe
  boolean. Diganti `in:true,false,1,0`; normalisasi tetap di service lewat
  `filter_var`. Ketahuan dari test yang gagal, bukan dari review.
- Test bertambah dari 9 (rencana) jadi 11: ditambah kasus submission tanpa baris
  (`withSum` mengembalikan null, bukan 0) dan kasus anggaran tingkat perusahaan
  (`department_id` null).

### Verifikasi

11/11 test hijau · Pint bersih.
