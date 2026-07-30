# Frontend `main` Catch-Up — Checklist Review Manual

> **Konteks**: per 2026-07-29, local `main` di `frontend/` (device ini) tertinggal **18 commit** dari `origin/main`. Commit-commit ini kemungkinan besar hasil kerja dari PC lain yang sudah di-push & merge ke `main`, tapi belum pernah di-`pull` atau direview di device ini. Branch kerja lain (`feat/reports-expansion`) sudah sinkron — file ini khusus untuk review manual isi `main`.
>
> **Tujuan**: menelusuri satu per satu perubahan sebelum/ sesudah pull `main`, memastikan tidak ada regresi, konvensi ter-follow, dan progress lintas-PC ini benar-benar dipahami sebelum dilanjutkan.
>
> **Rentang commit**: `43ce630..4e4cef4` (18 commit, `git log main..origin/main --oneline` di `frontend/`).

## Cara pakai

1. Kerjakan area demi area sesuai urutan tabel ledger (urutan kira-kira kronologis).
2. Untuk tiap area: `git show <hash>` atau `git diff main origin/main -- <path>` untuk lihat isi perubahan, baca file kunci, centang item checklist.
3. Update kolom **Status** di ledger (`⬜ Belum` → `🔄 Berjalan` → `✅ Selesai`) + catat temuan di kolom **Catatan**.
4. Setelah semua area ✅ dan tidak ada temuan blocking → aman untuk `git pull` / merge `main` ke branch kerja lokal.
5. Kalau ada temuan (bug, konvensi dilanggar, breaking change) — catat di kolom Catatan, jangan diam-diam diperbaiki di file ini; tindak lanjuti di repo `frontend`.

## Progress Ledger

| # | Area | Commit | Status | Catatan |
|---|------|--------|--------|---------|
| 1 | Navigasi Shell (GAP-11) + Reports Restructure (Design-I2) | `4e4cef4`, `921d8f7` | ⬜ Belum | |
| 2 | Reports — Ledger/Filter/Export/Warnings (Phase 36) | `ceec34a`, `4c0f774`, `6abb932`, `14af003`, `5274e3b` | ⬜ Belum | |
| 3 | Budget Module Baru (Phase 40/41) | `93d2da6`, `6e5836a` | ⬜ Belum | |
| 4 | Purchase Module — Adapter Boundary (Phase 30) | `43ce630` | ⬜ Belum | |
| 5 | Inventory & AP (Phase 32) | `75fbf8b`, `88d62a2` | ⬜ Belum | |
| 6 | Fixed Assets (Phase 33–34) | `3fdc43c`, `e0756f4` | ⬜ Belum | |
| 7 | Accounting Period End (Phase 35) | `a81d181` | ⬜ Belum | |
| 8 | Settings, Users, Access, Dashboard (Phase 37–38) | `16bf845`, `42c5f16` | ⬜ Belum | |
| 9 | Account Mapping & Onboarding (a11y + fix) | `60ed2dc`, `5274e3b` | ⬜ Belum | |
| 10 | Shared Components Cross-cutting | tersebar (lihat area 10) | ⬜ Belum | |
| 11 | Sanity Check Akhir (build, docs, env) | semua | ⬜ Belum | |

> Status yang boleh: `⬜ Belum`, `🔄 Berjalan`, `✅ Selesai`, `⚠️ Ada Temuan`.

---

## Area 1 — Navigasi Shell (GAP-11) + Reports Restructure (Design-I2)

**Commit**: `4e4cef4` (Design-I2 Phase 1-4), `921d8f7` (GAP-11 refactor navigasi shell)

