# Project Dimension & Budgeting Readiness — Implementation Plan

> **Status: dokumen plan, belum diimplementasikan.** Tidak ada kode/migration yang berubah
> untuk menghasilkan dokumen ini — audit read-only, 4 agent eksplorasi paralel, semua klaim
> diverifikasi langsung ke kode (path + nomor baris).
>
> **Dokumen ini menggantikan dan memperluas cakupan Project-dimension** di
> `phase-4-dimensi-revenue.md` dan bagian Project di `phase-6-view-turunan-dan-permission.md`
> (Cash Budget, Project Profitability tetap berlaku formulanya — hanya akurasi Actual Cost
> yang berubah). Kedua file itu tetap ada, diberi penanda supersede di bagian atas.

## Context

Modul Budget (fase 0-8 di folder ini) sudah dirancang dengan Project sebagai salah satu
dimensi kunci (Project Budget, Project Profitability, Project Cash Flow — lihat `phase-6`).
Audit lanjutan atas fitur Project itu sendiri ([project-feature-audit.md](project-feature-audit.md))
menemukan bahwa kebocoran dimensi `project_id` ke `journal_entry_lines` **jauh lebih luas**
dari yang tercakup `phase-4-dimensi-revenue.md` (yang hanya menutup Sales Invoice) — mencakup
juga Sales Return, Purchase Bill, Purchase Return, hampir seluruh jalur
`StockMovementJournalService` (COGS, purchase_in, adjustment, opening_stock — hanya opname
yang benar), dan seluruh journal Fixed Asset (capitalization, disposal, depreciation batch).

Pemilik produk meminta audit + plan lanjutan yang lebih dalam. Tujuan akhir: Project siap jadi
fondasi dimensi yang **akurat** untuk Unified Budgeting Engine — bukan cuma "field yang ada"
tapi "field yang benar-benar terisi sampai ke ledger".

Instruksi eksplisit yang mengikat sesi audit ini: tidak ada coding, tidak ada file diubah,
tidak ada migration. Output adalah dokumen implementation plan — implementasinya sendiri
adalah pekerjaan terpisah yang menunggu approval lebih lanjut.

---

## 1. Executive Summary

Project sudah menjadi entitas master data yang solid dan generic (flat, tanpa hierarki, tanpa
kolom industri-spesifik) — **struktur datanya sudah siap** jadi dimensi Unified Budget. Yang
**belum siap** adalah tiga hal:

1. **Integritas dimensi** — `project_id` hilang di ledger untuk sebagian besar jalur transaksi
   (Sales, Purchase, Inventory/COGS, Fixed Asset) kecuali Cash/Bank dan Journal manual.
   Prioritas tertinggi karena tanpa ini, Actual Project selalu under-reported.
2. **Input di UI** — tidak ada selector Project di form transaksi manapun kecuali Fixed Asset,
   jadi meski leak backend diperbaiki, data produksi akan tetap kosong sampai form diberi field.
3. **Kualitas & tata kelola** — status lifecycle tanpa guard, tiga implementasi berbeda dari
   aturan "project usable", tidak ada audit trail, beberapa bug frontend kecil, dan satu tab UI
   ("Anggaran" di form Project) yang datanya tidak pernah tersimpan dan akan bentrok konsep
   dengan Project Financial Summary yang direncanakan.

Tidak ada perubahan skema besar yang diperlukan — **tidak** ada kolom `budget_amount`/
`actual_amount`/`profit`/`margin` yang perlu ditambahkan ke `projects`. Semua angka finansial
tetap dihitung dari Unified Budget Engine (fase 1-2) + ledger, sesuai prinsip arsitektur yang
sudah disepakati.

---

## 2. Current Project Architecture

```
projects (tenant)                     — flat master data, generic
  id, code (unique), name, description,
  start_date, end_date, status (string), is_active (bool), metadata (json)

Project model — app/Modules/MasterData/Models/Project.php
  relasi: journalEntryLines() HasMany
  scope: scopeUsable() — TIDAK PERNAH DIPANGGIL (dead code)
  method: isUsable() = isActive() && status === 'active' — dipakai BusinessReferenceValidator

ProjectService — app/Modules/MasterData/Services/ProjectService.php (124 baris)
  create/update/deactivate/activate — dipakai controller
  markCompleted/markOnHold/cancel  — ADA di service, TIDAK diekspos controller mana pun
  TIDAK ADA constructor — TIDAK ADA AuditLogService — nol audit trail

ProjectController — index/store/show/update/deactivate/activate
Routes — /api/master-data/projects (+ /{id}, /{id}/activate, /{id}/deactivate)
Permission — projects.view, projects.create, projects.edit, projects.deactivate
  (activate memakai projects.edit, bukan permission terpisah)
```

Radius blast (model dengan `belongsTo(Project::class, 'project_id')`, dikonfirmasi via grep):
`CashPaymentLine`, `CashReceiptLine`, `FixedAsset`, `DeliveryOrderLine`, `SalesQuotationLine`,
`StockAdjustmentLine`, `PurchaseRequestLine`, `GoodsReceiptLine`, `BudgetLine`,
`JournalEntryLine`, `PurchaseRequest` (header), `StockMovementLine` — plus ±10 service laporan
yang memfilter `project_id` tanpa relasi Eloquent formal di file yang sama.

`journal_entry_lines.department_id`/`.project_id` — migration
`2026_05_19_000003_add_dimensions_to_journal_entry_lines_table.php`: nullable, FK
`nullOnDelete()`, index **per-kolom** (bukan composite).

---

## 3. Audit Findings

