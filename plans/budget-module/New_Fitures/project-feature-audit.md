# Audit Fitur Project — Laporan

> Audit read-only, tidak ada file yang diubah. Dilakukan sebagai pendalaman atas dimensi
> `Project` yang dipakai di rencana Budget (`phase-4`, `phase-6`), karena Project Budget,
> Project Profitability, dan Project Cash Flow bergantung penuh pada data ini benar.
>
> **Temuan utama: kebocoran dimensi proyek jauh lebih luas dari yang tercatat di
> `phase-4-dimensi-revenue.md`.** Dokumen itu perlu dibaca bersama laporan ini — lihat §7.

---

## 1. Model & Skema Data

Model: `app/Modules/MasterData/Models/Project.php`. Migration tenant:
`2026_05_19_000002_create_projects_table.php`.

```
id, code (unique), name, description, start_date, end_date,
status (string, default 'active'), is_active (bool, default true),
metadata (json), timestamps
```

- Tidak ada `company_id` (normal — isolasi sudah di level file SQLite per tenant).
- Tidak ada soft delete — nonaktif lewat `is_active`, bukan `deleted_at`.
- **Tidak ada hierarki** (`parent_id`) — Project adalah entitas flat, tidak ada sub-proyek/phase.
  Cocok dipakai sebagai dimensi tunggal di `budget_lines`, tidak perlu logika drill-down
  bertingkat di dalam entitas itu sendiri.
- Relasi model hanya satu: `journalEntryLines(): HasMany` ke `JournalEntryLine`.
- Scope `scopeUsable()` (`is_active=true AND status='active'`) **ada tapi tidak pernah dipanggil**
  di manapun (`grep` nol hasil). Aturan yang sama ditulis ulang lewat method instance
  `isUsable()` di `BusinessReferenceValidator::project()`, dan lagi secara manual di
  `JournalValidationService.php:124-133`. Bukan bug, tapi tiga tempat menulis aturan yang sama
  — kalau kriteria "usable" berubah, mudah lupa satu tempat.

---

## 2. Service & Business Logic

`app/Modules/MasterData/Services/ProjectService.php`.

- CRUD standar + `activate()`/`deactivate()` (toggle `is_active`).
- `markCompleted()`, `markOnHold()`, `cancel()` — **ada di service tapi tidak diekspos controller
  manapun**, dan **tidak ada guard transisi status**: langsung `$project->status = '...'` tanpa
  memeriksa status asal. `update()` (yang memang dipanggil dari controller) menerima field
  `status` mentah dari request dan hanya divalidasi `in:active,completed,on_hold,cancelled` —
  jadi transisi bebas ke arah mana pun (proyek `completed` bisa di-`update` balik ke `active`
  lewat form edit biasa).
- Tidak ada validasi budget-vs-actual di level Project — itu sepenuhnya domain modul Budget,
  sesuai desain "ONE ENGINE".

---

## 3. Controller, Request, Routes, Permission

Path: `/api/master-data/projects` (+ `/{id}`, `/{id}/activate`, `/{id}/deactivate`).
Permission: `projects.view`, `projects.create`, `projects.edit`, `projects.deactivate`
(`config/permissions.php:50-53`) — tidak ada `projects.delete`, konsisten (tidak ada route DELETE).

`proyekApi.search()` di frontend memanggil `index` yang sama dengan `{search, per_page:10,
status:'active'}`, bukan endpoint search terpisah.

Tidak ada endpoint `adjacent` (navigasi prev/next) yang ada di `ChartOfAccount`/`Contact`/
`Product` — inkonsistensi kecil, bukan blocker.

---

## 4. Kebocoran Dimensi — Temuan Inti

Tabel status per modul, sampai ke `journal_entry_lines.project_id`:

| Modul | Dimensi tersimpan di line dokumen? | Dimensi sampai ke journal? |
|---|---|---|
| Sales (quotation→order→DO→invoice) | ✅ | ❌ **dibuang** di `invoiceRevenueJournalLines()` |
| Purchase (PR/PO/GR/bill) | ✅ | ❌ **dibuang** di `billDebitJournalLines()` (khusus baris Inventory/FA Clearing) |
| CashBank (payment/receipt) | ✅ | ✅ utuh |
| Inventory/Stock Movement | ✅ (di stock_movement_lines) | ⚠️ **hanya jalur stock opname**; jalur umum (purchase_in, COGS penjualan, adjustment, sales_return_in, opening_stock) **membuang dimensi** |
| Fixed Assets | ✅ (field di level `fixed_assets`, bukan per-line) | ❌ **dibuang total** — capitalization, disposal, depreciation semua tanpa `project_id` |
| Journal manual | ✅ (input request) | ✅ utuh + tervalidasi |
| Budget | ✅ | ✅ (`budget_lines.project_id`, sudah dikonfirmasi di audit sebelumnya) |
| Reports | filter `project_id` ada di 20 request class | ✅ tapi hasilnya hanya akurat sejauh baris di atas tidak bocor |

### Yang sudah diketahui dan direncanakan diperbaiki (`phase-4`)

`SalesInvoiceService::invoiceRevenueJournalLines()` (baris ±451-506) mengelompokkan hanya per
`revenueAccountId`, membuang `project_id`/`department_id` meski `sales_invoice_lines` punya
keduanya. Ini sudah tercatat dan punya rencana perbaikan ±20 baris di `phase-4-dimensi-revenue.md`.

### Yang BELUM tercatat di dokumen manapun — temuan baru audit ini

**A. `StockMovementJournalService` — bocor di luar jalur opname.**
`opnameInventoryLines()`/`opnameOffsetLines()` (baris 212-263) memang mengelompokkan per
`(account, department_id, project_id)` dengan benar. Tapi jalur umum yang jauh lebih sering
dipakai — `inventoryDebitLines()`, `inventoryCreditLines()`, `cogsDebitLines()`,
`cogsCreditLines()`, `interimCreditLines()` (baris 183-343) yang menangani `purchase_in`,
**COGS penjualan**, `sales_return_in`, `adjustment_in/out`, `opening_stock` — semuanya
mengelompokkan **hanya per `account_id`**, tanpa dimensi apa pun.

Dampak langsung ke rencana Budget: **COGS adalah komponen biaya terbesar di kebanyakan Project
Profitability**, dan baris ini yang menghitungnya. Kalau tidak diperbaiki, `Actual Cost` proyek
akan under-reported signifikan — bukan cuma revenue yang hilang (seperti fokus `phase-4`
sekarang), tapi cost utamanya juga.

**B. `FixedAssetService` — journal capitalization/disposal/depreciation tidak pernah membawa dimensi.**
`FixedAsset` model punya `project_id` sendiri (`FixedAssetService.php:471-472` saat aset
dibuat), tapi private helper `journal()` yang dipanggil untuk capitalization (183-186),
disposal (256-275), dan depreciation (351-377) **tidak pernah** menyertakan `project_id`/
`department_id` di baris jurnal manapun. Depresiasi rutin — biaya berulang yang penting untuk
Project Cash Flow proyek berbasis aset (kontraktor, manufaktur) — karena itu tidak akan pernah
muncul saat difilter per proyek di ledger.

**Catatan tentang `phase-4-dimensi-revenue.md` yang perlu dikoreksi**: dokumen itu menandai
Inventory/COGS dan Fixed Asset dengan ✅ (mengutip `StockMovementJournalService.php:234-258`
dan `FixedAssetService.php:471-472`). Kutipan itu benar tapi **tidak lengkap** — baris 234-258
hanya mencakup opname, dan baris 471-472 hanya field level-aset, bukan journal. Kesimpulan ✅
di dokumen itu perlu direvisi jadi ⚠️/❌ sesuai temuan A dan B di atas sebelum fase 4/6
dieksekusi, supaya cakupan perbaikannya tidak berhenti di Sales Invoice saja.

