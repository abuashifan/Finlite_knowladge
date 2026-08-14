# Phase 1 — Fondasi Data

> Prasyarat: `phase-0-context-rules-guardrails.md` sudah dibaca dan disetujui.

## Objective

Satu tabel fakta yang membawa **semua dimensi di baris**, plus integritas referensial yang
hari ini tidak ada sama sekali (`budget_lines` punya nol foreign key dan nol unique constraint).

Menutup **G1, G2, G3, G10**.

---

## Model domain

Grain: **satu baris anggaran = satu nominal untuk satu kombinasi
`(versi, akun, cost center, proyek, bulan)`**.

```
budget_periods            wadah fiscal — dipertahankan, diperbaiki
   └── budget_submissions dokumen anggaran BERVERSI — unit approval
          └── budget_lines FAKTA — semua dimensi di sini
```

Tiga tabel, bukan empat. `budget_submissions` **adalah** versi: revisi membuat baris baru
dengan `version_no + 1` dan `parent_submission_id` menunjuk pendahulunya. Riwayat terjaga
karena baris lama beserta `budget_lines`-nya tidak pernah dihapus.

Instruction menyarankan nama `budgets / budget_lines / budget_versions / budget_version_lines`,
tapi eksplisit berkata jangan memaksakan nama itu dan ikuti konvensi existing. Empat tabel
berarti `budget_version_lines` yang isinya sama persis dengan `budget_lines` — redundansi murni.

### Mengapa dimensi tetap punya "header"

`budget_submissions.department_id` **dipertahankan** sebagai *pemilik dokumen* — itulah unit
persetujuan yang sudah teruji (`budgets.approve_head` = kepala departemen).

`budget_lines.department_id` adalah *dimensi* — default mengikuti header, tapi boleh berbeda
atau NULL.

Dua peran berbeda, bukan duplikasi. Header `department_id` menjadi **nullable**: NULL berarti
anggaran tingkat perusahaan yang langsung diajukan Finance tanpa tahap kepala departemen.

---

## Database changes

Semua migration baru di `database/migrations/tenant/` dengan
`protected $connection = 'tenant';` + `Schema::connection('tenant')`.

### 1.1 `departments` — hierarki cost center (G10)

```php
$table->unsignedBigInteger('parent_id')->nullable()->after('id');
$table->foreign('parent_id')->references('id')->on('departments')->nullOnDelete();
$table->index('parent_id');
```

Pola identik dengan `chart_of_accounts.parent_account_id`. Service mencegah siklus dan
membatasi kedalaman maksimal 5 level.

### 1.2 `budget_periods` — perbaikan integritas

| Perubahan | Alasan |
|---|---|
| + `fiscal_year_id` unsignedBigInteger nullable | `fiscal_years` ada di DB **central** → tidak bisa FK lintas-database. Pola sama dengan `created_by` dan `posted_by` di `journal_entries`. Divalidasi di service. |
| + `beginning_cash_override` decimal(20,2) nullable | Cash Budget: saldo awal default dihitung dari ledger; kolom ini hanya untuk override manual |
| + index `(fiscal_year, status)` | Query daftar periode |

`company_id` **dipertahankan apa adanya.** Ia redundan dengan batas tenant (satu DB per
perusahaan) dan tidak konsisten dengan tabel tenant lain, tapi sudah dipakai
`scopeForCompany()` di tiga service dan seluruh test. Mengubahnya memberi nol manfaat
fungsional. Catat sebagai peninggalan, jangan rapikan di fase ini.

### 1.3 `budget_submissions` — jadi dokumen berversi (G2)

| Kolom | Perubahan |
|---|---|
| `department_id` | NOT NULL → **nullable** (NULL = anggaran perusahaan) |
| `parent_submission_id` | **baru**, unsignedBigInteger nullable, self-FK nullOnDelete |
| `version_no` | **baru**, unsignedSmallInteger default 1 |
| `is_active` | **baru**, boolean default false — tepat satu `true` per (period, department) di antara versi berstatus `approved` |
| `revision_reason` | **baru**, text nullable |
| `status` enum | + `superseded` |
| FK | `budget_period_id` → `budget_periods` cascadeOnDelete; `department_id` → `departments` restrictOnDelete |
| index | `(budget_period_id, department_id, is_active)`, `(parent_submission_id)` |

`revision_number` yang sudah ada **dipertahankan** — ia menghitung berapa kali pengajuan
ditolak, beda peran dengan `version_no` yang menghitung versi anggaran. Perbedaannya wajib
didokumentasikan di `app/Modules/Budget/README.md`.

### 1.4 `budget_lines` — drop & recreate (G1, G3)

Grain berubah, jadi tabel lama dibuang.

> ⚠️ **Migration wajib memeriksa `count() === 0` lebih dulu dan `throw` bila ada data.**
> Tenant yang terlanjur mengisi tidak boleh terhapus diam-diam. Sekarang kedua tenant
> berisi 0 baris, tapi jangan mengandalkan itu — periksa di runtime.

```
id
budget_submission_id  FK → budget_submissions, cascadeOnDelete
account_id            FK → chart_of_accounts, restrictOnDelete   NOT NULL
department_id         FK → departments, nullOnDelete             NULL = tidak dialokasikan
project_id            FK → projects,    nullOnDelete             NULL = lintas proyek
period_month          char(7) NULL      -- 'YYYY-MM'; NULL = tahunan
direction             string(10)        -- 'revenue' | 'expense', diturunkan dari account_type
amount                decimal(20,2)
notes                 text NULL
timestamps
```

Index: `(budget_submission_id, account_id)`, `account_id`, `department_id`, `project_id`,
`period_month`, `direction`.

