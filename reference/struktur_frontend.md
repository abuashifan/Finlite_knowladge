# Struktur Frontend

Peta ringkas untuk AI agent di `/workspace/frontend`.

Gunakan file ini dulu saat mencari lokasi file. Fokus ke file yang ditulis di bawah; jangan buang token untuk menelusuri `node_modules/` atau asset build kecuali memang sedang debug build.

## Root

```text
.
|____.claude/
| |____settings.local.json
|____.env.example
|____.gitignore
|____AGENTS.md
|____CLAUDE.md
|____README.md
|____components.json
|____praproductions-docs/
| |____frontend-backend-gap-audit-2026-06-15.md
|____docs/
| |____AGENT_ENTRY_POINT.md
| |____audit-design-spec-2026-06-14.md
| |____audit_docs/
| | |____audit-00-backend-audit-index.md
| | |____audit-01-architecture-overview.md
| | |____audit-02-api-route-map.md
| | |____audit-03-database-erd-and-models.md
| | |____audit-04-sales-workflow-audit.md
| | |____audit-05-purchase-workflow-audit.md
| | |____audit-06-inventory-workflow-audit.md
| | |____audit-07-accounting-and-reporting-audit.md
| | |____audit-08-business-rules-and-validation-map.md
| | |____audit-09-risk-gap-and-improvement-backlog.md
| | |____audit-design-tablet-first.md
| | |____audit-10-ai-agent-context.md
| | |____audit-ar-account-mapping-erd.md
| | |____audit-coding-standards.md
| | |____audit-frontend-api-contract.md
| | |____audit-gap-completion-tracker.md
| | |____audit-tech-stack.md
| | |____audit-11-frontend-global-contract-map-16-06-26.md
| | |____audit-12-frontend-ux-workflow-audit-16-06-26.md
| | |____audit-13-manual-frontend-audit-tracker-17-06-26.md
| |____design_docs/
| | |____design-A1-topbar-ribbon.md
| | |____design-A2-ribbon-overflow-tablet.md
| | |____design-B-auth-pages.md
| | |____design-C1-datatable.md
| | |____design-C2-filter-sidebar.md
| | |____design-C3-searchable-select.md
| | |____design-C4-tablet-datatable-viewport.md
| | |____design-C5-filter-sidebar-tablet.md
| | |____design-D1-form-layout.md
| | |____design-D2-line-items-table.md
| | |____design-D3-bottom-action-bar.md
| | |____design-D4-form-summary.md
| | |____design-D5-document-locked-banner.md
| | |____design-D6-tablet-form-viewport.md
| | |____design-E2-toast.md
| | |____design-E3-void-dialog.md
| | |____design-E4-empty-state.md
| | |____design-E5-overlay-collision-rules.md
| | |____design-E6-focus-keyboard-accessibility.md
| | |____design-E7-status-badges.md
| | |____design-F1-onboarding-wizard.md
| | |____design-G-settings.md
| | |____design-H1-dashboard.md
| | |____design-H2-dashboard-tablet-landscape.md
| | |____design-I-reports.md
| | |____design-J1-tablet-landscape-shell.md
| | |____design-K-mobile-bottom-navigation.md
| | |____design-L-error-pages.md
| | |____design-M-print-export.md
| |____gap_docs/
| | |____gap-00-master-index.md
| | |____gap-01-p0-contract-fixes.md
| | |____gap-02-settings-access-mismatch.md
| | |____gap-03-missing-modules.md
| | |____gap-04-setup-wizard-refactor.md
| | |____gap-05-dashboard-no-backend.md
| | |____gap-06-report-gaps.md
| | |____gap-07-master-data-dto-contract.md
| | |____gap-08-transaction-dto-number-contract.md
| | |____gap-09-audit-12-ux-workflow-fixes.md
| | |____gap-10-audit-13-remediation-roadmap.md
| | |____gap-11-state-only-navigation-shell.md
| |____issue_docs/
| | |____issue-01-permission-keys.md
| | |____issue-02-ribbon-paths.md
| | |____issue-03-fiscal-year-http-methods.md
| | |____issue-04-bank-recon-methods.md
| | |____issue-05-settings-endpoints.md
| | |____issue-06-report-endpoint-fixes.md
| | |____issue-07-route-ribbon-canonical-map.md
| | |____issue-08-product-dto-and-table.md
| | |____issue-09-master-data-delete-actions.md
| | |____issue-10-journal-list-totals-and-account-labels.md
| | |____issue-11-dashboard-graceful-fallback.md
| | |____issue-12-searchable-select-selected-options-audit.md
| | |____issue-13-formatters-null-invalid-guard.md
| | |____issue-14-api-error-display-and-form-errors.md
| | |____issue-15-datatable-reuse-and-sticky-column-audit.md
| | |____issue-16-reports-runtime-contract.md
| | |____issue-17-stock-balance-dto-detail.md
| | |____issue-18-transaction-list-filters.md
| | |____issue-19-datatable-selection-bulk-void.md
| | |____issue-20-persistent-form-draft.md
| | |____issue-21-searchable-select-preload.md
| | |____issue-22-date-input-normalization.md
| | |____issue-23-primary-tab-close-all.md
| | |____issue-24-fixed-assets-ribbon-empty.md
| | |____issue-25-document-edit-mode-policy.md
| | |____issue-26-lint-debt-cleanup.md
| | |____issue-27-phase-24-runtime-router-foundation.md
| | |____issue-28-phase-25-master-data-account-mapping-canonical.md
| | |____issue-29-phase-26-accounting-foundation-opening-balance.md
| | |____issue-30-phase-27-cash-bank-contract-reconciliation.md
| | |____issue-31-phase-28-sales-transaction-contract.md
| | |____issue-32-phase-29-ar-subledger-reports.md
| | |____issue-33-phase-30-purchase-transaction-contract.md
| | |____issue-34-phase-31-ap-subledger-reports.md
| | |____issue-35-phase-32-inventory-integrity-workflow.md
| | |____issue-36-phase-33-fixed-assets-runtime-core.md
| | |____issue-37-phase-34-fixed-assets-lifecycle-reports.md
| | |____issue-38-phase-35-period-end-processing.md
| | |____issue-39-phase-36-financial-operational-reports.md
| | |____issue-40-phase-37-settings-access-dashboard-router.md
| | |____issue-41-phase-38-cross-cutting-ux-accessibility-consistency.md
| | |____issue-42-phase-39-full-regression-data-repair-audit-closure.md
| |____praproduction_docs/
| | |____CLAUDE.md
| | |____spec-01-project-context.md
| | |____spec-02-stack-and-dependencies.md
| | |____spec-03-folder-structure.md
| | |____spec-04-design-tokens.md
| | |____spec-05-layout-and-navigation.md
| | |____spec-06-responsive-rules.md
| | |____spec-07-component-library.md
| | |____spec-08-form-architecture.md
| | |____spec-09-table-and-list.md
| | |____spec-10-document-workflow.md
| | |____spec-11-permission-rules.md
| | |____spec-12-api-integration.md
| | |____spec-13-filter-and-search.md
| | |____spec-14-notification-rules.md
| | |____spec-15-module-patterns.md
| | |____spec-16-reports-module.md
| | |____spec-17-auth-and-company.md
| | |____spec-18-onboarding-wizard.md
| | |____spec-19-settings-module.md
| | |____spec-20-dashboard.md
| | |____spec-21-error-pages-and-print-export.md
| | |____spec-22-implementation-roadmap.md
| | |____spec-23-tablet-first-layout-rules.md
| | |____spec-24-auth-session-contract-clarifications.md
| | |____spec-25-viewport-list.md
| | |____spec-26-p0-contract-fixes.md
| | |____spec-27-settings-access-refactor.md
| | |____spec-28-fixed-assets-module.md
| | |____spec-29-opening-balance-module.md
| | |____spec-30-setup-wizard-refactor.md
| | |____spec-31-period-end-module.md
| | |____spec-32-master-data-dto-contract-fixes.md
| | |____spec-33-transaction-dto-number-contract.md
| | |____spec-34-route-ribbon-canonical-map.md
| | |____spec-35-shared-runtime-hardening.md
| | |____spec-36-audit-12-ux-workflow-fixes.md
| | |____spec-37-audit-13-remediation.md
| |____prompt/
| | |____prompt-00-master-index.md
| | |____prompt-guardrails-audit-11-implementation.md
| | |____prompt-guardrails-audit-13-implementation.md
| | |____prompt-phase-24-remediation-foundation-router.md
| | |____prompt-phase-25-master-data-account-mapping-canonical.md
| | |____prompt-phase-26-accounting-foundation-opening-balance.md
| | |____prompt-phase-27-cash-bank-contract-reconciliation.md
| | |____prompt-phase-28-sales-transaction-contract.md
| | |____prompt-phase-29-ar-subledger-reports.md
| | |____prompt-phase-30-purchase-transaction-contract.md
| | |____prompt-phase-30-completion-agent.md
| | |____prompt-phase-31-ap-subledger-reports.md
| | |____prompt-phase-32-inventory-integrity-workflow.md
| | |____prompt-phase-33-fixed-assets-runtime-core.md
| | |____prompt-phase-34-fixed-assets-lifecycle-reports.md
| | |____prompt-phase-35-period-end-processing.md
| | |____prompt-phase-36-financial-operational-reports.md
| | |____prompt-phase-37-settings-access-dashboard-router.md
| | |____prompt-phase-38-cross-cutting-ux-accessibility-consistency.md
| | |____prompt-phase-39-full-regression-data-repair-audit-closure.md
| | |____prompt-phase-1A-project-setup.md
| | |____prompt-phase-1B-auth-pages.md
| | |____prompt-phase-1C-app-shell-layout.md
| | |____prompt-phase-1C-section-state-connection.md
| | |____prompt-phase-1D-shared-components.md
| | |____prompt-phase-1E-error-onboarding.md
| | |____prompt-phase-2-master-data.md
| | |____prompt-phase-3-sales.md
| | |____prompt-phase-4-purchase.md
| | |____prompt-phase-5-inventory.md
| | |____prompt-phase-6-accounting-reports.md
| | |____prompt-phase-7-dashboard-settings.md
| | |____prompt-phase-8-p0-contract-fixes.md
| | |____prompt-phase-9-settings-access-refactor.md
| | |____prompt-phase-10-fixed-assets.md
| | |____prompt-phase-11-opening-balance.md
| | |____prompt-phase-12-setup-wizard.md
| | |____prompt-phase-13-period-end.md
| | |____prompt-phase-14-master-data-dto-contract-fixes.md
| | |____prompt-phase-15-transaction-dto-number-contract.md
| | |____prompt-phase-16-route-ribbon-canonical-map.md
| | |____prompt-phase-17-shared-runtime-hardening.md
| | |____prompt-guardrails-audit-12-implementation.md
| | |____prompt-phase-18-reports-contract-hardening.md
| | |____prompt-phase-19-stock-balance-contract-fixes.md
| | |____prompt-phase-20-filter-and-table-bulk-workflow.md
| | |____prompt-phase-21-persistent-form-drafts.md
| | |____prompt-phase-22-select-date-edit-mode-ux.md
| | |____prompt-phase-23-tabs-ribbon-lint-cleanup.md
| |____tracking/
| | |____phase-30-completion-report.md
| | |____phase-31-completion-report.md
| | |____phase-33-completion-report.md
| | |____2026-06-16-route-tabs-datatable-fixes.md
| | |____2026-06-16-workspace-document-number-alias-fix.md
| |____struktur_frontend.md
|____eslint.config.js
|____index.html
|____package-lock.json
|____package.json
|____postcss.config.js
|____public/
| |____favicon.svg
| |____icons.svg
|____src/
| |____App.css
| |____App.tsx
| |____assets/
| | |____hero.png
| | |____react.svg
| | |____vite.svg
| | |____illustrations/
| | | |____login-illustration.svg
| |____components/
| | |____shared/
| | | |____PermissionGuard.tsx
| | | |____document/
| | | | |____ConfirmDialog.tsx
| | | | |____DocumentActionBar.tsx
| | | | |____DocumentLockedBanner.tsx
| | | | |____documentEditPolicy.ts
| | | | |____DocumentStatusBadge.tsx
| | | | |____SystemGeneratedBadge.tsx
| | | | |____VoidConfirmDialog.tsx
| | | |____feedback/
| | | | |____EmptyState.tsx
| | | | |____ErrorBoundary.tsx
| | | | |____SessionWarningDialog.tsx
| | | | |____UnsavedFormsDialog.tsx
| | | |____form/
| | | | |____FieldError.tsx
| | | | |____FormSection.tsx
| | | | |____FormSummary.tsx
| | | | |____LineItemsTable.tsx
| | | | |____RecordNavButtons.tsx
| | | | |____SearchableSelect.tsx
| | | |____filter/
| | | | |____DateRangeFilterSection.tsx
| | | | |____ListSearchBar.tsx
| | | | |____MultiCheckboxFilter.tsx
| | | | |____dateRangeUtils.ts
| | | |____layout/
| | | | |____AppShell.tsx
| | | | |____FilterSidebar.tsx
| | | | |____FixedBottomBar.tsx
| | | | |____FormLayout.tsx
| | | | |____FormSaveActions.tsx
| | | | |____PrimaryTabs.tsx
| | | | |____RibbonPanel.tsx
| | | | |____SecondaryTabs.tsx
| | | | |____Topbar.tsx
| | | | |____WorkspaceLayout.tsx
| | | |____table/
| | | | |____BulkActionBar.tsx
| | | | |____DataTable.tsx
| | | | |____TablePagination.tsx
| | |____ui/
| | | |____alert-dialog.tsx
| | | |____alert.tsx
| | | |____badge.tsx
| | | |____button.tsx
| | | |____calendar.tsx
| | | |____checkbox.tsx
| | | |____dialog.tsx
| | | |____dropdown-menu.tsx
| | | |____form.tsx
| | | |____input.tsx
| | | |____label.tsx
| | | |____popover.tsx
| | | |____scroll-area.tsx
| | | |____select.tsx
| | | |____separator.tsx
| | | |____skeleton.tsx
| | | |____switch.tsx
| | | |____table.tsx
| | | |____tabs.tsx
| | | |____textarea.tsx
| | | |____toast.tsx
| | | |____toaster.tsx
| | | |____tooltip.tsx
| |____hooks/
| | |____use-toast.ts
| | |____useCompanySession.ts
| | |____useCompanySettings.ts
| | |____useDocumentActions.ts
| | |____useOpenPrimaryTab.ts
| | |____usePermission.ts
| | |____usePersistentFormDraft.ts
| | |____useRecordFormNavigation.ts
| | |____useRecordSequence.ts
| | |____useRecordTab.ts
| | |____useSessionTimeout.ts
| | |____useTabFormState.ts
| | |____useToast.ts
| | |____useUnsavedFormTracker.ts
| | |____useViewMode.ts
| |____index.css
| |____lib/
| | |____apiError.ts
| | |____companyScope.ts
| | |____companySession.ts
| | |____constants.ts
| | |____exportCsv.ts
| | |____formDraftStorage.ts
| | |____utils.ts
| |____main.tsx
| |____modules/
| | |____accounting/
| | | |____hooks/
| | | | |____useFiscalYear.ts
| | | | |____useJournalEntryList.ts
| | | | |____usePeriodEnd.ts
| | | |____pages/
| | | | |____FiscalYearPage.tsx
| | | | |____JournalFormPage.tsx
| | | | |____JournalListPage.tsx
| | | | |____PeriodEndPage.tsx
| | | | |____PeriodLockPage.tsx
| | | |____routes.tsx
| | | |____schemas/
| | | | |____journalEntrySchema.ts
| | | |____services/
| | | | |____fiscalYearApi.ts
| | | | |____journalEntryApi.ts
| | | | |____periodEndApi.ts
| | | | |____periodLockApi.ts
| | | |____types/
| | | | |____fiscalYear.types.ts
| | | | |____journalEntry.types.ts
| | |____auth/
| | | |____pages/
| | | | |____CompanyPickerPage.tsx
| | | | |____LoginPage.tsx
| | | |____schemas/
| | | | |____loginSchema.ts
| | | |____services/
| | | | |____authApi.ts
| | | | |____companyApi.ts
| | |____budget/
| | | |____components/
| | | | |____BudgetApprovalActions.tsx
| | | | |____BudgetConsolidationTable.tsx
| | | | |____BudgetLineEditor.tsx
| | | | |____BudgetStatusBadge.tsx
| | | |____pages/
| | | | |____BudgetComparisonPage.tsx
| | | | |____BudgetPeriodDetailPage.tsx
| | | | |____BudgetPeriodFormPage.tsx
| | | | |____BudgetPeriodListPage.tsx
| | | | |____BudgetSubmissionPage.tsx
| | | |____routes.tsx
| | | |____services/
| | | | |____budgetApi.ts
| | | |____types/
| | | | |____budget.types.ts
| | |____cash-bank/
| | | |____hooks/
| | | | |____useCashBankList.ts
| | | |____pages/
| | | | |____BankReconciliationFormPage.tsx
| | | | |____BankReconciliationListPage.tsx
| | | | |____BankTransferFormPage.tsx
| | | | |____BankTransferListPage.tsx
| | | | |____CashPaymentFormPage.tsx
| | | | |____CashPaymentListPage.tsx
| | | | |____CashReceiptFormPage.tsx
| | | | |____CashReceiptListPage.tsx
| | | |____routes.tsx
| | | |____schemas/
| | | | |____cashBankSchemas.ts
| | | |____services/
| | | | |____cashBankApi.ts
| | | |____types/
| | | | |____cashBank.types.ts
| | |____dashboard/
| | | |____components/
| | | | |____CashFlowChart.tsx
| | | | |____KpiCards.tsx
| | | | |____PendingDocumentAlerts.tsx
| | | | |____RecentActivity.tsx
| | | | |____SalesPurchaseChart.tsx
| | | |____hooks/
| | | | |____useDashboardData.ts
| | | |____pages/
| | | | |____DashboardPage.tsx
| | | |____services/
| | | | |____dashboardApi.ts
| | | |____types/
| | | | |____dashboard.types.ts
| | |____errors/
| | | |____ErrorPage.tsx
| | | |____MaintenancePage.tsx
| | | |____NetworkErrorPage.tsx
| | |____fixed-assets/
| | | |____hooks/
| | | | |____useFixedAssetCategories.ts
| | | | |____useFixedAssetList.ts
| | | | |____useFixedAssetMutations.ts
| | | |____pages/
| | | | |____FixedAssetCategoryPage.tsx
| | | | |____FixedAssetFormPage.tsx
| | | | |____FixedAssetListPage.tsx
| | | | |____reports/
| | | | | |____FixedAssetDepreciationReportPage.tsx
| | | | | |____FixedAssetDisposalsReportPage.tsx
| | | | | |____FixedAssetReconciliationReportPage.tsx
| | | | | |____FixedAssetRegisterReportPage.tsx
| | | | | |____FixedAssetReportTable.tsx
| | | |____routes.tsx
| | | |____schemas/
| | | | |____fixedAssetSchema.ts
| | | |____services/
| | | | |____fixedAssetApi.ts
| | | | |____fixedAssetCategoryApi.ts
| | | |____types/
| | | | |____fixedAsset.types.ts
| | |____inventory/
| | | |____components/
| | | |____hooks/
| | | | |____useStockAdjustmentList.ts
| | | | |____useStockBalanceList.ts
| | | | |____useStockMovementList.ts
| | | | |____useStockOpnameList.ts
| | | |____pages/
| | | | |____StockAdjustmentFormPage.tsx
| | | | |____StockAdjustmentListPage.tsx
| | | | |____StockBalanceDetailPage.tsx
| | | | |____StockBalanceListPage.tsx
| | | | |____StockMovementFormPage.tsx
| | | | |____StockMovementListPage.tsx
| | | | |____StockOpnameFormPage.tsx
| | | | |____StockOpnameListPage.tsx
| | | |____routes.tsx
| | | |____schemas/
| | | | |____stockAdjustmentSchema.ts
| | | | |____stockMovementSchema.ts
| | | | |____stockOpnameSchema.ts
| | | |____services/
| | | | |____stockAdjustmentApi.ts
| | | | |____stockBalanceApi.ts
| | | | |____stockMovementApi.ts
| | | | |____stockOpnameApi.ts
| | | |____types/
| | | | |____stockAdjustment.types.ts
| | | | |____stockBalance.types.ts
| | | | |____stockMovement.types.ts
| | | | |____stockOpname.types.ts
| | |____master-data/
| | | |____hooks/
| | | | |____useAccountMappings.ts
| | | | |____useCoaList.ts
| | | | |____useKontakList.ts
| | | | |____useProdukList.ts
| | | | |____useSimpleLists.ts
| | | |____pages/
| | | | |____CoaFormPage.tsx
| | | | |____CoaListPage.tsx
| | | | |____DepartemenPage.tsx
| | | | |____GudangPage.tsx
| | | | |____KategoriProdukPage.tsx
| | | | |____KontakFormPage.tsx
| | | | |____KontakListPage.tsx
| | | | |____PaymentTermsPage.tsx
| | | | |____ProdukFormPage.tsx
| | | | |____ProdukListPage.tsx
| | | | |____ProyekPage.tsx
| | | | |____SatuanPage.tsx
| | | |____routes.tsx
| | | |____schemas/
| | | | |____coaSchema.ts
| | | | |____departemenSchema.ts
| | | | |____gudangSchema.ts
| | | | |____kategoriProdukSchema.ts
| | | | |____kontakSchema.ts
| | | | |____paymentTermsSchema.ts
| | | | |____produkSchema.ts
| | | | |____proyekSchema.ts
| | | | |____satuanSchema.ts
| | | |____services/
| | | | |____accountMappingApi.ts
| | | | |____coaApi.ts
| | | | |____departemenApi.ts
| | | | |____gudangApi.ts
| | | | |____kategoriProdukApi.ts
| | | | |____kontakApi.ts
| | | | |____paymentTermsApi.ts
| | | | |____produkApi.ts
| | | | |____proyekApi.ts
| | | | |____satuanApi.ts
| | | |____types/
| | | | |____accountMapping.types.ts
| | | | |____coa.types.ts
| | | | |____departemen.types.ts
| | | | |____gudang.types.ts
| | | | |____kategoriProduk.types.ts
| | | | |____kontak.types.ts
| | | | |____paymentTerms.types.ts
| | | | |____produk.types.ts
| | | | |____proyek.types.ts
| | | | |____satuan.types.ts
| | |____onboarding/
| | | |____components/
| | | | |____MasterDataQuickAdd.tsx
| | | | |____WizardSidebar.tsx
| | | | |____steps/
| | | | | |____Step1CompanyInfo.tsx
| | | | | |____Step2TemplateCOA.tsx
| | | | | |____Step3AccountMapping.tsx
| | | | | |____Step4MasterData.tsx
| | | | | |____Step5OpeningBalance.tsx
| | | | | |____Step6Complete.tsx
| | | |____constants.ts
| | | |____pages/
| | | | |____OnboardingPage.tsx
| | | |____schemas/
| | | | |____companyInfoSchema.ts
| | | |____services/
| | | | |____onboardingApi.ts
| | |____opening-balance/
| | | |____hooks/
| | | | |____useOpeningBalance.ts
| | | |____pages/
| | | | |____OpeningBalanceBatchPage.tsx
| | | | |____OpeningBalanceStatusPage.tsx
| | | |____routes.tsx
| | | |____services/
| | | | |____openingBalanceApi.ts
| | | |____types/
| | | | |____openingBalance.types.ts
| | |____purchase/
| | | |____hooks/
| | | | |____useApData.ts
| | | | |____useGoodsReceiptList.ts
| | | | |____usePurchaseOrderList.ts
| | | | |____usePurchaseRequestList.ts
| | | | |____usePurchaseReturnList.ts
| | | | |____useVendorBillList.ts
| | | | |____useVendorDepositList.ts
| | | | |____useVendorPaymentList.ts
| | | |____pages/
| | | | |____ApAgingPage.tsx
| | | | |____ApReconciliationPage.tsx
| | | | |____ApSummaryPage.tsx
| | | | |____BillLedgerPage.tsx
| | | | |____GoodsReceiptFormPage.tsx
| | | | |____GoodsReceiptListPage.tsx
| | | | |____PurchaseOrderFormPage.tsx
| | | | |____PurchaseOrderListPage.tsx
| | | | |____PurchaseRequestFormPage.tsx
| | | | |____PurchaseRequestListPage.tsx
| | | | |____PurchaseReturnFormPage.tsx
| | | | |____PurchaseReturnListPage.tsx
| | | | |____VendorBillFormPage.tsx
| | | | |____VendorBillListPage.tsx
| | | | |____VendorDepositFormPage.tsx
| | | | |____VendorDepositListPage.tsx
| | | | |____VendorLedgerPage.tsx
| | | | |____VendorPaymentFormPage.tsx
| | | | |____VendorPaymentListPage.tsx
| | | |____routes.tsx
| | | |____schemas/
| | | | |____goodsReceiptSchema.ts
| | | | |____purchaseOrderSchema.ts
| | | | |____purchaseRequestSchema.ts
| | | | |____purchaseReturnSchema.ts
| | | | |____vendorBillSchema.ts
| | | | |____vendorDepositSchema.ts
| | | | |____vendorPaymentSchema.ts
| | | |____services/
| | | | |____apApi.ts
| | | | |____goodsReceiptApi.ts
| | | | |____purchaseOrderApi.ts
| | | | |____purchaseRequestApi.ts
| | | | |____purchaseReturnApi.ts
| | | | |____vendorBillApi.ts
| | | | |____vendorBillAdapter.ts
| | | | |____vendorBillSourceApi.ts
| | | | |____vendorDepositApi.ts
| | | | |____vendorPaymentApi.ts
| | | |____types/
| | | | |____ap.types.ts
| | | | |____goodsReceipt.types.ts
| | | | |____purchaseOrder.types.ts
| | | | |____purchaseRequest.types.ts
| | | | |____purchaseReturn.types.ts
| | | | |____vendorBill.types.ts
| | | | |____vendorDeposit.types.ts
| | | | |____vendorPayment.types.ts
| | |____reports/
| | | |____components/
| | | | |____ReportCompactBar.tsx
| | | | |____ReportDomainPanel.tsx
| | | | |____ReportParameterModal.tsx
| | | | |____PeriodSelector.tsx
| | | | |____SavedReportsPanel.tsx
| | | | |____SaveReportButton.tsx
| | | | |____ReportToolButton.tsx
| | | | |____PageSetupControl.tsx
| | | | |____ReportPrintToolbar.tsx
| | | | |____ReportPrintDocument.tsx
| | | | |____ReportPrintSection.tsx
| | | |____constants/
| | | | |____reportCategories.ts
| | | | |____reportDomainIcons.ts
| | | | |____reportKeyRoutes.ts
| | | | |____pageSizes.ts
| | | |____stores/
| | | | |____useReportPageSetupStore.ts
| | | |____hooks/
| | | | |____useSavedReports.ts
| | | | |____useInitialReportParams.ts
| | | | |____useReportParams.ts
| | | | |____useReportFilterSummary.ts
| | | |____pages/
| | | | |____ApAgingReportPage.tsx
| | | | |____ApOutstandingReportPage.tsx
| | | | |____ApVendorSummaryPage.tsx
| | | | |____ArAgingReportPage.tsx
| | | | |____ArCustomerSummaryPage.tsx
| | | | |____ArOutstandingReportPage.tsx
| | | | |____AccountLedgerPage.tsx
| | | | |____BalanceSheetPage.tsx
| | | | |____CashFlowPage.tsx
| | | | |____CashFlowDirectReportPage.tsx
| | | | |____RetainedEarningsReportPage.tsx
| | | | |____EquityChangesReportPage.tsx
| | | | |____ProfitLossMultiPeriodPage.tsx
| | | | |____BalanceSheetMultiPeriodPage.tsx
| | | | |____OutputVatReportPage.tsx
| | | | |____InputVatReportPage.tsx
| | | | |____EfakturExportPage.tsx
| | | | |____FinancialSummaryPage.tsx
| | | | |____GeneralLedgerPage.tsx
| | | | |____JournalListReportPage.tsx
| | | | |____InventoryAnalysisPage.tsx
| | | | |____InventoryAgingReportPage.tsx
| | | | |____OpnameWorksheetReportPage.tsx
| | | | |____ProductHistoryReportPage.tsx
| | | | |____ProfitLossPage.tsx
| | | | |____ReconciliationPage.tsx
| | | | |____CashBankStatementPage.tsx
| | | | |____FixedAssetDepreciationReportPage.tsx
| | | | |____FixedAssetDisposalsReportPage.tsx
| | | | |____FixedAssetReconciliationReportPage.tsx
| | | | |____FixedAssetRegisterReportPage.tsx
| | | | |____SalesByCustomerReportPage.tsx
| | | | |____SalesByProductReportPage.tsx
| | | | |____SalesSummaryReportPage.tsx
| | | | |____PurchaseByProductReportPage.tsx
| | | | |____PurchaseByVendorReportPage.tsx
| | | | |____PurchaseSummaryReportPage.tsx
| | | | |____ReportCategoryPage.tsx
| | | | |____ReportListPage.tsx
| | | | |____SavedReportsPage.tsx
| | | | |____legacy/
| | | | | |____ReportIndexPage.legacy.tsx
| | | | |____StockReportPage.tsx
| | | | |____TrialBalancePage.tsx
| | | |____routes.tsx
| | | |____services/
| | | | |____reportsApi.ts
| | | | |____savedReportsApi.ts
| | | |____types/
| | | | |____reports.types.ts
| | |____sales/
| | | |____components/
| | | | |____SourceDocumentPicker.tsx
| | | |____hooks/
| | | | |____useArData.ts
| | | | |____useCustomerDepositList.ts
| | | | |____useDeliveryOrderList.ts
| | | | |____useProformaList.ts
| | | | |____useQuotationList.ts
| | | | |____useSalesInvoiceList.ts
| | | | |____useSalesOrderList.ts
| | | | |____useSalesReceiptList.ts
| | | | |____useSalesReturnList.ts
| | | |____pages/
| | | | |____ArAgingPage.tsx
| | | | |____ArReconciliationPage.tsx
| | | | |____ArSummaryPage.tsx
| | | | |____CustomerDepositFormPage.tsx
| | | | |____CustomerDepositListPage.tsx
| | | | |____CustomerLedgerPage.tsx
| | | | |____DeliveryOrderFormPage.tsx
| | | | |____DeliveryOrderListPage.tsx
| | | | |____InvoiceLedgerPage.tsx
| | | | |____ProformaFormPage.tsx
| | | | |____ProformaListPage.tsx
| | | | |____QuotationFormPage.tsx
| | | | |____QuotationListPage.tsx
| | | | |____SalesInvoiceFormPage.tsx
| | | | |____SalesInvoiceListPage.tsx
| | | | |____SalesOrderFormPage.tsx
| | | | |____SalesOrderListPage.tsx
| | | | |____SalesReceiptFormPage.tsx
| | | | |____SalesReceiptListPage.tsx
| | | | |____SalesReturnFormPage.tsx
| | | | |____SalesReturnListPage.tsx
| | | |____routes.tsx
| | | |____schemas/
| | | | |____customerDepositSchema.ts
| | | | |____deliveryOrderSchema.ts
| | | | |____proformaSchema.ts
| | | | |____quotationSchema.ts
| | | | |____salesInvoiceSchema.ts
| | | | |____salesOrderSchema.ts
| | | | |____salesReceiptSchema.ts
| | | | |____salesReturnSchema.ts
| | | |____services/
| | | | |____arApi.ts
| | | | |____customerDepositApi.ts
| | | | |____deliveryOrderApi.ts
| | | | |____proformaApi.ts
| | | | |____quotationApi.ts
| | | | |____salesInvoiceApi.ts
| | | | |____salesOrderApi.ts
| | | | |____salesReceiptApi.ts
| | | | |____salesReturnApi.ts
| | | | |____sourceDocumentApi.ts
| | | |____types/
| | | | |____ar.types.ts
| | | | |____customerDeposit.types.ts
| | | | |____deliveryOrder.types.ts
| | | | |____proforma.types.ts
| | | | |____quotation.types.ts
| | | | |____salesInvoice.types.ts
| | | | |____salesOrder.types.ts
| | | | |____salesReceipt.types.ts
| | | | |____salesReturn.types.ts
| | |____settings/
| | | |____hooks/
| | | | |____useAccessManagement.ts
| | | | |____useCompanySettings.ts
| | | |____pages/
| | | | |____AccessAuditPage.tsx
| | | | |____AccountingPeriodPage.tsx
| | | | |____AccountMappingSettingsPage.tsx
| | | | |____CompanySettingsPage.tsx
| | | | |____InvitationsPage.tsx
| | | | |____MyPreferencesPage.tsx
| | | | |____RolesPage.tsx
| | | | |____TransactionSettingsPage.tsx
| | | | |____UsersPage.tsx
| | | |____routes.tsx
| | | |____services/
| | | | |____accessApi.ts
| | | | |____companySettingsApi.ts
| | | |____types/
| | | | |____access.types.ts
| | | | |____settings.types.ts
| |____router/
| | |____guards.tsx
| | |____index.tsx
| | |____moduleConfig.ts
| | |____placeholders.tsx
| | |____legacy/
| | | |____reportsRibbon.legacy.ts
| |____services/
| | |____http.ts
| |____stores/
| | |____useAuthStore.ts
| | |____useCompanyStore.ts
| | |____useTabStore.ts
| | |____useUnsavedFormsStore.ts
| |____types/
| | |____api.types.ts
| | |____auth.types.ts
| | |____common.types.ts
|____tailwind.config.ts
|____tsconfig.app.json
|____tsconfig.json
|____tsconfig.node.json
|____vite.config.ts
|____dist/  # generated build output, ignore for normal navigation
|____node_modules/  # dependency tree, ignore for normal navigation
```

## Catatan

- Tree ini mengikuti isi folder frontend saat ini.
- `dist/` dan `node_modules/` memang ada, tetapi tidak perlu dibuka saat mencari source.
- Jika ada file baru, update peta ini dulu supaya agent lain bisa baca satu file ini saja.