| # | Temuan | Bukti |
|---|---|---|
| F1 | `scopeUsable()` dead code; aturan "usable" ditulis ulang independen di 2 tempat lain | `Project.php:61-64` (isUsable), `BusinessReferenceValidator.php:142-154` (delegasi benar ke isUsable), `JournalValidationService.php:124-133` (reimplementasi manual — DIVERGEN) |
| F2 | `markCompleted/markOnHold/cancel` ada di service tapi tak terpakai; transisi status sebenarnya lewat `update()` tanpa guard apa pun | `ProjectService.php:69-83,101-123`; `ProjectController.php` (tidak ada action untuk 3 method itu) |
| F3 | Guard validitas Project **tidak konsisten** lintas modul | Tervalidasi: Sales (`HandlesSalesDocuments.php:50`), Purchase (`HandlesPurchaseDocuments.php:50,93`), Inventory StockMovement (`StockMovementValidationService.php:92`), GoodsReceipt (`GoodsReceiptService.php:292`). **Tidak** tervalidasi: CashBank, Budget, FixedAssets |
| F4 | Nol audit trail di seluruh siklus hidup Project | `ProjectService.php` tanpa constructor sama sekali |
| F5 | Tidak ada permission granular untuk data finansial Project; tidak ada precedent field-level permission di codebase ini | `config/permissions.php:50-53` vs `:260-264` (budgets, precedent stage-based, bukan field-level) |
| F6 | `proyekApi.search()` hardcode `status=active` — proyek `on_hold` tidak pernah muncul di selector mana pun | `proyekApi.ts:25` |
| F7 | Bug: form create Project tidak kirim `code` yang wajib di backend | `proyekSchema.ts` (tidak ada field code), `StoreProjectRequest` (wajib) |
| F8 | Bug: cache tidak invalidasi setelah create/update | `ProyekFormPage.tsx:74,79` panggil `proyekApi` langsung, tidak lewat `useProyekMutations()` (`useSimpleLists.ts:206-229`, hook yang benar tapi tidak dipakai) |
| F9 | Bug: `ProyekStatus` FE hilang `on_hold` | `proyek.types.ts:1` |
| F10 | Tab "Anggaran" di `ProyekFormPage.tsx` adalah UI mati — state lokal, tidak pernah dikirim ke backend | `ProyekFormPage.tsx:54 (state), :70-86 (onSubmit tidak menyertakan budgetLines)` |

---

## 4. Critical Dimension Leaks (P0)

Tabel lengkap per jalur, hasil audit line-verified atas `SalesInvoiceService.php`,
`SalesReturnService.php`, `VendorBillService.php`, `PurchaseReturnService.php`,
`StockMovementJournalService.php`, `FixedAssetService.php`:

| Modul | Method | Baris | Grouping key sekarang | Status |
|---|---|---|---|---|
| Sales revenue | `SalesInvoiceService::invoiceRevenueJournalLines()` | 451-506, grouping di 465/467, emit 482-490 | `$revenueAccountId` / `$discountAccountId` saja | ❌ LEAK |
| Sales AR/tax | `SalesInvoiceService::createInvoiceJournal()` | 413-432 | N/A (single line) | OK — akun kontrol, tidak butuh dimensi |
| Sales return | `SalesReturnService::returnAccountGroups()` | 297-311, grouping di 307 | `$accountId` saja | ❌ LEAK |
| Purchase bill | `VendorBillService::billDebitJournalLines()` | 481-536, grouping di 510 | `$accountId` saja | ❌ LEAK (hanya baris Inventory/FA-Clearing, neraca) |
| Purchase return | `PurchaseReturnService::returnAccountGroups()` | 297-311, grouping di 307 | `$accountId` saja | ❌ LEAK |
| Inventory purchase_in | `inventoryDebitLines()` (183-200) + `interimCreditLines()` (317-343) | key di 188 / 324 | `inventory_account_id` / `inventory_interim_account_id` saja | ❌ LEAK |
| Inventory purchase_return_out | `inventoryCreditLines()` (279-296) | key di 284 | `inventory_account_id` saja | ❌ LEAK |
| Inventory COGS (sales_out) | `cogsDebitLines()` (298-315) + `inventoryCreditLines()` | key di 303 | `cogs_account_id` saja | ❌ LEAK — komponen cost terbesar |
| Inventory sales_return_in | `cogsCreditLines()` (345-362) + `inventoryDebitLines()` | key di 350 | `cogs_account_id` saja | ❌ LEAK |
| Inventory adjustment_in/out | `createAdjustmentJournal()` (76-107) | 91-94, 103-106 | tidak ada grouping, hardcoded array | ❌ LEAK |
| Inventory opening_stock | `createOpeningStockJournal()` (155-168) | 164-167 | tidak ada grouping, hardcoded array | ❌ LEAK |
| Inventory opname_in/out | `opnameInventoryLines()` (202-240) + `opnameOffsetLines()` (242-263) | key komposit di 217-222 / 247 | `account\|department_id\|project_id` | ✅ REFERENSI — satu-satunya yang benar |
| Fixed Asset capitalization | `FixedAssetService::capitalize()` | 183-186 | tidak ada grouping, 2 baris literal | ❌ LEAK |
| Fixed Asset disposal | `FixedAssetService::dispose()` | 256-275 | tidak ada grouping | ❌ LEAK |
| Fixed Asset depreciation | `FixedAssetService::postDepreciationPeriod()` | 352-377, grouping di 361-362 | `'dr_'.expense` / `'cr_'.accumulated` — **batch lintas SEMUA aset dalam periode** | ❌ LEAK TERBURUK — kehilangan dimensi setiap aset sekaligus |
| Cash Payment/Receipt | `CashPaymentService::journal()` (167-217) / `CashReceiptService::journal()` (180-230) | per-baris, tidak digrouping (194-204 / 215-225) | 1:1 dari line ke journal line | ✅ SUDAH BENAR |
| Manual Journal | `JournalLineNormalizer::normalizeLine()` | 31-46, dims di 38-39 | passthrough dari request | ✅ SUDAH BENAR |

**Prioritas perbaikan di dalam P0** (berdasarkan besaran dampak ke Actual Cost/Revenue proyek):
1. Inventory COGS (`cogsDebitLines`/`cogsCreditLines`) — komponen biaya terbesar di kebanyakan proyek
2. Fixed Asset depreciation — batch leak, dampak berulang tiap periode
3. Sales revenue (`invoiceRevenueJournalLines`) — sudah punya rencana di `phase-4`, tinggal eksekusi
4. Sisanya (return, adjustment, opening_stock, purchase_in, capitalization/disposal) — dampak lebih kecil/jarang tapi tetap harus konsisten

---

## 5. Transaction → Journal Dimension Flow

Target akhir (berlaku untuk semua modul di atas):

```
Document Line (punya project_id, department_id — sudah ada di skema utk semua modul di §4)
   ↓
Journal-builder method mengelompokkan/emit baris jurnal
   ↓ [PERBAIKAN P0 ada di titik ini]
   ↓ kunci grouping HARUS komposit: account_id . '|' . (department_id ?: '') . '|' . (project_id ?: '')
   ↓ meniru pattern StockMovementJournalService::opnameInventoryLines() (baris 217-222)
Journal Entry Lines (department_id, project_id terisi bila sumbernya berdimensi)
   ↓
ReportQueryService::reportableJournalLinesQuery() (sudah benar — filter status=posted, is_obsolete=0)
   ↓
BudgetActualService (fase 2) — actual per dimensi
   ↓
Budget vs Actual / Project Financial Summary
```

**Prinsip yang mengunci desain**: kalau baris dokumen tidak punya `project_id` (transaksi umum,
mis. bayar listrik kantor), kunci grouping tetap jalan dengan `project_id=''` — baris jurnal
tetap ter-generate seperti sekarang, hanya kosong di dimensinya. Tidak ada perubahan pada baris
tanpa dimensi (regresi nol untuk kasus tanpa Project — wajib dibuktikan test byte-for-byte
identik, pola yang sama dipakai di `phase-4`).