---

## 5. Frontend

Lokasi: `frontend/src/modules/master-data/{pages,services,schemas,types}` — `ProyekPage.tsx`,
`ProyekFormPage.tsx`, `proyekApi.ts`, `proyekSchema.ts`, `proyek.types.ts`.

### Temuan bug fungsional

1. **Form create Project tidak mengirim `code`.** `proyekSchema.ts` hanya punya
   `name, status, start_date, end_date`; tidak ada input `code` di `ProyekFormPage.tsx`.
   Backend `StoreProjectRequest` mewajibkan `code`. Tanpa mekanisme auto-generate (tidak
   ditemukan di service/frontend manapun), `POST /master-data/projects` dari form ini
   kemungkinan **selalu gagal 422**. Perlu verifikasi manual — audit ini tidak menjalankan
   mutasi apa pun.
2. **Cache tidak invalidasi setelah create/update** — `ProyekFormPage.tsx` memanggil
   `proyekApi.create/update` langsung, bukan lewat hook mutasi bersama
   (`useSimpleLists.ts` punya `useProyekMutations()` yang tidak dipakai) — list bisa
   menampilkan data basi.
3. **Type `ProyekStatus` tidak lengkap** — `'active'|'completed'|'cancelled'`, hilang
   `'on_hold'` padahal backend mengizinkannya dan data demo tenant 1 memang punya 1 proyek
   berstatus itu. Label/warna status akan hilang di UI untuk proyek `on_hold`.

### Temuan desain — tabrakan dengan rencana Budget

`ProyekFormPage.tsx` punya **tab "Anggaran"** (baris ±178-273) yang menampilkan tabel baris
anggaran dan kartu "Total Pendapatan / Total Pengeluaran / Surplus-Defisit". **Ini state React
lokal murni** — `onSubmit` tidak pernah mengirim `budgetLines` ke backend, jadi tab ini
tampilan tanpa penyimpanan, hilang setiap refresh. Ini akan **bentrok secara UX** dengan
`ProjectFinancialSummaryPage` yang direncanakan di `phase-7-frontend.md` — dua tempat berbeda
yang sama-sama mengklaim menampilkan "anggaran proyek". **Perlu keputusan sebelum fase 7
dikerjakan**: hapus tab ini, atau ubah jadi tautan ke halaman Budget yang sebenarnya.

### Cakupan selector Project di UI transaksi

Selector Project (`SearchableSelect` + `proyekApi.search`) hanya ditemukan di: komponen modul
Budget (3 file), `ReportParameterModal`/`AccountLedgerPage` (laporan), dan **satu-satunya form
transaksi non-Budget/Report**: `FixedAssetFormPage.tsx`.

**Modul Sales, Purchase, Cash-Bank, Inventory, dan form Journal manual — nol referensi Project
di frontend.** Artinya meski backend mendukung `project_id` di level line untuk kelima modul
ini, **tidak ada tempat user bisa memilih Project saat input transaksi**, kecuali lewat API
langsung atau import. Ini menjelaskan mengapa data demo (§6) hanya berisi `project_id` dari
seeder, bukan dari alur UI nyata — dan berarti bahkan setelah semua leak di §4 diperbaiki,
`project_id` di produksi akan tetap kosong sampai form-form transaksi ini diberi selector.

---

## 6. Data Eksisting (tenant demo)

| Tenant | Total project | Status | journal_entry_lines dgn project_id |
|---|---|---|---|
| company_000001 | 6 | 4 active, 1 completed, 1 on_hold | 54, semua `source_module='dummy_cycle'` |
| company_000002 | 3 | 1 active, 2 completed | 319 — cash_bank 142, purchase 65, sales 65, inventory 26, adjustment 10, opening_balance 7, journal 4 |