**File kunci**:
- `src/components/shared/layout/AppShell.tsx` (−101 baris, banyak dihapus)
- `src/components/shared/layout/PrimaryTabs.tsx`, `SecondaryTabs.tsx`, `RibbonPanel.tsx`
- `src/stores/useTabStore.ts` (baru +10 baris)
- `src/modules/reports/constants/reportCategories.ts` (baru)
- `src/modules/reports/pages/ReportCategoryPage.tsx`, `components/ReportDomainPanel.tsx` (baru)
- `src/modules/reports/pages/ReportIndexPage.tsx` (refactor besar, −70 baris)
- `src/router/moduleConfig.ts`, `src/modules/reports/routes.tsx`
- `docs/gap_docs/gap-11-state-only-navigation-shell.md` (dokumentasi keputusan)

**Checklist**:
- [ ] Baca `gap-11-state-only-navigation-shell.md` — pahami *kenapa* navigasi shell diubah jadi "state-only" (apa masalah lama yang dipecahkan).
- [ ] Bandingkan `AppShell.tsx` sebelum vs sesudah — pastikan penghapusan 101 baris logic dipindah ke `useTabStore.ts`, bukan hilang begitu saja.
- [ ] Cek `reportCategories.ts` — ini jadi single source of truth kategori laporan. Pastikan tidak ada kategori/route yang hilang dibanding `ReportIndexPage.tsx` versi lama.
- [ ] Jalankan aplikasi, buka menu Reports → pastikan tiap kategori ribbon menampilkan `ReportDomainPanel` dengan kartu laporan yang benar.
- [ ] Cek tab switching (Primary/Secondary tabs) masih berfungsi normal setelah refactor `useTabStore`.
- [ ] Pastikan tidak ada route lama yang jadi broken link (cek `router/moduleConfig.ts` menyeluruh).

---

## Area 2 — Reports: Ledger / Filter / Export / Warnings (Phase 36)

**Commit**: `ceec34a`, `4c0f774`, `6abb932`, `14af003`, `5274e3b`

**File kunci**:
- `src/modules/reports/pages/AccountLedgerPage.tsx` (baru, +221 baris)
- `src/modules/reports/pages/CashFlowPage.tsx`, `TrialBalancePage.tsx`, `GeneralLedgerPage.tsx`, `ReconciliationPage.tsx`, `BalanceSheetPage.tsx`, `ProfitLossPage.tsx` (refactor)
- `src/modules/reports/components/ReportFilterParameter.tsx`, `ReportError.tsx` (baru)
- `src/modules/reports/services/reportsApi.ts`, `types/reports.types.ts` (banyak endpoint & tipe baru)
- `src/lib/exportCsv.ts` (baru, util export)
- `src/modules/accounting/pages/JournalFormPage.tsx`, `types/journalEntry.types.ts` — threading `warnings[]` dari response posting jurnal
- `src/modules/sales/services/arApi.ts`, `types/ar.types.ts` — fix adapter AR aging

**Checklist**:
- [ ] Cek `reportsApi.ts` — pastikan **adapter boundary** dijaga (aturan Audit-12 A12-12): tidak ada page yang baca `res.data.foo` mentah, semua lewat adapter yang menormalkan ke `reports.types.ts`.
- [ ] Buka tiap halaman laporan yang disebut di atas satu per satu, coba filter parameter (`ReportFilterParameter`) dan export CSV (`exportCsv.ts`) — pastikan hasil export sesuai data yang tampil di tabel.
- [ ] Cek `ReportError.tsx` dipakai konsisten untuk error state di semua halaman laporan yang diubah.
- [ ] Trigger posting jurnal yang menghasilkan warning (mis. akun belum di-mapping) → pastikan `warnings[]` muncul di UI `JournalFormPage.tsx`, bukan cuma di response API.
- [ ] Cek AR Aging report — bandingkan angka sebelum/sesudah fix adapter di `arApi.ts` (kemungkinan ada bug lama yang diperbaiki).
- [ ] Baca `docs/gap_docs/gap-10-audit-13-remediation-roadmap.md` bagian A13-232 s/d A13-253 — cocokkan tiap item dengan implementasi aktual.

---

## Area 3 — Budget Module Baru (Phase 40 Backend / 41 Frontend)