---

## 6. Required Project Model Changes

**Tidak ada perubahan skema `projects`.** Audit mengonfirmasi flat structure sudah cukup:
tidak perlu `parent_id` (tidak ada bukti kebutuhan sub-proyek di codebase manapun), tidak perlu
`company_id` (tenant isolation sudah di level file), tidak perlu kolom finansial apa pun.

Satu perubahan kecil di level model (bukan skema): hapus `Project::scopeUsable()` yang dead
code — lihat keputusan produk di penutup dokumen ini.

---

## 7. Project Budget Integration

Tidak berubah dari `phase-6-view-turunan-dan-permission.md` §"Project Budget & Profitability" —
`budget_lines.project_id` sudah ada dan benar (dikonfirmasi ulang: `BudgetLine.php:20,68`).
Struktur representasi (Revenue/Material/Labor/dst sebagai baris `budget_lines` per akun) tetap
berlaku persis seperti dirancang di `phase-6`.

**Yang berubah karena audit ini**: akurasi *Actual* sisi Budget vs Actual bergantung penuh pada
P0 di atas selesai. Sebelum P0, `BudgetActualService` (fase 2) akan menghitung Actual Cost
proyek jauh lebih rendah dari kenyataan karena COGS dan depresiasi tidak per-proyek di ledger.
**P0 adalah prasyarat keras P1**, bukan paralel.

---

## 8. Project Financial Summary

Formula dan struktur halaman **tetap seperti `phase-6`** (`ProjectFinancialSummaryPage.tsx`,
`BudgetProjectService::GET /budget/projects/{id}/summary`) — Revenue/Cost/Profit/Margin
Budget vs Actual, dengan catatan keterbatasan invoice lama.

**Tambahan dari audit ini**: catatan keterbatasan itu perlu diperluas — bukan cuma "invoice
sebelum perbaikan revenue", tapi **"transaksi sebelum P0 selesai (Sales, Purchase, Inventory/
COGS, Fixed Asset) tidak akan akurat per proyek"**. UI wajib menampilkan disclaimer tanggal
efektif ("Akurat untuk transaksi setelah [tanggal deploy P0]").

---

## 9. Project Profitability

Formula tetap seperti `phase-6` §"Project Profitability": `Profit = Revenue − Cost`,
`Margin % = Profit / Revenue × 100` (`null` bila Revenue = 0). Tidak berubah.

Perubahan dari audit ini hanya di keandalan input `Cost` — lihat §4. Tidak ada perubahan
formula atau desain baru.

---

## 10. Project Cash Flow

Tetap seperti `phase-6` §"Cash Budget" — `BudgetCashService`, filter `project_id` untuk versi
proyek. Cash/Bank **sudah benar** meneruskan dimensi (§4), jadi Project Cash Flow **tidak**
bergantung pada perbaikan P0 — bisa akurat lebih cepat dari Profitability/Financial Summary.
Ini alasan bagus untuk urutan implementasi: Cash Flow bisa dirilis duluan sebagai quick win.

---

## 11. Transaction UI Project Selector

Prasyarat P0 (backend) selesai dulu — percuma menambah selector kalau baris jurnalnya tetap
membuang dimensi.

**Temuan kunci**: bukan cuma Project yang belum ada selectornya — **Department/Cost Center
juga tidak ada** di line editor Sales/Purchase/Cash-Bank/Inventory (grep dikonfirmasi nol hasil
di keempatnya). Satu-satunya `department_id` yang ada di UI transaksi adalah header-level di
`PurchaseRequestFormPage.tsx` (232-243) — beda bentuk (header vs per-line) dari yang dibutuhkan.

### RULE — wajib pakai `LineItemsTable`, bukan tabel manual

Lihat juga [phase-0.1-reusable-line-items-component.md](phase-0.1-reusable-line-items-component.md)
— dokumen terpisah yang merapikan 4 form lain (`BudgetLineEditor`, `OpeningBalanceBatchPage`,
`VendorPaymentFormPage`, `SalesReceiptFormPage`) yang masih memakai tabel manual di luar 7 form
target P1 di dokumen ini. Dikerjakan lebih dulu agar seluruh form baris-item di frontend
konsisten satu komponen, bukan cuma yang disentuh Project selector.

**Temuan penting (diverifikasi ulang setelah draf pertama plan ini)**: `GoodsReceiptFormPage.tsx`
("form penerimaan") dan **ketujuh** form transaksi yang jadi target §24 P1 —
`SalesInvoiceFormPage.tsx`, `VendorBillFormPage.tsx`, `CashPaymentFormPage.tsx`,
`CashReceiptFormPage.tsx`, `StockAdjustmentFormPage.tsx`, `StockMovementFormPage.tsx`,
`JournalFormPage.tsx` — **SEMUANYA sudah memakai** komponen tabel baris bersama
`@/components/shared/form/LineItemsTable` (`frontend/src/components/shared/form/LineItemsTable.tsx`),
bukan tabel manual. Ini gaya "compact table view" yang dimaksud: `<table className="min-w-full
border-collapse text-[13px]">`, header abu `bg-[#eeeeee]`, sel `px-2.5 py-2`, input di dalam sel
`h-8 text-[12px]`, tombol hapus baris ikon kecil `h-6 w-6`.

**Konsekuensi untuk plan ini**: kolom Project selector **wajib** ditambahkan sebagai entri baru
di array `LineItemColumn<EditableLine>[]` yang sudah ada di tiap form (lihat pola
`GoodsReceiptFormPage.tsx:168-197`, kolom `render: ({ item, onUpdate, isReadOnly }) => <Input
... className="h-8 text-[12px]" />`), **bukan** membuat tabel/komponen baru. Cukup tambah satu
kolom dengan `render` yang mengembalikan `SearchableSelect` (`size="sm"` supaya sama tinggi
dengan sel lain) alih-alih menulis ulang struktur tabel.

**`BudgetLineEditor.tsx` BUKAN referensi pattern yang tepat** — komentar di baris 91 file itu
sendiri mengakui tabelnya sengaja dibiarkan manual, tidak dipindah ke `LineItemsTable` bersama.
Ini deviasi yang sudah ada di modul Budget, bukan pattern yang harus ditiru di form lain. Draf
plan ini sebelumnya salah mengutip `BudgetLineEditor.tsx` sebagai contoh per-line — dikoreksi di
sini.

