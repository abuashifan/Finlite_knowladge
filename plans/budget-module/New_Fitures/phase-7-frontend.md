# Phase 7 — Frontend

> Prasyarat: fase 6 selesai, dan `phase-0.1-reusable-line-items-component.md` sudah
> memindahkan `BudgetLineEditor.tsx` ke `LineItemsTable` — merapikan basis komponen sebelum
> fase ini menambah fitur di atasnya.
> Baca `frontend/AGENTS.md` sebelum menyentuh apa pun di `/workspace/frontend/`.

## Objective

**Satu antarmuka anggaran terpadu** dengan filter dimensi dan mode, bukan enam belas halaman
terpisah — cerminan langsung dari "one engine, many views" di sisi UI.

Menutup **G14**.

---

## Konsep antarmuka

Satu halaman `BudgetAnalysisPage` dengan:

**Filter dimensi** — Fiscal Year · Periode Anggaran · Akun · Cost Center · Proyek · Versi
**Mode** — Summary · Detail · Variance · Actual · *Forecast (FUTURE, tidak dibuat)*
**Grouping** — pilih urutan dimensi; baris bisa di-*expand* untuk drill-down

Halaman khusus hanya untuk yang bentuknya memang beda: riwayat versi, ringkasan finansial
proyek, cash budget, dan dashboard.

---

## Existing files affected

| File | Perubahan |
|---|---|
| `src/modules/budget/services/budgetApi.ts` | + method endpoint baru. Pola `http.get<unknown, ApiResponse<T>>` — **jangan unwrap dua kali**; interceptor `src/services/http.ts` sudah mengembalikan `response.data`. Itu cacat A yang sudah diperbaiki, jangan diulang. |
| `src/modules/budget/types/budget.types.ts` | + `BudgetAnalysisRow`, `BudgetAnalysisParams`, `BudgetVersion`, `ProjectFinancialSummary`, `CashBudget`, `BudgetState`, `BudgetDirection` |
| `src/modules/budget/components/BudgetLineEditor.tsx` | + kolom **Cost Center** (`SearchableSelect` → `departemenApi`); badge `direction` otomatis dari akun terpilih; validasi `period_month` tetap `^\d{4}-(0[1-9]\|1[0-2])$` |
| `src/modules/budget/pages/BudgetComparisonPage.tsx` | `<table>` manual → `DataTable`; adopsi `ReportCompactBar` + `useReportParams` seperti 42 halaman laporan lain. Komentar di file sudah mencatat penyimpangan ini; ini yang menutupnya. |
| `src/modules/budget/components/BudgetStatusBadge.tsx` | + status `superseded`; ganti map lokal dengan kelas token `status-*` di `src/index.css` |
| `src/modules/budget/pages/BudgetSubmissionPage.tsx` | + tombol **Revisi** (dibungkus `PermissionGuard permission="budgets.revise"`), tampilkan `version_no` dan badge "Versi Aktif" |
| `src/modules/budget/pages/BudgetPeriodDetailPage.tsx` | Tab lokal buatan tangan → `components/ui/tabs` |
| `src/router/moduleConfig.ts` | + ribbon item: Analisis Anggaran, Anggaran Proyek, Cash Budget, Dashboard |
| `src/stores/useTabStore.ts` | **+ `'budget'` ke union `ModuleKey`** (G14) — sekarang dipakai lewat cast di `Topbar.tsx:40`, lolos type-check tanpa dijaga |
| `src/modules/reports/constants/reportCategories.ts` | + entri untuk tiap report key baru, domain `financial`, `permission: 'budgets.view'` |
| `src/modules/reports/constants/reportKeyRoutes.ts` | + pemetaan supaya laporan bisa disimpan lewat `SaveReportButton` |
| `src/modules/accounting/types/journalEntry.types.ts` | `BudgetWarning` + `state`, `direction`, `matched_scope` (fase 3) |

`src/components/shared/layout/Topbar.tsx` sudah punya entri `budget: Wallet` di `MODULE_ICONS`
— cukup diverifikasi, tidak perlu diubah.

---

## New files

### `src/modules/budget/pages/`