**Commit**: `93d2da6` (plan/design docs), `6e5836a` (frontend implementation)

**File kunci** (modul baru sepenuhnya):
- `src/modules/budget/pages/BudgetPeriodListPage.tsx`, `BudgetPeriodFormPage.tsx`, `BudgetPeriodDetailPage.tsx`
- `src/modules/budget/pages/BudgetSubmissionPage.tsx`, `BudgetComparisonPage.tsx`
- `src/modules/budget/components/BudgetLineEditor.tsx`, `BudgetApprovalActions.tsx`, `BudgetConsolidationTable.tsx`, `BudgetStatusBadge.tsx`
- `src/modules/budget/services/budgetApi.ts`, `types/budget.types.ts`, `routes.tsx`
- `docs/gap_docs/gap-12-budget-module.md`, `docs/prompt/prompt-phase-40-budget-backend.md`, `prompt-phase-41-budget-frontend.md`

**Checklist**:
- [ ] Baca `gap-12-budget-module.md` — pahami alur bisnis budget (submission → approval → consolidation → comparison).
- [ ] **Cek dependency backend**: modul ini butuh endpoint dari `laravel_backend` (Phase 40). Pastikan versi backend yang jalan di device ini juga sudah include Phase 40 (`laravel_backend` main juga tertinggal 12 commit — cek apakah budget backend termasuk).
- [ ] Coba alur end-to-end: buat Budget Period → isi line item (`BudgetLineEditor`) → submit (`BudgetSubmissionPage`) → approve/reject (`BudgetApprovalActions`) → lihat consolidation table & comparison page.
- [ ] Cek routing baru terdaftar dengan benar di `src/router/index.tsx` dan muncul di `ReportIndexPage.tsx`/menu terkait (ada +5 baris di `ReportIndexPage.tsx` dari commit ini).
- [ ] Cek permission/role guard — siapa saja yang boleh submit vs approve budget.

---

## Area 4 — Purchase Module: Adapter Boundary (Phase 30)

**Commit**: `43ce630`

**File kunci**:
- `src/modules/purchase/services/*Adapter.ts` (baru: `goodsReceiptAdapter`, `purchaseOrderAdapter`, `purchaseRequestAdapter`, `purchaseReturnAdapter`, `vendorBillAdapter`, `vendorDepositAdapter`, `vendorPaymentAdapter`)
- `src/modules/purchase/pages/VendorBillFormPage.tsx` (+328/−146, perubahan besar)
- `src/components/shared/document/ConfirmDialog.tsx` (baru)
- `src/modules/purchase/schemas/vendorBillSchema.ts` (baru validasi)

**Checklist**:
- [ ] Pahami pola baru: tiap entity Purchase sekarang punya file `*Adapter.ts` terpisah dari `*Api.ts` — cek konsisten dipakai di semua list/form page terkait.
- [ ] Buka `VendorBillFormPage.tsx` — ini paling banyak berubah, jalankan alur create/edit vendor bill secara manual, termasuk validasi `vendorBillSchema.ts` baru.
- [ ] Cek `ConfirmDialog.tsx` dipakai untuk konfirmasi aksi (void/delete/submit) di halaman-halaman Purchase — pastikan tidak ada dialog konfirmasi lama yang duplikat/konflik.
- [ ] Cek semua `use*List.ts` hooks (GoodsReceipt, PurchaseOrder, PurchaseRequest, dst) — pastikan pagination/filter tetap jalan setelah refactor adapter.
- [ ] Baca `docs/tracking/phase-30-completion-report.md` untuk daftar definition-of-done resmi, cocokkan dengan hasil cek manual.

---

## Area 5 — Inventory & AP (Phase 32)

**Commit**: `75fbf8b`, `88d62a2`