**Manual Journal** kasus khusus: backend type **sudah siap** (`journalEntry.types.ts:9-12,74-75`
punya `department_id`/`project_id`), `JournalFormPage.tsx` juga **sudah pakai `LineItemsTable`**
(baris 378), tapi `columns` (250-312) belum punya entri untuk `project_id`/`department_id`, dan
`EditableLine` (28-35) + mapping load-dari-server (167-177) + build-payload (207) belum
menyertakannya. Ini **wiring** murni (tambah 1 kolom + 3 titik data), bukan desain baru —
effort lebih rendah dari 6 form lain karena strukturnya sudah 100% siap pakai `LineItemsTable`.

**Keputusan bentuk field per modul** (semua per-line, konsisten dengan `LineItemsTable`):

| Modul | Bentuk | Alasan |
|---|---|---|
| Sales Invoice | Per-line, kolom baru di `LineItemsTable` existing | Satu invoice bisa memuat item lintas proyek |
| Vendor Bill | Per-line, sama | Sama alasannya |
| Cash Payment/Receipt | Per-line, sama (ikuti struktur `CashPaymentLine`/`CashReceiptLine` yang SUDAH punya `project_id` di baris, backend sudah benar §4) | Skema baris sudah mendukung multi — konsisten dengan backend |
| Stock Adjustment/Movement | Per-line, sama | Selaras dengan `StockMovementLine.project_id` yang sudah ada |
| Manual Journal | Per-line, sama | Sudah didukung tipe & backend & `LineItemsTable`, tinggal wiring |

`proyekApi.search()` tetap hardcode `status=active` untuk konteks input transaksi baru (benar
secara bisnis — tidak boleh posting ke proyek yang sudah selesai/batal) — **tidak diubah**.

---

## 12. Project Lifecycle / Status

Status: `active`, `on_hold`, `completed`, `cancelled`. Saat ini bebas — `update()` menerima
field `status` mentah tanpa guard transisi (`ProjectService.php:69-83`).

**Pattern rujukan**: `PurchaseOrderService::transition()` (private helper generik) —
`in_array($order->status, $from, true)` guard, throw `ApiException` 422 kalau invalid, lalu set
status + audit call dalam satu tempat. **Jangan pakai `SalesOrderService` sebagai rujukan** —
constructor-nya menyuntik `AuditLogService` tapi tidak pernah memanggilnya (dependency mati).

**Allowed transitions**:

| Dari | Ke | Diizinkan? |
|---|---|---|
| `active` | `on_hold` | ✅ |
| `active` | `completed` | ✅ |
| `active` | `cancelled` | ✅ |
| `on_hold` | `active` | ✅ (resume) |
| `on_hold` | `cancelled` | ✅ |
| `on_hold` | `completed` | ❌ — harus resume ke `active` dulu |
| `completed` | apa pun | ❌ — final, historical data harus terkunci |
| `cancelled` | apa pun | ❌ — final |

**Siapa yang boleh mengubah**: tetap `projects.edit` — **keputusan produk**: tidak ada
permission baru (lihat penutup dokumen).

**Impact ke transaksi**: `completed`/`cancelled` diblokir dari **transaksi baru** lewat
`BusinessReferenceValidator::project()` yang sudah ada (§13) — cukup pastikan semua modul
memanggilnya (perbaikan konsistensi, bukan logika baru). **Data historis tidak boleh terpengaruh**
— tidak ada cascading delete/update ke `journal_entry_lines`/dokumen lama; `nullOnDelete()` di FK
sudah menjamin ini di level skema.

**Impact ke Budget**: proyek `completed`/`cancelled` tetap muncul di semua laporan Budget
(historical), tapi tidak bisa jadi target `budget_lines.project_id` baru — validasi ini masuk
`UpdateBudgetLinesRequest` (fase 1 Budget), memakai `BusinessReferenceValidator::project()` yang
sama.

---

## 13. Project Usability Validation

**Masalah**: tiga implementasi berbeda untuk aturan yang sama ("project usable" = `is_active`
AND `status === 'active'`):

1. `Project::isUsable()` — model method, **benar**, sumber kebenaran yang seharusnya
2. `Project::scopeUsable()` — query scope, identik logikanya, tapi **dead code** — **dihapus**
   (keputusan produk)
3. `JournalValidationService::validateDimensions()` baris 124-133 — **reimplementasi manual**,
   divergen dari #1 (ditulis ulang, bukan memanggil `isUsable()`)

**Rencana konsolidasi**:
- `JournalValidationService` diubah memanggil `Project::isUsable()` (atau
  `BusinessReferenceValidator::project()` kalau ingin exception message konsisten) — bukan
  menulis ulang kondisinya.
- **Perluasan cakupan validasi** (F3, §3): `BusinessReferenceValidator::project()` sudah benar
  tapi tidak dipanggil dari CashBank, Budget, FixedAssets. Tambahkan pemanggilan di titik input
  ketiga modul itu (`CashPaymentService`/`CashReceiptService`, `BudgetSubmissionService`,
  `FixedAssetService::create/update`) — **satu titik perubahan per modul**, memakai validator
  yang sudah ada, bukan menulis validator baru.

---

## 14. Database Changes

**Tidak ada.** Dikonfirmasi ulang: tidak ada kolom baru di `projects`, tidak ada migration baru
untuk skema Project.

---

## 15. Backend Changes — ringkasan (detail per file di §24)

- 6 service journal-builder diperbaiki groupingnya (§4) — pola sama diulang, bukan desain baru
  per file.
- `JournalValidationService` — konsolidasi validasi project ke `Project::isUsable()`.
- `CashPaymentService`, `CashReceiptService`, `BudgetSubmissionService`, `FixedAssetService` —
  tambah pemanggilan `BusinessReferenceValidator::project()` di titik create/update.
- `ProjectService` — tambah `AuditLogService` nullable + private `transition()` helper (pola
  `PurchaseOrderService`) untuk status guard + audit; auto-generate `code` saat create.
- Request classes line-level (Sales/Purchase/CashBank/Inventory/Journal) — tambah rule validasi
  `project_id` nullable `exists:projects,id` per baris, mengikuti pola `department_id` yang
  sudah ada di baris lain (mis. `PurchaseRequestLine`).

---

## 16. Frontend Changes — ringkasan (detail per file di §24)

- 5 form transaksi + line editor: tambah kolom/field Project selector (§11).
- `ProyekFormPage.tsx`: tab "Anggaran" **dihapus total** (keputusan produk, F10). Perbaikan F8
  (pakai `useProyekMutations`), F9 (tambah `on_hold` ke type).
- `proyekSchema.ts`/`proyek.types.ts`: tambah `on_hold`. Field `code` **tidak** ditambahkan ke
  form — auto-generate backend (keputusan produk, F7).

---

## 17. Reporting Changes