| File | Isi |
|---|---|
| `BudgetAnalysisPage.tsx` | Antarmuka terpadu: `ReportCompactBar` + `ReportParameterModal` untuk filter, `DataTable` dengan baris yang bisa di-*expand* untuk drill-down, `ReportToolButton` untuk Export CSV |
| `BudgetVersionHistoryPage.tsx` | Rantai versi + total per versi + alasan revisi + siapa/kapan |
| `ProjectFinancialSummaryPage.tsx` | Revenue / Cost / Profit / Margin, budget vs actual, plus catatan keterbatasan invoice lama (fase 6 §3) |
| `CashBudgetPage.tsx` | Beginning + Inflow − Outflow = Ending, dikelompokkan per `cash_flow_section`, plus catatan asumsi akrual |
| `BudgetDashboardPage.tsx` | KPI tile + grafik, meniru `modules/dashboard/components/KpiCards.tsx` dan `SalesPurchaseChart.tsx` (Recharts sudah terpasang) |

### `src/modules/budget/hooks/` — folder baru

`useBudgetAnalysis.ts` · `useBudgetVersions.ts` · `useProjectFinancials.ts` · `useCashBudget.ts`

Modul budget belum punya folder `hooks/` sama sekali; ini menutup penyimpangan dari
`spec-03-folder-structure`. Pola mengikuti `modules/fixed-assets/hooks/`: query key array
`['budget', 'analysis', params]`, satu hook mutasi yang mengembalikan beberapa mutation dengan
`invalidate` bersama.

### `src/modules/budget/schemas/` — folder baru

`budgetSchema.ts` — memindahkan skema Zod yang sekarang ditulis inline di
`BudgetPeriodFormPage.tsx`, ditambah skema untuk baris anggaran dan form revisi.

---

## Komponen yang dipakai ulang — jangan bikin baru

| Kebutuhan | Komponen |
|---|---|
| Shell halaman daftar | `shared/layout/WorkspaceLayout.tsx` |
| Shell form | `shared/layout/FormLayout.tsx` + `FormSaveActions.tsx` |
| Tabel | `shared/table/DataTable.tsx` (+ `TablePagination`, `useListSort`) |
| Filter | `modules/reports/components/ReportCompactBar.tsx` + `ReportParameterModal.tsx` |
| Pilih master data | `shared/form/SearchableSelect.tsx` (`coaApi.search`, `departemenApi.search`, `proyekApi.search`) |
| Input nominal | `shared/form/AmountInput.tsx` |
| Badge status | `shared/document/DocumentStatusBadge.tsx` + kelas `status-*` |
| Konfirmasi | `shared/document/ConfirmDialog.tsx` |
| Cek permission | `shared/PermissionGuard.tsx` + `hooks/usePermission.ts` |
| Format angka | `lib/utils.ts` — `formatCurrency`, `formatNumber`, `formatDate` |
| Export | `lib/exportCsv.ts` + `modules/reports/components/ReportToolButton.tsx` |
| Cetak | `modules/reports/components/ReportPrintDocument.tsx` |

**Drill-down belum punya primitif bersama di codebase.** Preseden terdekat: `rowSpan` grouping
di `modules/budget/components/BudgetConsolidationTable.tsx` dan toggle summary↔detail di
`modules/reports/pages/GeneralLedgerPage.tsx`. Pilih salah satu dan konsisten —
**jangan bikin komponen baru**.

---

## Database / API changes

Tidak ada.

---

## Dependencies

Fase 6.

---

## Risks

| Risiko | Mitigasi |
|---|---|
| `createMemoryRouter` — `navigate()` langsung membuat tab bar tidak sinkron dan halaman hilang saat pindah tab | Navigasi wajib lewat `useRecordTab` / `openRecordTab` / `replaceRecordTab`. Ini cacat F yang sudah diperbaiki di rencana sebelumnya; jangan diulang. |
| Godaan membuat komponen tabel drill-down baru | Pakai salah satu preseden yang ada. Guardrail `frontend/AGENTS.md`: "no komponen baru bila sudah ada". |
| `budgetApi` kembali unwrap dua kali | Semua method wajib memakai generic kedua `ApiResponse<T>`; tanpa generic, tipenya `any` dan cacat A bisa lolos build lagi. |
| Halaman terlalu padat di layar pendek | `spec-23`: pakai `h-dvh`/`min-h-dvh`, sediakan mode ringkas di `@media (max-height: 620px)`. |
| Angka tidak sejajar | `font-variant-numeric: tabular-nums` sudah global di `index.css`, tapi tetap verifikasi kolom nominal rata kanan. |