**Unique constraint.** NULL ≠ NULL di SQL, jadi unique biasa tidak menggigit — itulah sebabnya
migration lama sengaja tidak memasangnya dan menyerahkan ke service. Pakai unique index
berbasis ekspresi lewat raw statement:

```sql
CREATE UNIQUE INDEX budget_lines_grain_unique ON budget_lines (
  budget_submission_id, account_id,
  COALESCE(department_id, 0), COALESCE(project_id, 0), COALESCE(period_month, '')
);
```

SQLite dan MySQL 8 keduanya mendukung index ekspresi.
`validateLinesUnique()` yang sudah ada dan teruji **tetap dipertahankan** sebagai lapis pertama,
supaya pesan errornya ramah (422 dengan penjelasan) alih-alih `DATABASE_ERROR`.

**`direction`** diturunkan dari `chart_of_accounts.account_type` saat baris ditulis, bukan
diinput user:

| `account_type` | `direction` |
|---|---|
| `revenue` | `revenue` |
| `expense` | `expense` |
| lainnya | ditolak — `BUDGET_ACCOUNT_DIRECTION_MISMATCH` |

Disimpan (bukan di-join setiap kali) supaya filter `direction=revenue` bisa memakai index.

---

## Existing files affected

| File | Perubahan |
|---|---|
| `app/Modules/Budget/Models/BudgetPeriod.php` | + `fiscal_year_id`, `beginning_cash_override` di `$fillable`/`$casts` |
| `app/Modules/Budget/Models/BudgetSubmission.php` | + kolom versi; relasi `parent()` / `versions()`; scope `active()` |
| `app/Modules/Budget/Models/BudgetLine.php` | + `department_id`, `direction`; relasi `department()`; `$appends` + `department_name` |
| `app/Modules/MasterData/Models/Department.php` | + relasi `parent()` / `children()`; scope `roots()` |
| `app/Modules/MasterData/Services/DepartmentService.php` | guard siklus + batas kedalaman 5 |
| `app/Modules/MasterData/Requests/{Store,Update}DepartmentRequest.php` | + `parent_id` nullable `exists:tenant.departments,id` |
| `app/Modules/Budget/Requests/StoreBudgetSubmissionRequest.php` | `department_id` jadi nullable |
| `app/Modules/Budget/Requests/UpdateBudgetLinesRequest.php` | + `department_id` nullable per baris |
| `app/Modules/Budget/Services/BudgetSubmissionService.php` | `create()` menerima `department_id` null; `updateLines()` menurunkan `direction` |

---

## New files

- 4 migration tenant: `departments` parent, `budget_periods` alter, `budget_submissions` alter,
  `budget_lines` drop-recreate
- `app/Modules/Budget/Support/BudgetDirection.php` — `const string REVENUE = 'revenue'` /
  `EXPENSE = 'expense'` + helper `fromAccountType()`. Class of `const string`, bukan backed enum
  (konvensi codebase).

---

## API / service changes

Tidak ada endpoint baru di fase ini. Kontrak `PUT /budget-submissions/{id}/lines` bertambah
field opsional `department_id` per baris — aditif, tidak merusak pemanggil lama.

---

## Frontend changes

Tidak ada. Frontend menyusul di fase 7. Pastikan halaman existing tetap jalan karena field
baru bersifat opsional.

---

## Dependencies

Tidak ada. Fase pertama.

---

## Risks

| Risiko | Mitigasi |
|---|---|
| Drop `budget_lines` menghapus data tenant yang tidak diketahui | Migration menghitung baris dan `throw` bila ≠ 0. Jalankan pemeriksaan di semua tenant sebelum deploy. |
| SQLite tidak mendukung `ALTER TABLE` untuk mengubah NOT NULL → nullable | Laravel butuh `doctrine/dbal`, atau pakai pola rebuild tabel. Periksa dulu; bila tidak tersedia, `budget_submissions` juga di-drop-recreate dengan guard yang sama. |
| Menambah FK ke tabel yang sudah punya baris yatim | Tidak berlaku — semua tabel budget kosong. |
| `restrictOnDelete` pada `account_id` memblokir penghapusan akun yang sah | Itu memang perilaku yang diinginkan (business rule "deleted account"). CoA juga tidak punya soft delete, hanya `is_active`. |

---

## Testing

`tests/Feature/Budget/` (extends `BudgetTestCase`) + migration test:

- `php artisan migrate --database=tenant --path=database/migrations/tenant` bersih di tenant kosong
- Migration **gagal keras** dengan pesan jelas di tenant yang `budget_lines` berisi data
- FK: hapus submission → baris ikut terhapus (cascade); hapus project → `project_id` jadi NULL;
  hapus akun terpakai → ditolak (restrict)
- Unique index menolak duplikat termasuk saat `department_id`/`project_id`/`period_month` NULL
- `direction` terisi otomatis dari `account_type`; akun neraca ditolak 422
- Hierarki department: menolak siklus, menolak kedalaman > 5
- `BudgetFlowTest` 7 test lama tetap lulus setelah penyesuaian model

Perintah:
```bash
cd /workspace/laravel_backend
vendor/bin/pint --test
php artisan test tests/Feature/Budget
```

---

## Acceptance criteria

1. Skema baru terpasang di tenant kosong tanpa error.
2. Satu `budget_submissions` bisa memuat baris dengan cost center dan proyek **berbeda-beda**.
3. `budget_lines` punya FK ke keempat tabel referensi dan unique index yang menggigit
   termasuk saat dimensi NULL.
4. `departments` bisa dibentuk hierarki dan menolak siklus.
5. `BudgetFlowTest` lama lulus tanpa perubahan makna test.