12 laporan yang diminta (Project Budget, Actual, Budget vs Actual, Variance, Utilization,
Revenue, Cost, Profitability, Margin, Cash Flow, Transactions, Budget Revision History) —
**semuanya sudah tercakup** sebagai preset `BudgetAnalysisService` (fase 2) + `BudgetProjectService`/
`BudgetCashService` (`phase-6`), tidak ada laporan baru yang butuh service terpisah. Yang baru
dari audit ini hanya **Project Transactions** (daftar mentah `journal_entry_lines` terfilter
`project_id`, drill-down level terbawah) — ini murni pemakaian `ReportQueryService` yang sudah
ada dengan filter `project_id`, tidak perlu service baru.

---

## 18. Permission & Audit Trail

**Permission**: Tidak ditemukan precedent field/visibility-level permission di seluruh
`config/permissions.php` (hanya precedent stage-based seperti `budgets.approve_head` vs
`budgets.approve_finance`). **Keputusan produk: tidak ada permission baru** — `projects.edit`
tetap dipakai untuk status transition, `projects.view` + `budgets.view` cukup untuk melihat
Project Financial Summary (data finansialnya adalah data Budget, digate `budgets.view`).

**Audit Trail**: `ProjectService` disuntik `AuditLogService` nullable-last (pola
`JournalEntryService.php:46-57`), private helper `audit()` dipanggil di setiap jalur tulis:
`project.created`, `project.updated`, `project.status_changed`, `project.activated`,
`project.deactivated`. Event constants baru ditambahkan ke `AuditEvent.php` (belum ada satu pun
`PROJECT_*` di sana). Tidak perlu audit untuk "Budget linked"/"Budget revision" — itu sudah
tercakup audit trail Budget module (`phase-5-versioning-dan-audit.md`).

---

## 19. Testing Strategy

**Wajib melalui APPLICATION FLOW asli** (UI/API → Service → Journal → Journal Entry Lines),
**bukan seeder** — audit ini membuktikan data demo (`TradingCompanyAccountingCycleSeeder`)
menulis `project_id` langsung ke `journal_entry_lines`, memotong kode aplikasi yang justru
terbukti membuang dimensi tersebut. Test yang hanya memeriksa seeder akan **lolos palsu**.

| # | Alur diuji | Assertion kunci |
|---|---|---|
| 1 | Sales Invoice (dgn & tanpa project) → Journal | `project_id` terisi di baris revenue; tanpa project → jurnal byte-for-byte identik dgn sebelum perubahan |
| 2 | Sales Return → Journal | sama |
| 3 | Vendor Bill → Journal | `project_id` di baris Inventory/FA-Clearing |
| 4 | Purchase Return → Journal | sama |
| 5 | Stock Movement (purchase_in, sales COGS, return, adjustment, opening_stock) → Journal | `project_id` per jalur, termasuk yang sebelumnya hardcoded 2-baris |
| 6 | Fixed Asset (capitalize, dispose, depreciation batch multi-aset) → Journal | tiap baris jurnal punya `project_id` aset masing-masing, termasuk saat 1 batch depresiasi menangani banyak aset dgn proyek berbeda |
| 7 | Cash/Bank → Journal | regresi — tetap benar (sudah OK) |
| 8 | Manual Journal → Project | regresi — tetap tervalidasi |
| 9 | Project Budget → Actual (lewat `BudgetActualService` fase 2) | actual dari transaksi asli (bukan seeder) cocok dgn jumlah manual |
| 10 | Budget vs Actual, Profitability, Cash Flow | konsisten dgn formula `phase-6`, memakai data dari test #1-8 |
| 11 | Status transition | semua transisi valid/invalid di tabel §12; `completed`/`cancelled` memblokir transaksi baru tapi tidak menyembunyikan data lama |

**Edge case wajib**: Project NULL, Project inactive (`is_active=false`), Project `completed`,
Project `cancelled`, project_id tidak valid, reversal/refund/return, multi-project dalam satu
dokumen (Sales Invoice 2 baris proyek berbeda, akun sama → 2 baris jurnal bukan 1), akun sama
lintas proyek, multi cost-center dalam satu proyek.

Regresi wajib penuh (menyentuh 4 modul transaksi):
```bash
cd /workspace/laravel_backend
vendor/bin/pint --test
php artisan test tests/Feature/Sales tests/Feature/Purchase tests/Feature/Inventory \
  tests/Feature/FixedAssets tests/Feature/CashBank tests/Feature/Journal \
  tests/Feature/MasterData tests/Feature/Reports tests/Feature/Architecture
```

---

## 20-23. P0 / P1 / P2 / P3 Implementation

(Detail file-by-file lengkap ada di §24. Ringkasan urutan & isi per prioritas.)

**P0 — Project Dimension Integrity** (backend only, tanpa ini semua Actual proyek salah)
- Composite grouping di 6 titik: Sales revenue, Sales return, Purchase bill, Purchase return,
  5 method Inventory (purchase_in/COGS/return/adjustment/opening_stock), 3 method Fixed Asset
  (capitalize/dispose/depreciation)
- Semua mengikuti SATU pattern: `implode('|', [$accountId, $departmentId ?: '', $projectId ?: ''])`
  meniru `StockMovementJournalService::opnameInventoryLines()`

**P1 — Project Input & Financial Usage**
- Project selector di 5 form transaksi (§11)
- Project Financial Summary, Profitability, Cash Flow — **sudah dirancang di `phase-6`**, tidak
  didesain ulang, hanya diberi disclaimer akurasi (§8) dan menunggu P0 selesai
- Perluasan validasi `BusinessReferenceValidator::project()` ke CashBank/Budget/FixedAssets (§13)

**P2 — Project Quality**
- Status transition guard + audit trail (§12, §18)
- Konsolidasi "usable" ke satu sumber, hapus `scopeUsable()` (§13)
- 3 bug frontend (F7-F9) + tab Anggaran dihapus (F10)

**P3 — Future (TIDAK dikerjakan sekarang)**
Project hierarchy/sub-project, project phases, milestones, forecast, scenario budgeting,
resource planning — tidak ada bukti kebutuhan di codebase saat ini; jalur penambahannya nanti
sama seperti FUTURE EXTENSION di `phase-8-dokumentasi.md` (kolom tambahan, bukan rombak engine).

---

## 24. File-by-File Change Plan

### P0 — Dimension Integrity

