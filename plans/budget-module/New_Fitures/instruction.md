Saya ingin kamu membuat PLANNING IMPLEMENTASI modul BUDGETING untuk sistem akuntansi yang sedang dikembangkan.

PENTING:
- Jangan melakukan coding.
- Jangan mengubah file apa pun.
- Jangan membuat migration.
- Jangan membuat implementasi.
- Jangan mengubah database.
- Tugasmu hanya melakukan audit codebase, analisis arsitektur, dan menghasilkan implementation plan yang detail.
- Gunakan architecture, naming convention, design pattern, database convention, API convention, UI pattern, authorization pattern, dan testing pattern yang sudah digunakan project.
- Reuse existing functionality sebanyak mungkin.
- Jangan membuat entity/module baru jika functionality yang sama sudah tersedia.
- Jangan mengasumsikan struktur sistem sebelum memeriksa codebase.

==================================================
TUJUAN UTAMA
==================================================

Merancang implementasi:

# UNIFIED MULTIDIMENSIONAL BUDGETING ENGINE

Budgeting harus menjadi satu engine yang dapat dilihat dan diringkas berdasarkan berbagai dimensi:

- Account
- Period
- Cost Center
- Project
- Revenue / Sales
- Expense / Cost
- Cash
- Company / Entity jika sistem mendukung multi-company

Jangan membuat "Budget by Account", "Budget by Project", "Budget by Cost Center", "Sales Budget", dan "Expense Budget" sebagai engine/database terpisah jika sebenarnya semuanya dapat berasal dari satu unified budget model.

Prinsip utama:

ONE BUDGET ENGINE
→ MULTIPLE DIMENSIONS
→ MULTIPLE VIEWS
→ MULTIPLE SUMMARIES

==================================================
KONSEP DIMENSION
==================================================

Budget harus dapat dikaitkan dengan:

- Fiscal Year
- Accounting Period
- Account / Chart of Accounts
- Cost Center
- Project
- Company / Organization jika tersedia

Account, Cost Center, Project, dan Period adalah DIMENSI YANG BERBEDA.

Contoh:

Account:
Beban Konsumsi

Cost Center:
Kesiswaan

Project:
Class Meeting 2026

Period:
September 2026

Budget:
Rp7.000.000

Actual:
Rp6.500.000

Variance:
Rp500.000

==================================================
BUDGET TYPES / VIEWS
==================================================

Engine harus mampu menghasilkan minimal:

LEVEL 1
1. Budget by Account
2. Budget by Period
3. Budget Pendapatan
4. Budget Beban
5. Budget vs Actual
6. Budget Utilization

LEVEL 2
7. Budget by Cost Center
8. Budget by Project
9. Project Budget
10. Cash Budget
11. Sales / Revenue Budget
12. Expense / Cost Budget
13. Variance Analysis
14. Budget Revision / Versioning

JANGAN menganggap semua item di atas sebagai independent budget engines.

Sebaliknya, tentukan mana yang merupakan:
- core budget data
- dimension
- reporting view
- aggregation
- derived calculation

==================================================
PROJECT BUDGET HARUS GENERIC
==================================================

Project Budget TIDAK boleh didesain khusus untuk sekolah.

Harus dapat digunakan untuk berbagai jenis bisnis:

1. Lembaga pendidikan
   - Class Meeting
   - Study Tour
   - MPLS
   - Wisuda
   - Pentas Seni
   - Lomba
   - Renovasi
   - Workshop
   - Kegiatan sekolah

2. Kontraktor
   - Renovasi kantor
   - Pembangunan gedung
   - Infrastruktur

3. Agency
   - Campaign
   - Event
   - Digital Marketing Project

4. Manufaktur
   - Custom production
   - Production project
   - Special order

5. Distributor / Trading
   - Pengadaan barang
   - Tender / procurement project
   - Delivery project

6. Jasa
   - Consulting project
   - Implementation project
   - Service contract

Karena itu Project harus diperlakukan sebagai GENERIC BUSINESS DIMENSION.

==================================================
PROJECT FINANCIAL MODEL
==================================================

Project Budget tidak hanya berisi expense.

Project dapat memiliki:

- Revenue Budget
- Cost Budget
- Expense Budget
- Gross Profit Budget
- Gross Margin Budget
- Cash Inflow Budget
- Cash Outflow Budget

Contoh:

PROJECT:
Renovasi Kantor PT ABC

Contract Revenue:
Rp500.000.000

Budget Cost:
Rp470.000.000

Budget Profit:
Rp30.000.000

Budget Margin:
6%

Actual Revenue:
Rp500.000.000

Actual Cost:
Rp462.000.000

Actual Profit:
Rp38.000.000

Actual Margin:
7,6%

Sistem harus mampu menghasilkan ringkasan seperti tersebut apabila architecture existing mendukung revenue/project transaction.

==================================================
PROJECT BUDGET STRUCTURE
==================================================

Project dapat memiliki budget lines:

Project:
Renovasi Kantor PT ABC

Revenue:
- Project Revenue Rp500 juta

Costs:
- Material Rp220 juta
- Labor Rp120 juta
- Transport Rp25 juta
- Subcontractor Rp70 juta
- Equipment Rp20 juta
- Other Cost Rp15 juta

Total Cost Budget:
Rp470 juta

Budget Profit:
Rp30 juta

Jelaskan apakah struktur existing cukup untuk mendukung model ini.

Jika tidak cukup, jelaskan perubahan minimum yang diperlukan.

==================================================
TRANSACTION INTEGRATION
==================================================

Actual TIDAK boleh diinput ulang melalui modul Budgeting.

Actual harus berasal dari transaction/accounting engine existing.

Idealnya:

TRANSACTION
+
ACCOUNT
+
COST CENTER
+
PROJECT
+
PERIOD
+
COMPANY

akan menjadi dasar actual calculation.

Contoh transaksi:

Purchase:
Rp10.000.000

Account:
Material Expense / Inventory

Cost Center:
Project Division

Project:
Renovasi Kantor ABC

Period:
August 2026

Transaction tersebut harus dapat mempengaruhi secara otomatis:

- Account Actual
- Cost Center Actual
- Project Actual
- Period Actual
- Expense Actual
- Cash Actual jika dibayar
- Budget vs Actual

Jangan membuat actual ledger terpisah jika architecture existing sudah memiliki accounting ledger.

==================================================
MULTI-DIMENSIONAL SUMMARY
==================================================

Sistem harus mampu melakukan aggregation dan drill-down.

Contoh:

TOTAL COMPANY
Budget Rp500 juta
Actual Rp420 juta
Variance Rp80 juta
Utilization 84%

↓ Drill Down

COST CENTER:
Kesiswaan
Budget Rp150 juta
Actual Rp130 juta

↓ Drill Down

PROJECT:
Class Meeting
Budget Rp15 juta
Actual Rp13 juta

↓ Drill Down

ACCOUNT:
Beban Konsumsi
Budget Rp3 juta
Actual Rp2,8 juta

Semua angka tersebut harus berasal dari source budget/transaction yang sama.

Jelaskan arsitektur aggregation yang paling sesuai dengan existing codebase.

==================================================
REPORTING VIEWS
==================================================

Minimal support:

1. Budget by Account
2. Budget by Cost Center
3. Budget by Project
4. Budget by Period
5. Revenue Budget
6. Expense Budget
7. Budget vs Actual
8. Variance Analysis
9. Budget Utilization
10. Cash Budget
11. Project Budget
12. Project Actual
13. Project Profitability
14. Project Margin
15. Project Cash Flow
16. Budget Revision History

Untuk setiap report jelaskan:

- source data
- filter
- grouping
- dimensions
- columns
- calculations
- drill-down
- relationship dengan report lain

==================================================
CASH BUDGET
==================================================

Cash Budget boleh memiliki calculation khusus, tetapi JANGAN membuat cash ledger baru apabila sistem existing sudah memiliki Cash/Bank ledger.

Minimal:

Beginning Cash
+
Budgeted Cash Inflow
-
Budgeted Cash Outflow
=
Budgeted Ending Cash

Jelaskan bagaimana Cash Budget berhubungan dengan:

- Revenue Budget
- Expense Budget
- Project Budget
- Actual Cash Transaction

==================================================
BUDGET VS ACTUAL
==================================================

Wajib mendukung:

- Under Budget
- Over Budget
- Exactly on Budget
- No Actual
- No Budget
- Negative adjustment
- Reversal
- Refund
- Credit note/debit note jika applicable
- Partial period

Untuk expense:

Budget - Actual = Remaining / Favorable-Unfavorable sesuai business definition.

Untuk revenue:

Actual - Budget dapat digunakan untuk menunjukkan performance.

Jelaskan secara eksplisit definisi variance untuk:

- Revenue
- Expense
- Cost
- Project Profit
- Cash

Jangan membuat definisi yang ambigu.

==================================================
BUDGET UTILIZATION
==================================================

Minimal:

Expense:

Actual / Budget × 100%

Revenue:

Actual / Budget × 100%

Project:

Actual Cost / Budget Cost × 100%

Jelaskan handling ketika Budget = 0.

==================================================
BUDGET REVISION / VERSIONING
==================================================

Budget harus mendukung versioning.

Contoh:

Version 1:
Rp15 juta

Version 2:
Rp18 juta

Version 3:
Rp20 juta

History version sebelumnya tidak boleh hilang.

Analisis:

- Original Budget
- Revised Budget
- Current Active Budget
- Revision History
- Revision Reason
- Created By
- Created At
- Approval Status jika tersedia
- Effective Period
- Relationship dengan transactions

Jelaskan apakah approved budget immutable.

==================================================
FORECAST / FUTURE EXTENSION
==================================================

Jangan implementasikan fitur Level 3 kecuali architecture existing sudah mendukungnya.

Namun pastikan desain core budget tidak menghalangi future support untuk:

- Forecast
- Rolling Budget
- Flexible Budget
- Scenario Budget
- Multi-year Budget
- What-if Analysis

Tandai fitur tersebut sebagai FUTURE EXTENSION, bukan MUST HAVE.

==================================================
DATABASE ANALYSIS
==================================================

Audit existing database terlebih dahulu.

Cari existing:

- accounts
- journals
- journal_lines
- ledger
- fiscal_year
- accounting_period
- cost_centers
- projects
- transactions
- sales
- purchases
- expenses
- cash
- bank
- companies
- branches
- users
- approvals
- audit logs

Lalu tentukan:

- tabel yang bisa direuse
- tabel baru yang diperlukan
- field tambahan yang diperlukan
- relationship
- indexes
- unique constraints
- tenant/company scoping
- soft delete behavior

Pertimbangkan kemungkinan:

budgets
budget_lines
budget_versions
budget_version_lines

Tetapi JANGAN memaksakan nama tersebut.

Ikuti convention existing.

Yang paling penting:

Jelaskan apakah semua budget views dapat berasal dari struktur data yang sama tanpa redundancy.

==================================================
BUSINESS RULES
==================================================

Identifikasi business rules untuk:

- duplicate budget
- overlapping budget periods
- multiple project budgets
- multiple cost center budgets
- approved budget
- revised budget
- closed accounting period
- deleted project
- deleted account
- deleted cost center
- zero budget
- negative budget
- revenue budget
- expense budget
- project budget
- partial project
- completed project

Jangan membuat business rules yang bertentangan dengan existing system.

==================================================
PERMISSION
==================================================

Audit existing authorization model.

Mapping kebutuhan minimal:

budget.view
budget.create
budget.update
budget.delete
budget.submit
budget.approve
budget.revise
budget.export

Tetapi gunakan naming convention permission existing.

Project budget juga harus menghormati permission project existing.

==================================================
UI / UX
==================================================

Audit existing design system.

Jangan membuat design system baru.

Planning minimal:

- Budget List
- Create Budget
- Budget Detail
- Edit Budget
- Budget Version History
- Budget vs Actual
- Variance Analysis
- Budget Utilization
- Project Budget
- Project Financial Summary
- Cash Budget
- Dashboard / Summary

Pertimbangkan satu unified budget interface dengan filter dimensions:

Company
Fiscal Year
Period
Account
Cost Center
Project

dan mode:

Summary
Detail
Variance
Actual
Forecast (future)

==================================================
API PLAN
==================================================

Rancang endpoint atau application service sesuai pattern existing.

Jangan langsung membuat REST endpoint jika project menggunakan service/action/query pattern lain.

Minimal coverage:

- budget list
- budget detail
- budget creation
- budget update
- budget revision
- budget version history
- budget vs actual
- variance
- utilization
- project budget
- project summary
- project profitability
- cash budget

==================================================
TESTING PLAN
==================================================

Buat test plan:

- unit
- integration
- database
- API
- permission
- accounting calculation
- budget calculation
- project budget
- project profitability
- cash budget
- versioning
- tenant isolation
- regression

