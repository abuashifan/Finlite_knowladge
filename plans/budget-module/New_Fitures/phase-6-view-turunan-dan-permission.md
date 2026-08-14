# Phase 6 — View Turunan, Cash Budget, Project Profitability & Permission

> Prasyarat: fase 2, 4, 5 selesai.
>
> ⚠️ **Bagian Project Budget/Profitability/Cash Flow di fase ini diberi lapisan tambahan — lihat
> [project-dimension-budgeting-readiness-plan.md](project-dimension-budgeting-readiness-plan.md).**
> Formula (Profit = Revenue − Cost, Margin %, Cash Budget) **tidak berubah** dan tetap berlaku.
> Yang berubah: akurasi *Actual Cost* bergantung pada perbaikan dimensi di COGS
> (`StockMovementJournalService`) dan depresiasi (`FixedAssetService`) yang ternyata juga bocor
> — bukan cuma Sales Invoice. Project Cash Flow relatif aman lebih cepat (Cash/Bank sudah benar
> propagasi dimensinya); Project Profitability/Financial Summary baru akurat setelah dokumen
> baru itu P0-nya selesai.

## Objective

Enam belas reporting view sebagai **pembungkus tipis** di atas mesin fase 2 — nol logika
duplikat. Plus Cash Budget, Project Profitability, business rules, dan permission baru.

Menutup **G13**.

---

## 1. Enam belas view = preset, bukan engine

| # | View | Preset / service |
|---|---|---|
| 1 | Budget by Account | `group_by=[account]` |
| 2 | Budget by Cost Center | `group_by=[department]` |
| 3 | Budget by Project | `group_by=[project]` |
| 4 | Budget by Period | `group_by=[period]` |
| 5 | Revenue Budget | `group_by=[account]&direction=revenue` |
| 6 | Expense Budget | `group_by=[account]&direction=expense` |
| 7 | Budget vs Actual | `group_by=[account]&mode=variance` |
| 8 | Variance Analysis | idem + urut `abs(variance)` desc |
| 9 | Budget Utilization | idem + urut `utilization_pct` desc |
| 10 | Cash Budget | `BudgetCashService` (§2) |
| 11 | Project Budget | `group_by=[project,account]` |
| 12 | Project Actual | idem, kolom actual |
| 13 | Project Profitability | `BudgetProjectService` (§3) |
| 14 | Project Margin | kolom turunan dari #13 |
| 15 | Project Cash Flow | #10 difilter `project_id` |
| 16 | Budget Revision History | fase 5, `GET /budget-submissions/{id}/versions` |

Untuk setiap view, keterangan yang diminta brief:

- **Source data** — `budget_lines` (sisi anggaran) + `journal_entry_lines` posted, non-obsolete
  (sisi actual). Selalu keduanya, selalu sama.
- **Filter** — `budget_period_id` wajib; `department_id`, `project_id`, `account_id`,
  `account_type`, `direction`, `date_from`, `date_to`, `version` opsional.
- **Grouping / dimensions** — `group_by[]`, urutannya menentukan hierarki drill-down.
- **Columns** — `budget_amount`, `actual_amount`, `variance`, `variance_pct`,
  `utilization_pct`, `state`, `direction`.
- **Calculations** — tabel variance & utilization di fase 2. Tidak ada rumus khusus per view.
- **Drill-down** — panggilan ulang dengan `group_by` lebih panjang + nilai induk sebagai filter.
- **Relationship** — semuanya membaca baris anggaran dan baris jurnal yang **sama**. Angka di
  view #2 adalah jumlah dari angka di view #3 untuk cost center itu, dan seterusnya.

Endpoint terpisah tetap dibuat meskipun isinya preset, karena
`frontend/src/modules/reports/constants/reportCategories.ts` membutuhkan report key diskrit
untuk katalog laporan dan fitur simpan laporan.

---

## 2. Cash Budget — tanpa tabel baru

`app/Modules/Budget/Services/BudgetCashService.php`

```
Beginning Cash          saldo akun is_cash_bank pada period_from − 1 hari, dari ledger
+ Budgeted Cash Inflow  Σ budget_lines direction='revenue'
− Budgeted Cash Outflow Σ budget_lines direction='expense'
= Budgeted Ending Cash
```