**Peringatan penting**: baris `sales`/`purchase` di company_000002 berasal dari
`TradingCompanyAccountingCycleSeeder.php` yang menulis `journal_entry_lines.project_id`
**langsung**, memotong jalur `SalesInvoiceService`/`VendorBillService` yang sebenarnya (yang
terbukti membuang dimensi ini). **Angka ini bukan bukti bahwa leak di §4 tidak berdampak** —
sebaliknya, ini adalah data sintetis yang menutupi bug tersebut. Jangan pakai tenant demo untuk
menguji apakah leak sudah beres; harus lewat alur aplikasi nyata (buat invoice via UI/API,
periksa jurnal yang dihasilkan).

---

## 7. Bagaimana ini mengubah rencana Budget yang sudah ada

`phase-4-dimensi-revenue.md` saat ini scoped ke satu method (`SalesInvoiceService`) dengan
alasan itu "satu-satunya pengecualian". Audit ini menunjukkan ada tiga celah lagi:

| Celah | Dampak ke metrik Budget | Perlu masuk fase mana |
|---|---|---|
| `StockMovementJournalService` jalur umum (bukan opname) | **Actual Cost** proyek (COGS) under-reported | Perluasan `phase-4`, atau fase baru sebelum `phase-6` |
| `FixedAssetService` (capitalization/disposal/depreciation) | Biaya depresiasi tidak pernah masuk Project Cost | Perluasan `phase-4`, atau fase baru sebelum `phase-6` |
| Tidak ada selector Project di form Sales/Purchase/CashBank/Inventory/Journal | `project_id` tetap kosong di produksi meski backend & journal sudah diperbaiki | `phase-7` (frontend) — di luar cakupan `phase-4` yang backend-only |

**Rekomendasi**: sebelum mengeksekusi `phase-6` (Project Profitability/Cash Flow), `phase-4`
perlu diperluas cakupannya dari "Sales Invoice saja" menjadi ketiga celah di atas —
kalau tidak, `Actual Cost` yang ditampilkan di `ProjectFinancialSummaryPage` akan secara
konsisten lebih rendah dari kenyataan, dan margin proyek akan terlihat lebih baik dari yang
sebenarnya. Ini bukan perubahan arsitektur — pola perbaikannya identik dengan yang sudah
didesain untuk Sales Invoice (ubah kunci grouping jadi komposit), hanya lokasinya bertambah.

Keputusan cakupan (perluas `phase-4` vs fase baru terpisah, dan apakah selector Project di UI
transaksi masuk cakupan sekarang atau FUTURE) **diserahkan ke pemilik produk** — laporan ini
tidak mengubah dokumen fase manapun.

---

## 8. Ringkasan temuan

1. Model Project flat, tanpa hierarki — aman dipakai sebagai dimensi tunggal.
2. Kebocoran dimensi ke `journal_entry_lines.project_id` lebih luas dari catatan `phase-4`:
   Sales Invoice (sudah tercatat), plus **Vendor Bill**, **StockMovementJournalService jalur
   umum**, dan **seluruh journal Fixed Asset** (baru, belum tercatat di dokumen manapun).
3. **COGS dan depresiasi** — dua komponen biaya besar — sama sekali tidak per-proyek di
   ledger saat ini. Ini prioritas lebih tinggi dari revenue Sales Invoice untuk akurasi
   Project Profitability, karena COGS/depresiasi biasanya lebih besar nilainya.
4. Tidak ada UI input Project di form transaksi manapun kecuali Fixed Asset — masalah adopsi
   terpisah dari bug backend.
5. Tab "Anggaran" palsu di `ProyekFormPage.tsx` perlu keputusan desain sebelum `phase-7`.
6. Tiga bug kecil di frontend Project (code tidak terkirim, cache tidak invalidasi, status
   `on_hold` hilang dari type) — di luar cakupan Budget tapi mempengaruhi kualitas data
   dimensi proyek itu sendiri.
7. Data demo tidak bisa dipakai memverifikasi perbaikan leak — seeder menulis `project_id`
   langsung ke jurnal, bukan lewat kode aplikasi.