**File kunci**:
- `src/modules/inventory/pages/StockAdjustment{List,Form}Page.tsx`, `StockMovement{List,Form}Page.tsx`, `StockOpname{List,Form}Page.tsx`, `StockBalance{List,Detail}Page.tsx`
- `src/modules/inventory/services/stockBalanceApi.ts`, schemas terkait
- `src/modules/purchase/pages/ApAgingPage.tsx`, `ApReconciliationPage.tsx`, `ApSummaryPage.tsx`
- `src/modules/purchase/services/apAdapters.ts` (baru, +222 baris)

**Checklist**:
- [ ] Jalankan alur Stock Adjustment & Stock Opname end-to-end (create → submit → lihat efek ke Stock Balance).
- [ ] Cek `apAdapters.ts` dipakai di ketiga halaman AP (Aging/Reconciliation/Summary) — bandingkan angka rekonsiliasi sebelum/sesudah.
- [ ] Baca `docs/tracking/phase-32-completion-report.md` untuk checklist resmi fase ini.

---

## Area 6 — Fixed Assets (Phase 33–34)

**Commit**: `3fdc43c`, `e0756f4`

**File kunci**:
- `src/modules/fixed-assets/pages/FixedAssetCategoryPage.tsx`, `FixedAssetFormPage.tsx` (+261 baris total dari kedua commit)
- `src/modules/fixed-assets/schemas/fixedAssetSchema.ts`, `types/fixedAsset.types.ts` (baru)
- `src/modules/master-data/services/coaApi.ts` (terkait mapping akun)
- `docs/gap_docs/gap-11-state-only-navigation-shell.md` (entri baru terkait fixed assets)

**Checklist**:
- [ ] Coba create/edit Fixed Asset penuh — cek validasi baru di `fixedAssetSchema.ts` (field apa saja yang jadi wajib/berubah).
- [ ] Cek kategori asset baru bisa dibuat dan muncul di dropdown form asset.
- [ ] Cek integrasi dengan `coaApi.ts` — pastikan mapping akun default (akumulasi penyusutan, dst) benar.

---

## Area 7 — Accounting Period End (Phase 35)

**Commit**: `a81d181`

**File kunci**:
- `src/modules/accounting/pages/PeriodEndPage.tsx` (+147/−55, refactor besar)
- `src/modules/accounting/services/periodEndApi.ts`

**Checklist**:
- [ ] Jalankan proses tutup periode (period-end close) end-to-end, perhatikan pesan error/warning yang ditampilkan.
- [ ] Bandingkan UI lama vs baru — pastikan tidak ada langkah yang hilang dari proses closing.
- [ ] Baca `docs/tracking/phase-35-completion-report.md`.

---

## Area 8 — Settings, Users, Access, Dashboard (Phase 37–38)

**Commit**: `16bf845`, `42c5f16`

**File kunci**:
- `src/modules/dashboard/pages/DashboardPage.tsx`
- `src/modules/settings/pages/{AccountingPeriodPage,CompanySettingsPage,TransactionSettingsPage,UsersPage,RolesPage,InvitationsPage,AccessAuditPage,MyPreferencesPage}.tsx`
- `src/components/shared/document/VoidConfirmDialog.tsx`, `src/components/shared/form/SearchableSelect.tsx` (a11y fixes)

**Checklist**:
- [ ] Cek Dashboard — apa 30 baris yang berubah (widget baru? angka baru?).
- [ ] Cek tiap halaman Settings yang disebut — fokus ke a11y (dialog descriptions, label form) dari commit `42c5f16`, pastikan tidak ada regresi visual/fungsional.
- [ ] Cek `UsersPage.tsx` paling banyak berubah (+75/-40 lalu +10/-3) — jalankan alur invite/edit/nonaktifkan user.
- [ ] Cek `VoidConfirmDialog` & `SearchableSelect` dipakai di halaman lain juga (shared component) — pastikan perubahan a11y tidak break halaman yang memakainya di luar Settings.

---

## Area 9 — Account Mapping & Onboarding (a11y + fix)