Edge cases:

- Budget 0
- Actual 0
- Actual > Budget
- Actual < Budget
- Revenue > Budget
- Revenue < Budget
- Expense > Budget
- Expense < Budget
- Project with revenue
- Project without revenue
- Project with only expense
- Project with no transaction
- Budget without transaction
- Transaction without budget
- Multiple versions
- Reversal
- Refund
- Closed period
- Negative adjustment
- Partial period

==================================================
IMPLEMENTATION PHASES
==================================================

Buat phased implementation:

PHASE 0
Existing Architecture Audit

PHASE 1
Domain & Database

PHASE 2
Unified Budget Engine

PHASE 3
Budget Line & Period Allocation

PHASE 4
Budget vs Actual

PHASE 5
Cost Center Budget

PHASE 6
Generic Project Budget

PHASE 7
Project Profitability

PHASE 8
Cash Budget

PHASE 9
Budget Revision / Versioning

PHASE 10
Reporting & Aggregation

PHASE 11
Frontend / Dashboard

PHASE 12
Permission / Approval

PHASE 13
Testing

PHASE 14
Documentation

Untuk setiap phase jelaskan:

- objective
- existing files affected
- new files
- database changes
- API/service changes
- frontend changes
- dependencies
- risks
- testing
- acceptance criteria

==================================================
OUTPUT FINAL
==================================================

Buat dokumen:

# Unified Budgeting Implementation Plan

## 1. Executive Summary
## 2. Existing Architecture Analysis
## 3. Existing Features Reusable
## 4. Gap Analysis
## 5. Proposed Budget Architecture
## 6. Budget Domain Model
## 7. Multidimensional Budget Model
## 8. Transaction-to-Actual Architecture
## 9. Budget vs Actual Logic
## 10. Cost Center Budget
## 11. Generic Project Budget
## 12. Project Profitability
## 13. Cash Budget
## 14. Budget Revision / Versioning
## 15. Aggregation & Drill-down
## 16. Reporting Architecture
## 17. Database Plan
## 18. API / Service Plan
## 19. Frontend Plan
## 20. Permission & Approval
## 21. Business Rules
## 22. Testing Strategy
## 23. Migration Strategy
## 24. Implementation Phases
## 25. File-by-File Change Plan
## 26. Risks & Technical Decisions
## 27. Future Extension
## 28. Acceptance Criteria
## 29. Recommended Implementation Order

==================================================
IMPORTANT ARCHITECTURAL PRINCIPLES
==================================================

1. ONE UNIFIED BUDGET ENGINE.
2. Account, Cost Center, Project, Period adalah dimensions, bukan independent budget engines.
3. Reporting views harus berasal dari source budget yang sama.
4. Actual berasal dari accounting transactions existing.
5. Jangan input actual secara manual di Budgeting.
6. Project adalah generic business dimension.
7. Project dapat memiliki Revenue, Cost, Expense, Profit, Margin, dan Cash Flow.
8. Project Budget harus cocok untuk pendidikan maupun bisnis komersial.
9. Budget vs Actual harus bisa dilakukan lintas dimension.
10. Semua dimension harus dapat di-summary dan drill-down.
11. Budget Versioning harus menjaga historical versions.
12. Jangan membuat duplicate ledger/accounting transaction system.
13. Jangan over-engineer.
14. Reuse existing modules.
15. Ikuti architecture existing.
16. Pisahkan MUST HAVE, SHOULD HAVE, dan FUTURE.
17. Pastikan desain scalable untuk UMKM, perusahaan, dan lembaga pendidikan.
18. Pastikan desain memungkinkan future Forecast / Rolling Budget / Scenario Budget tanpa harus rewrite core budget engine.

SEBELUM MEMBERIKAN PLAN FINAL:
- Audit codebase secara menyeluruh.
- Verifikasi relationship antar module.
- Verifikasi apakah Project, Cost Center, Account, Fiscal Year, Period, Cash/Bank, Sales, Purchase, Expense sudah tersedia.
- Verifikasi bagaimana transaction dan ledger existing bekerja.
- Verifikasi multi-company/tenant architecture.
- Verifikasi authorization dan audit trail.
- Pastikan implementation plan tidak menduplikasi functionality existing.

JANGAN IMPLEMENTASI APA PUN.
HANYA HASILKAN ANALISIS DAN IMPLEMENTATION PLAN.