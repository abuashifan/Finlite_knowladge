# Phase 0 — Context, Rules & Guardrails

> Fase ini **tidak menghasilkan kode**. Ia menetapkan konteks, aturan main, dan batas yang
> mengikat fase 1–8. Baca sampai habis sebelum menyentuh fase mana pun.

## Objective

Menetapkan apa yang sudah ada, apa yang tidak boleh dibuat, dan mengapa.

---

## 1. Keadaan terverifikasi

Semua di bawah dibaca langsung dari kode, bukan dari dokumen.

| Fakta | Bukti |
|---|---|
| Modul Budget sudah lengkap & teruji di backend | `app/Modules/Budget/` — 3 controller, 3 model, 7 request, 5 service, 16 route di `Routes/api.php`, `tests/Feature/Budget/BudgetFlowTest.php` 7 lulus |
| Fase 0–3 perbaikan frontend sudah selesai | `../README.md` progress ledger, 2026-08-09 |
| **Data produksi 0 baris** di kedua tenant | `budget_periods` kosong → skema masih bebas dirombak |
| Struktur sekarang tidak bisa multidimensi | `department_id` ada di **header pengajuan** (`budget_submissions`), bukan di baris |
| `cost_centers` tidak ada di seluruh codebase | grep `cost_center` → 0 hit di `app/`, `database/`, `config/`, `routes/`, `frontend/` |
| Dimensi **sudah** mengalir ke jurnal dari Cash Payment, Cash Receipt, COGS, Fixed Asset | `CashPaymentService.php:200-201`, `CashReceiptService.php:222-223`, `StockMovementJournalService.php:234-258`, `FixedAssetService.php:471-472` |
| **Kecuali Sales Invoice** — dimensi dibuang | `SalesInvoiceService.php:451-467` mengelompokkan pendapatan hanya per `revenue_account_id` |
| Tidak ada tabel ledger | GL diturunkan dari `journal_entry_lines ⋈ journal_entries WHERE status='posted' AND is_obsolete=0` |
| Tenancy = satu database SQLite per perusahaan | `TenantConnectionManager`, `TenantContext`; tidak ada global scope, tidak ada row-level `company_id` sebagai batas |
| Empat cacat perilaku sudah tercatat, belum diperbaiki | `../README.md` §"Temuan rancangan yang belum diputuskan" |

---

## 2. Prinsip arsitektur

1. **ONE BUDGET ENGINE.** Account, Cost Center, Project, Period adalah *dimensi*, bukan engine
   terpisah. "Budget by Account", "Sales Budget", "Project Budget" adalah **view**, bukan tabel.
2. **Semua reporting view lahir dari satu sumber.** Kalau sebuah angka bisa dihitung, jangan
   disimpan — profit, margin, variance, utilization semuanya turunan.
3. **Actual selalu dari ledger existing.** Tidak ada input actual manual di modul Budget.
4. **Project adalah dimensi bisnis generik** — sekolah, kontraktor, agency, manufaktur,
   distributor, jasa. Tidak ada kolom spesifik-industri.
5. **Jangan buat ledger, cash ledger, atau design system baru.**
6. **Jangan over-engineer.** Tiga tabel, bukan empat.

---

## 3. Arsitektur existing yang dipakai ulang