Sisi actual memakai mesin yang sama, dibatasi ke akun `is_cash_bank = 1`.
Pengelompokan inflow/outflow memakai `chart_of_accounts.cash_flow_section`
(`operating` / `investing` / `financing`) yang **sudah ada** — tidak perlu klasifikasi baru.

`beginning_cash_override` (fase 1) dipakai bila diisi; kalau null, saldo dihitung dari ledger.

### Asumsi yang wajib ditulis eksplisit

Anggaran bersifat **akrual**, jadi Budgeted Cash Flow mengabaikan jeda AR/AP: pendapatan yang
dianggarkan bulan Maret diperlakukan sebagai kas masuk bulan Maret, walaupun invoice-nya baru
tertagih bulan Mei.

Ini harus muncul sebagai catatan di UI Cash Budget, bukan hanya di dokumen. Penghalusan
memakai `payment_terms` (tabelnya sudah ada) adalah **FUTURE**, bukan MUST HAVE.

### Hubungan dengan view lain

Cash Budget membaca **baris anggaran yang sama** dengan Revenue Budget dan Expense Budget —
bukan angka terpisah yang bisa berbeda. Difilter `project_id` ia menjadi Project Cash Flow
(view #15). Actual Cash Transaction datang dari akun `is_cash_bank` di ledger yang sama.

---

## 3. Project Budget & Profitability

`MasterData\Models\Project` sudah generic (`code`, `name`, `start_date`, `end_date`, `status`,
`is_active`) — cocok untuk lembaga pendidikan, kontraktor, agency, manufaktur, distributor,
maupun jasa. **Tidak ada kolom spesifik-industri yang ditambahkan.** Class Meeting, Renovasi
Kantor, Campaign, dan Custom Production semuanya baris yang sama bentuknya.

Struktur "Renovasi Kantor PT ABC" dari brief terwakili penuh tanpa tabel baru:

| Baris brief | Representasi |
|---|---|
| Project Revenue 500 jt | `budget_line(project=X, account=Pendapatan Jasa, direction=revenue, 500jt)` |
| Material 220 jt / Labor 120 jt / Transport 25 jt / Subcon 70 jt / Equipment 20 jt / Other 15 jt | satu baris per akun, `direction=expense` |
| Total Cost Budget 470 jt | agregasi `direction=expense` |
| Budget Profit 30 jt | turunan, tidak disimpan |
| Budget Margin 6% | turunan, tidak disimpan |

`app/Modules/Budget/Services/BudgetProjectService.php` → `GET /budget/projects/{id}/summary`:

| Metrik | Rumus |
|---|---|
| Budget / Actual Revenue | `direction=revenue`, sudah bertanda positif |
| Budget / Actual Cost | `direction=expense` |
| Profit | `Revenue − Cost` |
| Margin % | `Profit / Revenue × 100`; **`null` bila Revenue = 0** |
| Cash In / Out | Cash Budget difilter `project_id` |

Contoh brief menghasilkan: Budget Profit 30 jt / 6%, Actual Profit 38 jt / 7,6% — persis.

> ⚠️ Akurasi Actual Revenue bergantung pada fase 4. Invoice yang di-post **sebelum** fase 4
> tidak membawa `project_id` dan tidak akan terhitung. Tampilkan catatan ini di UI Project
> Summary, jangan diam-diam menampilkan angka yang kurang.

---

## 4. Permission

Naming mengikuti `{module}.{action}` dan tabel aksi di
`PermissionCatalogService::matrixColumnForAction()` supaya render di matriks permission, bukan
sebagai chip "special".

| Key | Status | Peran |
|---|---|---|
| `budgets.view` | ada | Lihat semua view & laporan |
| `budgets.submit` | ada | Buat/edit baris, ajukan |
| `budgets.approve_head` | ada | Setujui tahap kepala |
| `budgets.approve_finance` | ada | Setujui tahap finance |
| `budgets.manage` | ada | Kelola & tutup periode |
| `budgets.revise` | **baru** | Buat versi baru dari anggaran approved |
| `budgets.export` | **baru** | Export CSV |

`budgets.delete` **tidak ditambahkan** — hari ini tidak ada route DELETE, dan soft-delete sudah
cukup lewat `budgets.manage`. Konsisten dengan modul Journal yang juga tanpa DELETE.

Tiga tempat wajib disentuh:

1. `config/permissions.php` — daftar `permissions` **dan** preset role (`finance` mendapat
   keduanya; `owner`/`admin` sudah `['*']`)
2. Migration central `database/migrations/YYYY_MM_DD_NNNNNN_sync_budget_permissions.php`
   (**G13** — belum pernah ada, jadi `budgets.*` hanya sampai ke database lewat
   `PermissionSeeder`). Meniru `2026_08_11_000001_sync_import_permissions.php`.
3. `config/plan_features.php` — feature `budgeting` ditambah `budgets.revise` dan
   `budgets.export`. **`budgets.view` tetap tidak di-gate** supaya akses baca bertahan saat
   plan diturunkan.

Project budget menghormati permission project existing — pemilihan proyek lewat
`proyekApi.search()` yang tunduk pada `projects.view`.

---

## 5. API changes

Semua ditambahkan ke `app/Modules/Budget/Routes/api.php` di dalam grup
`['auth:sanctum','company.access']` yang sudah ada. Pola existing: **tanpa `/v1`, tanpa route
name, tanpa `Route::apiResource`**, sub-aksi sebagai POST.

**16 endpoint lama dipertahankan seluruhnya** — kontrak frontend tidak dirusak.

| Method | Path | Permission |
|---|---|---|
| GET | `/budget/analysis` | `budgets.view` |
| GET | `/budget/summary` | `budgets.view` |
| GET | `/budget/cash` | `budgets.view` |
| GET | `/budget/projects/{id}/summary` | `budgets.view` |
| GET | `/budget/projects/{id}/profitability` | `budgets.view` |
| GET | `/reports/budget/by-account` | `budgets.view` |
| GET | `/reports/budget/by-cost-center` | `budgets.view` |
| GET | `/reports/budget/by-project` | `budgets.view` |
| GET | `/reports/budget/by-period` | `budgets.view` |
| GET | `/reports/budget/utilization` | `budgets.view` |
| GET | `/reports/budget/variance` | `budgets.view` |

`GET /reports/budget/comparison` **dipertahankan** sebagai alias tipis ke
`by-account&mode=variance`, supaya `BudgetComparisonPage` yang sudah jalan tidak rusak.

`ApiErrorCode` baru — daftarkan di **kedua** tempat (class + `config/api_errors.php`):

`BUDGET_PERIOD_OVERLAP` · `BUDGET_VERSION_NOT_ACTIVE` · `BUDGET_ALREADY_APPROVED` ·
`BUDGET_NEGATIVE_AMOUNT` · `BUDGET_ACCOUNT_DIRECTION_MISMATCH` · `BUDGET_PROJECT_NOT_ACTIVE`

---

## 6. Business rules

| Kasus | Aturan |
|---|---|
| Duplicate budget | Unique index grain (fase 1) + `validateLinesUnique()` |
| Overlapping budget periods | Dua periode berstatus `open` pada `fiscal_year` sama **tidak boleh** beririsan tanggal → `BUDGET_PERIOD_OVERLAP` |
| Multiple project budgets | Boleh — beda proyek = beda baris |
| Multiple cost center budgets | Satu pengajuan **aktif** per (period, department); versi baru menggantikan yang lama |
| Approved budget | Immutable; ubah hanya lewat `revise` |
| Revised budget | Butuh `revision_reason`; versi lama jadi `superseded` |
| Closed accounting period | Anggaran **tetap terbaca**; pembuatan/revisi ditolak lewat `PeriodLockService::isDateReadOnly()` pada `period_from` |
| Deleted project | `nullOnDelete` → baris jadi lintas-proyek, tidak yatim |
| Deleted account | `restrictOnDelete` — akun yang terpakai anggaran tidak bisa dihapus |
| Deleted cost center | `nullOnDelete` di baris; `restrictOnDelete` di header pengajuan |
| Zero budget | **Sah** — menandai "tidak boleh belanja"; utilization `null`, state `no_budget` |
| Negative budget | **Ditolak** → `BUDGET_NEGATIVE_AMOUNT`. Koreksi turun dilakukan lewat revisi, bukan nominal negatif |
| Revenue budget | Hanya akun `account_type='revenue'`; `direction` diturunkan otomatis |
| Expense budget | Hanya `account_type='expense'`; akun neraca ditolak → `BUDGET_ACCOUNT_DIRECTION_MISMATCH` |
| Project budget | Proyek harus `is_active` **dan** `status='active'` (`Project::usable()`) |
| Partial project | Proyek `active` boleh dianggarkan kapan saja, termasuk lintas periode |
| Completed project | Anggaran **baru** ditolak → `BUDGET_PROJECT_NOT_ACTIVE`; anggaran lama tetap terbaca dan tetap dibandingkan dengan actual |
| Akun non-leaf | Ditolak — `PostableAccount` rule (sudah dipakai) |

Tidak ada satu pun aturan di atas yang bertentangan dengan sistem existing — semuanya
memanfaatkan guard yang sudah ada.

---

## Existing files affected

`Routes/api.php` · `Controllers/BudgetConsolidationController.php` ·
`Reports/Controllers/BudgetComparisonController.php` · `Services/BudgetPeriodService.php`
(cek overlap) · `Services/BudgetSubmissionService.php` (validasi direction, negative, project
aktif) · `config/permissions.php` · `config/plan_features.php` · `config/api_errors.php` ·
`App\Shared\Api\ApiErrorCode`

## New files

`Services/BudgetCashService.php` · `Services/BudgetProjectService.php` ·
`Controllers/BudgetAnalysisController.php` · `Controllers/BudgetProjectController.php` ·
`Controllers/BudgetCashController.php` · `Requests/BudgetAnalysisRequest.php` ·
`Requests/BudgetCashRequest.php` · migration central `sync_budget_permissions`

## Database changes

Hanya migration central untuk permission. Tidak ada perubahan skema tenant.

## Frontend changes

Tidak ada di fase ini — fase 7.

---

## Dependencies

Fase 2 (mesin), fase 4 (dimensi revenue), fase 5 (versioning).

---

## Risks

| Risiko | Mitigasi |
|---|---|
| Sebelas endpoint baru terasa banyak | Semuanya pembungkus 3–5 baris di atas satu service. Kalau ada yang butuh logika sendiri, itu tanda mesin fase 2 kurang lengkap. |
| Project Profitability menampilkan angka kurang untuk invoice lama | Catatan eksplisit di UI dan dokumen (§3). |
| Asumsi akrual pada Cash Budget disalahpahami sebagai proyeksi kas sungguhan | Catatan di UI, bukan hanya di dokumen. |
| Permission baru tidak sampai ke database existing | Itulah gunanya migration `sync_budget_permissions` (G13). Verifikasi dengan menjalankan `php artisan migrate` di database central lalu cek tabel `permissions`. |

---

## Testing

- Cash Budget: `Beginning + Inflow − Outflow = Ending`, dengan dan tanpa `beginning_cash_override`
- Project Profitability dengan revenue → Profit & Margin benar
- Project **tanpa** revenue → Margin `null`, bukan pembagian nol
- Project hanya beban → Profit negatif, tidak error
- Project tanpa transaksi → semua actual 0, state `no_actual`
- Anggaran tanpa transaksi → `no_actual`; transaksi tanpa anggaran → `no_budget`
- Isolasi tenant: perusahaan A tidak melihat anggaran perusahaan B
- 403 untuk role tanpa `budgets.revise` / `budgets.export`
- 422 untuk **setiap** business rule di tabel §6 — satu test per baris
- Konsistensi lintas view: total view #2 = Σ view #3 per cost center = Σ view #1 per akun
- Migration permission: key baru muncul di tabel `permissions` dan `role_permissions`

```bash
cd /workspace/laravel_backend
vendor/bin/pint --test
php artisan test tests/Feature/Budget tests/Feature/Architecture
```

---

## Acceptance criteria

1. Keenam belas view memberi angka konsisten dari sumber yang sama.
2. Drill-down di tiap level menjumlah ke induknya.
3. Cash Budget dan Project Profitability tidak membuat tabel baru satu pun.
4. Setiap business rule di §6 punya test yang membuktikannya.
5. `budgets.revise` dan `budgets.export` sampai ke database lewat migration, bukan hanya seeder.