**FILE:** `app/Modules/Sales/Services/SalesInvoiceService.php`
**CURRENT ROLE:** Membangun journal entry untuk Sales Invoice (AR, revenue, tax, discount lines)
**PROBLEM:** `invoiceRevenueJournalLines()` (451-506) mengelompokkan `$revenueGrouped`/
`$discountGrouped` hanya per account_id (465, 467); baris jurnal yang di-emit (482-490) tanpa
`department_id`/`project_id`
**PROPOSED CHANGE:** Ubah key grouping jadi komposit `accountId|departmentId|projectId`; saat
membentuk `$lines`, pecah kembali key dan sertakan `department_id`/`project_id`
**REASON:** Actual Revenue per proyek selalu 0 tanpa ini; sudah didiagnosis di `phase-4`
**DEPENDENCY:** Tidak ada — bisa dikerjakan pertama
**RISK:** Total per akun harus tetap sama, hanya jumlah baris bertambah; Σdebit=Σkredit wajib
tetap balance
**TEST:** `tests/Feature/Sales/SalesInvoiceDimensionTest.php` — sesuai §19 kasus #1

**FILE:** `app/Modules/Sales/Services/SalesReturnService.php`
**CURRENT ROLE:** Journal untuk retur penjualan
**PROBLEM:** `returnAccountGroups()` (297-311) grouping `$accountId` saja (307); `SalesReturnLine`
sudah punya `department_id`/`project_id` (`normalizeReturnLines():191`, `createFromSalesInvoice/
DeliveryOrder():114,125`) tapi dibuang saat jurnal dibentuk
**PROPOSED CHANGE:** Sama polanya dengan SalesInvoiceService — composite grouping
**REASON:** Retur proyek harus mengurangi Actual Revenue proyek yang benar, bukan proyek lain/tak berdimensi
**DEPENDENCY:** Tidak ada
**RISK:** Sama seperti di atas — balance jurnal
**TEST:** kasus #2 §19

**FILE:** `app/Modules/Purchase/Services/VendorBillService.php`
**CURRENT ROLE:** Journal untuk Vendor Bill (Inventory/FA-Clearing debit, AP/tax credit)
**PROBLEM:** `billDebitJournalLines()` (481-536) grouping `$accountId` saja (510)
**PROPOSED CHANGE:** Composite grouping sama pattern. **Catatan**: baris ini hanya Inventory/FA
Clearing (neraca) — dampaknya untuk WIP tracking proyek (kontraktor/manufaktur), bukan P&L
langsung. Tetap diperbaiki untuk konsistensi arsitektur "dimensi tidak boleh hilang"
**REASON:** Project WIP/inventory value per proyek
**DEPENDENCY:** Tidak ada
**RISK:** Rendah — hanya menambah baris saat >1 proyek per bill
**TEST:** kasus #3 §19

**FILE:** `app/Modules/Purchase/Services/PurchaseReturnService.php`
**CURRENT ROLE:** Journal retur pembelian
**PROBLEM:** `returnAccountGroups()` (297-311) sama persis pola VendorBillService — grouping 307
**PROPOSED CHANGE:** Composite grouping
**REASON:** Konsistensi dengan Purchase Bill
**DEPENDENCY:** Tidak ada
**RISK:** Rendah
**TEST:** kasus #4 §19

**FILE:** `app/Modules/Inventory/Services/StockMovementJournalService.php`
**CURRENT ROLE:** Journal builder untuk semua pergerakan stok (purchase_in, sales COGS, return,
adjustment, opening_stock, opname)
**PROBLEM:** 5 dari 7 jalur membuang dimensi — `inventoryDebitLines()` (183-200, key 188),
`inventoryCreditLines()` (279-296, key 284), `cogsDebitLines()` (298-315, key 303),
`cogsCreditLines()` (345-362, key 350), `interimCreditLines()` (317-343, key 324) hanya
grouping per account; `createAdjustmentJournal()` (76-107) dan `createOpeningStockJournal()`
(155-168) malah tidak grouping sama sekali (array literal 2 baris)
**PROPOSED CHANGE:** Ubah kelima method grouping ke composite key persis pola
`opnameInventoryLines()` (baris 217-222, SUDAH BENAR — dijadikan referensi langsung, bukan
didesain ulang). `createAdjustmentJournal()`/`createOpeningStockJournal()` diubah dari array
literal menjadi grouping composite juga (perlu groupBy per baris movement, bukan asumsi 1 baris)
**REASON:** Ini prioritas TERTINGGI — COGS adalah komponen cost terbesar untuk Project
Profitability; tanpa ini, Actual Cost proyek manapun akan salah signifikan
**DEPENDENCY:** Tidak ada
**RISK:** File ini paling banyak method yang berubah (7) — risiko regresi tertinggi di P0.
Wajib per-method test terpisah, bukan satu test besar
**TEST:** `tests/Feature/Inventory/StockMovementDimensionTest.php` — semua 7 jalur, kasus #5 §19

**FILE:** `app/Modules/FixedAssets/Services/FixedAssetService.php`
**CURRENT ROLE:** Lifecycle Fixed Asset (create, capitalize, dispose, depreciation run)
**PROBLEM:** `capitalize()` (183-186), `dispose()` (256-275), `postDepreciationPeriod()`
(352-377, grouping BATCH lintas-aset di 361-362) — semua membuang `$asset->project_id`/
`department_id` meski field itu sudah ada di model (`assetPayload():471-472`)
**PROPOSED CHANGE:** `capitalize()`/`dispose()` — sertakan `$asset->project_id`/`department_id`
langsung di setiap baris literal (tidak perlu grouping, satu aset = 1 event). `postDepreciationPeriod()`
— ubah grouping key dari `'dr_'.expense`/`'cr_'.accumulated` jadi menyertakan project/department
tiap aset: `'dr_'.expense.'|'.dept.'|'.proj` — ini akan memecah baris per kombinasi
akun+dimensi, bukan satu baris per akun untuk semua aset
**REASON:** Depreciation adalah biaya berulang penting untuk Project Cash Flow/Profitability
proyek berbasis aset (kontraktor, manufaktur); batch leak ini kehilangan dimensi SETIAP aset
sekaligus, bukan cuma satu transaksi
**DEPENDENCY:** Tidak ada
**RISK:** `postDepreciationPeriod()` bisa menghasilkan lebih banyak baris jurnal per run
(sebelumnya 1 baris debit + 1 kredit per akun, sekarang bisa N baris per kombinasi
akun×dimensi) — pastikan performa tetap wajar untuk perusahaan dengan banyak aset per proyek
**TEST:** `tests/Feature/FixedAssets/FixedAssetDimensionTest.php` — kasus #6 §19, termasuk
skenario 1 batch depresiasi menangani aset dari 3 proyek berbeda