| Kebutuhan | Yang dipakai | Lokasi |
|---|---|---|
| Sumber actual | Posted journal lines | `ReportQueryService::reportableJournalLinesQuery()` — sudah memfilter `status='posted' AND is_obsolete=0` |
| Filter dimensi | `ReportDimensionFilter` | `app/Shared/Reports/Data/ReportDimensionFilter.php` |
| Dimensi di ledger | `journal_entry_lines.department_id` / `.project_id` | `2026_05_19_000003_add_dimensions_to_journal_entry_lines_table.php` |
| Sifat akun | `chart_of_accounts.account_type`, `is_cash_bank`, `cash_flow_section` | Cash Budget lahir dari sini, tanpa cash ledger baru |
| Fiscal year & periode | `fiscal_years`, `accounting_periods` (DB **central**) | Sudah punya open/closed + `locked_until` |
| Kunci periode | `PeriodLockService::isDateReadOnly()` | `app/Modules/Accounting/Services/PeriodLockService.php` |
| Permission | `config/permissions.php` + middleware `permission:` | `budgets.*` sudah ada 5 key |
| Audit trail | `AuditLogService` → `tenant_audit_logs` | Budget **belum** memakainya (G12) |
| Envelope API | `ApiResponse` trait + `ApiResponseBuilder` | `app/Shared/Api/` |
| List/filter/sort | `AppliesListQuery` | `app/Shared/Api/AppliesListQuery.php` |
| Error | `ApiException::make(ApiErrorCode::X, …)` | Kode baru wajib di class **dan** `config/api_errors.php` |
| Validasi akun leaf | `PostableAccount` rule | `app/Shared/Rules/PostableAccount.php` — sudah dipakai `UpdateBudgetLinesRequest` |
| Report FE | `ReportCompactBar`, `ReportParameterModal`, `useReportParams`, `SaveReportButton` | `frontend/src/modules/reports/` |
| Tabel & form FE | `DataTable`, `SearchableSelect`, `AmountInput`, `WorkspaceLayout`, `FormLayout`, `PermissionGuard` | `frontend/src/components/shared/` |

---

## 4. Guardrails

### Backend (`laravel_backend/AGENTS.md`)

- Business logic di Service; controller tipis (FormRequest → service → `ApiResponse`).
- Validasi di `Requests/`, tidak pernah di controller.
- Semua tulis dibungkus `DB::transaction`.
- Perubahan skema hanya lewat migration; jangan sunting file SQLite langsung.
- **Jangan rusak**: middleware tenant, permission, immutability jurnal, date/period guard,
  rollback/void.
- Jangan refactor modul yang tidak diminta.
- Setiap fitur wajib punya feature test happy path **dan** failure path.
- Impor lintas modul baru wajib didaftarkan di `ModuleBoundariesTest::KNOWN_MODULE_COUPLING`,
  kalau tidak `tests/Feature/Architecture` gagal.
- Presisi uang: ikuti kolom budget existing `decimal(20,2)`; `decimal(18,2)` untuk yang lain.
- Enum ditulis sebagai `const string` di class, bukan PHP backed enum (konvensi codebase).
- Tanpa API Resource — flattening lewat `$appends` pada model.
- Tanpa `/v1`, tanpa route name, tanpa `Route::apiResource`. Sub-aksi sebagai POST
  (`/{id}/submit`, `/{id}/revise`).
- Menambah direktori backend ⇒ perbarui `docs/backend-directory-tree.md` (tanggal + hitungan
  direktori). Itu bagian dari Definition of Done.
- Jalankan test yang paling sempit: `php artisan test tests/Feature/Budget`. Suite penuh ±6 menit.

### Frontend (`frontend/AGENTS.md` §8)

```
❌ no `any` tanpa komentar justifikasi   ❌ no fetch di komponen (TanStack Query)
❌ no data API di Zustand                ❌ no komponen baru bila sudah ada
❌ no Tailwind di luar design token       ❌ no URL API hardcoded
❌ jangan sunting src/components/ui/      ❌ no tombol aksi tanpa cek permission

✅ semua panggilan API di src/modules/{module}/services/
✅ form pakai React Hook Form + Zod       ✅ props & response API bertipe
✅ tabular-nums di semua angka            ✅ perbarui docs/struktur_frontend.md
✅ npm run build DAN npm run lint hijau sebelum selesai
```

Tambahan dari memori proyek:

- Konfirmasi TypeScript dengan `npm run build`, **bukan hanya** `rtk tsc` — `rtk tsc` tidak lengkap.
- Salin versi lama file UI ke scratchpad sebelum mengedit, supaya bisa dibatalkan.
- Navigasi lewat `useRecordTab` / `openRecordTab`, bukan `navigate()` langsung
  (`createMemoryRouter`).

---

## 5. Yang TIDAK dibuat

- ❌ Tabel ledger / cash ledger baru — actual selalu dari `journal_entry_lines`
- ❌ Entitas `cost_centers` — `departments` **adalah** cost center
- ❌ Modul `Project` baru — `MasterData\Models\Project` sudah generic
- ❌ API Resource layer
- ❌ Design system atau komponen UI baru
- ❌ `budgets.delete` — tidak ada route DELETE hari ini; konsisten dengan modul Journal
- ❌ Tabel `budget_version_lines` terpisah — versi menyimpan barisnya sendiri