---

## Testing

Tidak ada test runner frontend di repo ini. Verifikasi lewat:

```bash
cd /workspace/frontend
npm run build      # WAJIB — lebih lengkap dari `rtk tsc`
npm run lint
```

Ditambah prosedur manual di `phase-8-dokumentasi.md`.

Sebelum mengedit halaman existing, **salin versi lamanya ke scratchpad** supaya bisa dibatalkan.

---

## Hasil implementasi — 2026-08-14

Status: **selesai secara kode**; verifikasi browser belum.

### File baru

`pages/`: `BudgetAnalysisPage.tsx` · `CashBudgetPage.tsx` · `ProjectFinancialSummaryPage.tsx` ·
`BudgetVersionHistoryPage.tsx` · `BudgetDashboardPage.tsx`
`hooks/` (folder baru): `useBudgetAnalysis.ts` · `useBudgetVersions.ts` ·
`useProjectFinancials.ts` · `useCashBudget.ts`
`schemas/` (folder baru): `budgetSchema.ts`

### File yang berubah

`budgetApi.ts` (+10 method, semua dengan generic kedua `ApiResponse<T>`) ·
`budget.types.ts` (+11 tipe) · `BudgetLineEditor.tsx` (+kolom Cost Center) ·
`BudgetStatusBadge.tsx` (+`superseded`) · `BudgetSubmissionPage.tsx` (+Versi, badge Versi
Aktif, tombol Revisi ber-`PermissionGuard`, alasan revisi) · `routes.tsx` (+5 rute) ·
`moduleConfig.ts` (+4 item ribbon) · `useTabStore.ts` (**+`'budget'` ke `ModuleKey`** — G14) ·
`reportCategories.ts` (+7 entri) · `reportKeyRoutes.ts` (+9 entri) ·
`journalEntry.types.ts` (fase 3).

### Penyimpangan

1. **`BudgetComparisonPage.tsx` tidak dipindah ke `DataTable`.** Ada di §Existing files
   affected tapi tidak di acceptance criteria. `DataTable` menuntut `id` per baris + paginasi
   server-side; baris laporan ini hasil agregasi tanpa id. Halaman analisis baru memakai pola
   tabel manual yang sama, jadi konversinya churn berisiko tanpa manfaat.
2. **Tab lokal `BudgetPeriodDetailPage` tidak dipindah ke `components/ui/tabs`** — kosmetik,
   di luar acceptance criteria.
3. **Drill-down memakai pola breadcrumb + klik baris**, bukan baris yang bisa di-*expand*.
   Rencana mengizinkan memilih salah satu preseden; ini yang paling dekat dengan
   `GeneralLedgerPage` dan tidak butuh komponen baru.
4. **`ReportCompactBar`/`ReportParameterModal` tidak dipakai** — keduanya terikat
   `useReportParams`, yang parameternya (start/end date + akun) tidak cocok dengan parameter
   anggaran (periode anggaran, group_by, versi, alokasi). Filter dipasang lewat `toolbar`
   `WorkspaceLayout`, pola yang sama dengan `BudgetComparisonPage` yang sudah ada.

### Verifikasi

```
npm run build   → ✅ 0 error
npm run lint    → ✅ No issues found
grep -rn "as ModuleKey" src/  → 1 hasil di Topbar.tsx:80, generik untuk semua modul
                                (bukan cast khusus 'budget') — G14 tertutup
```

**Belum dijalankan:** verifikasi di browser (drill-down 4 level, angka konsisten tiap level,
tampilan di viewport pendek). Tidak ada test runner frontend di repo ini.

---

## Acceptance criteria

1. Drill-down Total → Cost Center → Proyek → Akun berjalan di browser dengan angka konsisten
   di tiap level.
2. Satu halaman analisis melayani view #1–#9 lewat filter, bukan sembilan halaman.
3. `npm run build` dan `npm run lint` hijau, nol error.
4. `ModuleKey` di `useTabStore.ts` memuat `'budget'`; tidak ada cast `as ModuleKey` yang tersisa
   untuk modul ini.
5. Tidak ada komponen UI baru di `src/components/`.
6. `frontend/docs/struktur_frontend.md` diperbarui dengan semua file baru.