**FILE:** `app/Modules/Journal/Services/JournalValidationService.php`
**CURRENT ROLE:** Validasi baris manual journal, termasuk dimensi (`validateDimensions()`, 83-141)
**PROBLEM:** Baris 124-133 reimplementasi manual aturan "project usable" (`is_active` AND
`status==='active'`), divergen dari `Project::isUsable()`
**PROPOSED CHANGE:** Ganti pemeriksaan manual dengan pemanggilan `Project::isUsable()` (atau
`BusinessReferenceValidator::project()` kalau ingin exception message konsisten)
**REASON:** Satu sumber kebenaran (§13) — F1
**DEPENDENCY:** Tidak ada
**RISK:** Rendah — perilaku seharusnya identik, hanya sumbernya disatukan
**TEST:** Test existing untuk validasi project di manual journal harus tetap lulus

### P1 — Input & Financial Usage

**FILE:** `app/Shared/Validation/BusinessReferenceValidator.php`
**CURRENT ROLE:** Validasi referensi bisnis (`project()`, `department()`, dll) untuk dokumen
transaksional
**PROBLEM:** Tidak dipanggil dari CashBank, Budget, FixedAssets (F3)
**PROPOSED CHANGE:** Tidak ada perubahan pada file ini sendiri — perubahan ada di 3 file
pemanggil (di bawah), yang menambahkan pemanggilan `$this->validator->project($id)` di titik
input mereka
**REASON:** Konsistensi validasi proyek "usable" di semua modul yang menerima `project_id`
**DEPENDENCY:** Tidak ada
**RISK:** Rendah
**TEST:** Test negatif — input `project_id` milik proyek `cancelled` ke CashPayment/
BudgetSubmission/FixedAsset harus ditolak 422

**FILE:** `app/Modules/CashBank/Services/CashPaymentService.php`, `CashReceiptService.php`
**CURRENT ROLE:** Journal Cash Payment/Receipt (sudah benar soal propagasi dimensi, §4)
**PROBLEM:** `project_id` di-copy dari line tanpa validasi keberadaan/usability (F3)
**PROPOSED CHANGE:** Tambah pemanggilan `BusinessReferenceValidator::project()` saat build/
validate baris, sebelum journal dibentuk
**REASON:** Cegah posting ke proyek yang sudah `cancelled`/`completed`
**DEPENDENCY:** Tidak ada
**RISK:** Rendah — hanya menambah validasi, tidak mengubah journal building yang sudah benar
**TEST:** kasus edge "Project cancelled" §19

**FILE:** 6 form transaksi FE, SEMUA sudah memakai `LineItemsTable`
(`SalesInvoiceFormPage.tsx`, `VendorBillFormPage.tsx`, `CashPaymentFormPage.tsx`,
`CashReceiptFormPage.tsx`, `StockAdjustmentFormPage.tsx`, `StockMovementFormPage.tsx`,
`JournalFormPage.tsx`)
**CURRENT ROLE:** Form input transaksi, masing-masing dengan `EditableLine` interface sendiri +
array `columns: LineItemColumn<EditableLine>[]` yang dirender lewat `<LineItemsTable columns=
{columns} .../>` (compact table view — sama komponen dengan `GoodsReceiptFormPage.tsx`,
"form penerimaan")
**PROBLEM:** Tidak ada kolom untuk mengisi Project di `columns` manapun (§11) — Manual Journal
kekecualian sebagian (tipe & `LineItemsTable` sudah ada, kolomnya belum)
**PROPOSED CHANGE:** Tambah `project_id: number | null` (+ `department_id` kalau relevan) ke
`EditableLine`; tambah **satu entri baru** di array `columns` dengan `render: ({ item, onUpdate,
isReadOnly }) => <SearchableSelect value={item.project_id} onChange={(v) => onUpdate('project_id',
v)} onSearch={proyekApi.search} disabled={isReadOnly} size="sm" .../>` — pola identik kolom
`Input`/`Select` yang sudah ada di `columns` masing-masing form (mis.
`GoodsReceiptFormPage.tsx:168-197`); **tidak membuat tabel atau komponen baru**; sertakan
`project_id` di payload save
**REASON:** Tanpa ini, `project_id` tetap kosong di produksi meski backend sudah benar (§11).
Menambah kolom ke `LineItemsTable` existing menjaga konsistensi visual dengan form penerimaan
dan seluruh form transaksi lain
**DEPENDENCY:** P0 selesai (percuma isi data yang akan dibuang backend)
**RISK:** `JournalFormPage.tsx` risiko lebih rendah (tipe & `LineItemsTable` sudah ada, tinggal 1
kolom + wiring data); 6 form lain risiko sedang (kolom baru + payload baru, harus tidak mengubah
kolom lain atau lebar tabel jadi terlalu padat — cek `width` per kolom di `LineItemColumn`)
**TEST:** `npm run build`, `npm run lint`, uji manual submit dengan & tanpa Project terisi,
verifikasi visual tabel tetap compact (tidak overflow di layar sempit)

### P2 — Quality

**FILE:** `app/Modules/MasterData/Services/ProjectService.php`
**CURRENT ROLE:** CRUD Project, no constructor, no audit
**PROBLEM:** F2 (transisi status bebas), F4 (nol audit), F7 (code tidak terkirim FE)
**PROPOSED CHANGE:** Tambah constructor dgn `?AuditLogService $auditLogService = null`
(nullable-last, pola `JournalEntryService.php:46-57`); tambah private `transition()` mengikuti
`PurchaseOrderService::transition()` — guard `in_array($project->status, $from, true)`, throw
422 kalau invalid, lalu audit. `update()` diubah: kalau `status` berubah, panggil `transition()`
bukan `fill()` langsung. `create()` — generate `code` otomatis (pola sequence/prefix, mis.
`PRJ-00001`) kalau tidak dikirim request; cek pola auto-number existing (`DocumentNumberService`)
untuk reuse mekanisme, bukan menulis generator baru; `StoreProjectRequest` ubah `code` jadi opsional
**REASON:** F2, F4, F7, §12, §18
**DEPENDENCY:** Tidak ada
**RISK:** Perlu pastikan test existing yang mengubah status via `update()` masih lulus dengan
transisi valid; test baru untuk transisi invalid; pastikan unique constraint `code` tetap
terjaga saat auto-generate
**TEST:** kasus #11 §19, semua baris tabel §12; create Project tanpa `code` dari UI berhasil,
dua create berurutan menghasilkan `code` unik

**FILE:** `app/Modules/MasterData/Models/Project.php`
**CURRENT ROLE:** Model, punya `scopeUsable()` dead code
**PROBLEM:** F1 (duplikasi aturan usable)
**PROPOSED CHANGE:** Hapus `scopeUsable()` — dikonfirmasi dead code, `isUsable()` tetap
satu-satunya sumber kebenaran
**REASON:** §13
**DEPENDENCY:** Tidak ada
**RISK:** Rendah, perubahan kecil (pastikan benar-benar tidak dipanggil di tempat lain sebelum
dihapus — grep ulang saat eksekusi)
**TEST:** Tidak perlu test baru (menghapus dead code)