---

## 6. Yang ditunda, dengan alasan

**Scoping "Dept hanya lihat pengajuannya sendiri".** Tidak ada kolom apa pun yang
menghubungkan user ke departemen — `company_users` (central) hanya punya `role`; tabel
`departments` (tenant) tidak punya kaitan ke user. Menambahkan `company_users.department_id`
berarti satu departemen per user untuk **semua** perusahaan, yang hampir pasti salah. Butuh
rancangan tersendiri.

> ⚠️ Jangan dikerjakan "sekalian" di tengah fase mana pun.

**Multi-company consolidation.** Tenancy adalah satu database per perusahaan. Konsolidasi
lintas perusahaan butuh agregator lintas-DB tersendiri, di luar cakupan modul Budget.

---

## 7. Gap Analysis

| # | Gap | Dampak | Ditutup di fase |
|---|---|---|---|
| G1 | `department_id` di header, bukan di baris | Tidak multidimensi | 1 |
| G2 | Tidak ada versioning; `revision_number` hanya counter | Riwayat hilang saat baris ditimpa | 1, 5 |
| G3 | `budget_lines` tanpa FK & unique constraint | Baris yatim & duplikat lolos | 1 |
| G4 | `BudgetComparisonService` tidak pakai `ReportQueryService` | Jurnal `is_obsolete` terhitung sebagai actual | 2, 3 |
| G5 | `SUM(debit − credit)` untuk semua akun | Actual pendapatan negatif; `over_budget` tak pernah menyala | 2, 3 |
| G6 | Anggaran tahunan dibandingkan actual **satu bulan** | Anggaran gaji setahun baru menyala kalau sebulan tembus setahun | 2, 3 |
| G7 | Baris jurnal ber-proyek tidak dicocokkan ke anggaran umum | Belanja proyek lolos dari anggaran departemen | 2, 3 |
| G8 | Baris jurnal tanpa dept mencocok anggaran dept mana pun | `when($departmentId, …)` + `first()` ambil baris sembarang | 2, 3 |
| G9 | `strftime()` SQLite-only | Tidak portabel ke MySQL | 3 |
| G10 | `departments` flat tanpa `parent_id` | Drill-down cost center hanya 1 level | 1 |
| G11 | Baris pendapatan jurnal kehilangan dimensi | Project Revenue selalu 0 | 4 |
| G12 | Budget tidak menulis audit log | Tidak ada jejak perubahan anggaran | 5 |
| G13 | Tidak ada `sync_budget_permissions` migration | Permission hanya sampai lewat seeder | 6 |
| G14 | `ModuleKey` di `useTabStore.ts` tanpa `'budget'` | Modul dipakai lewat cast, lolos type-check | 7 |

---

## 8. MUST HAVE / SHOULD HAVE / FUTURE

**MUST HAVE** — fase 1–8

Unified budget line multidimensi · Budget vs Actual lintas dimensi · Variance & Utilization
dengan definisi eksplisit · Cost Center hierarkis · Generic Project Budget · Project
Profitability & Margin · Cash Budget · Versioning/Revisi · Agregasi & drill-down · 16 reporting
view · Perbaikan 4 cacat perilaku.

**SHOULD HAVE** — dikerjakan bila fase induknya lancar

Pemerataan anggaran tahunan per bulan sebagai opsi tampilan (`allocation=even`) ·
Export CSV di seluruh view · Budget dashboard dengan KPI tile.

**FUTURE** — jangan diimplementasikan sekarang

Forecast · Rolling Budget · Flexible Budget · Scenario Budget · Multi-year Budget ·
What-if Analysis · Cash timing lewat termin pembayaran · Multi-company consolidation ·
Scoping user↔departemen.

Desain fase 1–8 tidak menghalangi satu pun di antaranya. Lihat bagian FUTURE EXTENSION di
`phase-8-dokumentasi.md`.

---

## Acceptance criteria

Dokumen ini disetujui pemilik produk sebelum fase 1 dimulai.