**Commit**: `60ed2dc`, `5274e3b`

**File kunci**:
- `src/modules/onboarding/components/steps/Step3AccountMapping.tsx` (+185/−94, refactor besar)
- `src/modules/onboarding/services/onboardingApi.ts`
- `src/modules/master-data/pages/AccountMappingPage.tsx`
- `src/modules/settings/pages/AccountMappingSettingsPage.tsx`
- `src/components/shared/feedback/SessionWarningDialog.tsx`

**Checklist**:
- [ ] Jalankan flow onboarding dari awal sampai Step 3 (Account Mapping) — pastikan tidak ada regresi dibanding versi lama.
- [ ] Cek `AccountMappingPage.tsx` dan `AccountMappingSettingsPage.tsx` — dua halaman ini mirip, pastikan perubahan konsisten di keduanya (tidak fix di satu tempat doang).
- [ ] Baca `docs/gap_docs/gap-10-audit-13-remediation-roadmap.md` — commit ini nambah 191 baris ke file itu, cek item apa yang diklaim selesai.

---

## Area 10 — Shared Components Cross-cutting

**Tersebar di banyak commit** — komponen ini dipakai lintas modul, jadi regresi di sini berdampak luas.

**File kunci**:
- `src/components/shared/document/ConfirmDialog.tsx` (baru, Phase 30)
- `src/components/shared/document/VoidConfirmDialog.tsx` (Phase 38, a11y)
- `src/components/shared/form/SearchableSelect.tsx` (Phase 38, a11y)
- `src/components/shared/feedback/EmptyState.tsx`, `SessionWarningDialog.tsx`
- `src/components/shared/layout/Topbar.tsx`
- `src/lib/exportCsv.ts`

**Checklist**:
- [ ] Untuk tiap komponen di atas, cari semua pemanggilnya (`grep -r` di `src/modules/`) dan pastikan API/props yang berubah sudah di-update di semua tempat pakai, bukan cuma di modul yang jadi fokus commit.
- [ ] Cek `SearchableSelect` khususnya — dipakai sangat luas (dropdown akun, produk, dst), test keyboard navigation & screen reader label setelah perubahan a11y.

---

## Area 11 — Sanity Check Akhir

- [ ] `npm run build` (atau `pnpm build`) di `frontend/` — 0 error TypeScript.
- [ ] `npm run lint` — 0 violation baru.
- [ ] Cek `.env` — commit `43ce630` menambah 3 baris ke `.env`; pastikan device ini juga punya env var yang sama (jangan sampai fitur baru butuh env var yang belum di-set lokal).
- [ ] Cek `docs/struktur_frontend.md` (banyak diupdate di sepanjang 18 commit ini) — sinkronkan dengan `Finlite_knowladge/reference/struktur_frontend.md` (mirror, wajib dijaga sinkron per `reference/README.md`).
- [ ] Baca semua `docs/tracking/phase-3{0,1,2,3,4,5,7}-completion-report.md` yang baru — cocokkan klaim "selesai" dengan hasil review manual di atas.
- [ ] Setelah semua ✅: `git pull` / merge `main` ke branch kerja, lalu jalankan smoke test menyeluruh sekali lagi sebelum lanjut kerja baru di atasnya.

---

## Catatan Umum

- Dokumen ini adalah snapshot per **2026-07-29** (18 commit `43ce630..4e4cef4`). Kalau `origin/main` sudah maju lagi saat kamu mengerjakan ini, jalankan ulang `git log main..origin/main --oneline` untuk cek apakah ada commit baru yang belum masuk daftar ini.
- `laravel_backend` juga tertinggal 12 commit dari `origin/main` dengan tema paralel (budget backend, account-mapping, reports) — beberapa item di atas (terutama **Area 3 — Budget**) butuh backend yang sudah update juga. Pertimbangkan buat checklist serupa untuk `laravel_backend` kalau mau review dua sisi sekaligus.