**FILE:** `frontend/src/modules/master-data/schemas/proyekSchema.ts`
**CURRENT ROLE:** Zod schema form Project — status tanpa `on_hold`
**PROBLEM:** F9
**PROPOSED CHANGE:** Ubah enum status jadi `['active','on_hold','completed','cancelled']`.
Field `code` **tidak** ditambahkan ke form (auto-generate backend)
**REASON:** F9
**DEPENDENCY:** `ProjectService::create()` auto-generate `code` harus selesai duluan
**RISK:** Rendah
**TEST:** Manual test create Project dari UI setelah perbaikan

**FILE:** `frontend/src/modules/master-data/pages/ProyekFormPage.tsx`
**CURRENT ROLE:** Form create/edit Project, termasuk tab "Anggaran" yang mati (F10)
**PROBLEM:** F8 (tidak pakai `useProyekMutations`), F10 (tab Anggaran disconnected)
**PROPOSED CHANGE:** Ganti pemanggilan `proyekApi.create/update` langsung dengan
`useProyekMutations().create/update` (hook sudah ada & benar, `useSimpleLists.ts:206-229`,
tinggal diimpor dan dipakai). Tab "Anggaran" **dihapus total** (bukan link) — keputusan produk:
tidak menambah dependency ke Budget module dalam plan ini
**REASON:** F8, F10 — cegah cache stale dan cegah dua sumber kebenaran anggaran proyek
**DEPENDENCY:** Tidak ada
**RISK:** User yang terbiasa pakai tab lama akan kehilangan (fitur itu toh tidak pernah
tersimpan) — komunikasikan sebagai perbaikan, bukan penghapusan fitur
**TEST:** Manual — buat/edit proyek, verifikasi cache ter-invalidate (list ter-refresh otomatis)

---

## 25. Risks

| Risiko | Mitigasi |
|---|---|
| `StockMovementJournalService` — 7 method berubah dalam 1 file, risiko regresi tertinggi di P0 | Test per-method terpisah, bukan 1 test besar; jalankan regresi Inventory penuh sebelum lanjut ke modul lain |
| `postDepreciationPeriod()` batch bisa menghasilkan jauh lebih banyak baris jurnal jika aset lintas-proyek banyak | Uji dengan dataset realistis (mis. 50 aset, 5 proyek) sebelum deploy; pantau waktu eksekusi run bulanan |
| Data demo tidak valid untuk verifikasi (seeder menulis project_id langsung) | SEMUA test P0 wajib lewat service/API asli, eksplisit dicek di code review — lihat §19 |
| UI selector ditambah sebelum P0 selesai → user mengisi Project tapi datanya tetap hilang di ledger | Urutan implementasi mengunci P0 sebelum P1 (§20-23); jangan deploy frontend selector duluan |
| Menghapus tab "Anggaran" dianggap regresi fitur oleh user yang terbiasa pakai | Komunikasi eksplisit: fitur itu tidak pernah tersimpan (dibuktikan di F10), bukan capability yang hilang |
| Menyentuh 6 service transaksi (Sales, Purchase, Inventory, FixedAsset) sekaligus melanggar semangat "jangan refactor modul tak diminta" | Scope dikunci ketat: HANYA mengubah grouping key + emit dimension, tidak menyentuh logika lain di method yang sama |

---

## 26. Acceptance Criteria

1. Semua 6 titik leak di §4 menghasilkan `journal_entry_lines.project_id`/`department_id`
   terisi ketika dokumen sumber punya dimensi, dan **byte-for-byte identik** dengan sebelum
   perubahan ketika dokumen sumber tidak punya dimensi.
2. `Project::isUsable()` adalah satu-satunya sumber kebenaran; `JournalValidationService` tidak
   lagi reimplementasi logikanya sendiri; `scopeUsable()` dihapus.
3. `BusinessReferenceValidator::project()` dipanggil dari CashBank, Budget, dan FixedAssets
   (sebelumnya bolong).
4. Status Project punya guard transisi eksplisit (tabel §12), dengan audit log tertulis di
   setiap perubahan.
5. Selector Project tersedia (opsional) di Sales Invoice, Vendor Bill, Cash Payment/Receipt,
   Stock Adjustment/Movement, dan Manual Journal.
6. Tab "Anggaran" di `ProyekFormPage.tsx` sudah dihapus.
7. 3 bug frontend (F7 code auto-generate, F8 cache, F9 on_hold) diperbaiki.
8. Tidak ada perubahan skema tabel `projects`. Tidak ada permission baru.
9. Regresi penuh `tests/Feature/{Sales,Purchase,Inventory,FixedAssets,CashBank,Journal,
   MasterData,Reports,Architecture}` hijau.

---

## 27. Recommended Implementation Order

1. **P0 backend** — 6 file journal-builder (§24), urutan: Inventory COGS dulu (dampak
   terbesar) → Fixed Asset depreciation → Sales revenue (tinggal eksekusi `phase-4` yang sudah
   dirancang) → sisanya (return, purchase bill, adjustment, opening_stock, capitalize/dispose)
2. **P0 konsolidasi validasi** — `JournalValidationService` pakai `Project::isUsable()`
3. **P1 backend** — perluasan `BusinessReferenceValidator::project()` ke CashBank/Budget/FixedAssets
4. **P1 frontend** — 5 selector Project (setelah P0 backend live, supaya data yang diisi user
   benar-benar sampai ke ledger)
5. **P2** — status transition guard + audit trail Project, 3 bug frontend, hapus tab Anggaran
6. Verifikasi menyeluruh mengikuti pola `phase-8-dokumentasi.md` (edge case matrix + manual
   procedure), diperluas dengan skenario multi-proyek per dokumen

P3 tidak dijadwalkan.

---

## Keputusan pemilik produk (dikonfirmasi)

1. `Project::scopeUsable()` — **dihapus** (dead code, satu sumber kebenaran tetap `isUsable()`).
2. Tab "Anggaran" di `ProyekFormPage.tsx` — **dihapus total**, tanpa link ke Budget module
   (tidak menambah dependency lintas-plan; link bisa ditambah nanti setelah Budget module live).
3. Permission status Project — **tetap gabung dengan `projects.edit`**, tidak ada
   `projects.transition` baru.
4. Field `code` saat create Project — **auto-generate di backend** oleh `ProjectService`, form
   tidak perlu input manual.

---

## Status implementasi

Belum dimulai. Dokumen ini adalah plan — eksekusi P0–P2 menunggu instruksi lanjutan.
