# Unified Multidimensional Budgeting — Index & Progress Ledger

> **Agent: baca file ini PERTAMA setiap sesi**, lalu `phase-0-context-rules-guardrails.md`.
> Phase 0 memuat aturan main yang mengikat seluruh fase — jangan mulai fase mana pun
> sebelum membacanya.
>
> Rencana ini **menyempurnakan modul anggaran yang sudah ada**, bukan membangunnya dari nol.

## Konteks — kenapa rencana ini ada

Brief pemilik produk ada di `instruction.md` (834 baris): satu budget engine, banyak dimensi,
banyak view — bukan lima engine terpisah. Instruction itu melarang coding dan hanya meminta
audit + implementation plan. Audit sudah dilakukan; hasilnya ada di `phase-0`.

Rencana sebelumnya (`../README.md`, Fase 0–3, selesai 2026-08-09) **menghidupkan** modul yang
mati: memperbaiki kontrak service, menambah pintu masuk, menutup lubang alur kerja, dan
menyamakan ke pola shell. Rencana ini melanjutkannya ke lapis berikutnya — **mengubah bentuk
data supaya benar-benar multidimensi.**

## Peta dokumen

| Fase | Judul | File | Status |
|------|-------|------|--------|
| 0 | Context, Rules & Guardrails | `phase-0-context-rules-guardrails.md` | ✅ Selesai¹ |
| 0.1 | Satukan Form Baris-Item ke `LineItemsTable` | `phase-0.1-reusable-line-items-component.md` | ✅ Selesai² |
| 1 | Fondasi Data | `phase-1-fondasi-data.md` | ✅ Selesai³ |
| 2 | Mesin Inti | `phase-2-mesin-inti.md` | ✅ Selesai³ |
| 3 | Perbaikan 4 Cacat | `phase-3-perbaikan-cacat.md` | ✅ Selesai⁴ |
| 4 | Dimensi Revenue | `phase-4-dimensi-revenue.md` | ✅ Selesai⁴ |
| 5 | Versioning & Audit | `phase-5-versioning-dan-audit.md` | ✅ Selesai⁴ |
| 6 | View Turunan & Permission | `phase-6-view-turunan-dan-permission.md` | ✅ Selesai⁴ |
| 7 | Frontend | `phase-7-frontend.md` | ✅ Selesai⁴ |
| 8 | Dokumentasi | `phase-8-dokumentasi.md` | 🔄 Berjalan⁵ |
| — | Project Dimension & Budgeting Readiness (audit + plan, menggantikan/memperluas bagian Project di fase 4 & 6) | `project-dimension-budgeting-readiness-plan.md` | ✅ Plan selesai — implementasi belum dimulai |

> Status yang boleh: `⬜ Belum`, `🔄 Berjalan`, `✅ Selesai`.

¹ **Fase 0 (2026-08-14)** — dokumen dibaca penuh dan fakta kuncinya diverifikasi ulang ke kode:
`cost_center` 0 hit di `laravel_backend/{app,database,config,routes}` + `frontend/src`,
`app/Modules/Budget/` berisi Controllers/Models/Requests/Routes/Services, dan `ModuleKey` di
`frontend/src/stores/useTabStore.ts:18-28` memang tidak punya `'budget'` (G14 nyata).
Fase ini tidak menghasilkan kode. **Persetujuan formal pemilik produk masih menjadi syarat
sebelum fase 1 dimulai** — itu di luar kendali agent.

² **Fase 0.1 (2026-08-14)** — 4 form manual dipindah ke `LineItemsTable`; `npm run build`
(`tsc -b && vite build`) dan `npm run lint` hijau 0 error. **Regresi visual manual ke-17 form
existing belum dijalankan** — lihat catatan di `phase-0.1-reusable-line-items-component.md`
§Hasil implementasi.

³ **Fase 1 & 2 (2026-08-14)** — dikerjakan sekaligus karena fase 2 tidak bisa diuji tanpa
skema fase 1. Skema baru (4 migration tenant), `BudgetDirection`/`BudgetState`, dan mesin
`BudgetAnalysisService` + `BudgetActualService` + `BudgetMatchResolver` +
`BudgetAllocationResolver` terpasang; `BudgetComparisonService`, `BudgetConsolidationService`,
dan `BudgetWarningService` kini pemakai mesin itu, bukan punya logika sendiri.
`tests/Feature/Budget` 47 lulus (dari 7), `pint --test` bersih pada seluruh file yang diubah.
Detail + deviasi ada di masing-masing dokumen fase, §Hasil implementasi.
**Catatan lingkup:** G7 & G8 ikut tertutup di sini karena `BudgetWarningService` terpaksa
dipindahkan ke resolver — kolom `budget_lines.period` yang dipakainya sudah tidak ada setelah
fase 1. Fase 3 tinggal G9 + verifikasi.

⁴ **Fase 3–7 (2026-08-14)** — dikerjakan berurutan dalam satu sesi. Ringkas:

| Fase | Yang dikerjakan |
|---|---|
| 3 | Payload peringatan + `state`/`direction`/`matched_scope`; `BudgetWarning` di FE dapat 3 field opsional; G9 diverifikasi (`grep strftime app/Modules/Budget/` → hanya komentar) |
| 4 | `SalesInvoiceService::invoiceRevenueJournalLines()` memakai kunci grouping komposit akun\|dept\|proyek; baris pendapatan **dan** diskon kini membawa dimensi |
| 5 | `BudgetRevisionService` (revise + versions), `ReviseBudgetSubmissionRequest`, 11 konstanta `AuditEvent`, audit di seluruh jalur tulis, 2 route |
| 6 | `BudgetCashService`, `BudgetProjectService`, 3 controller + 2 request, 13 route baru, `budgets.revise`/`budgets.export` + migration central `sync_budget_permissions` (G13), business rules (overlap periode, nominal negatif, proyek nonaktif) |
| 7 | 5 halaman baru, folder `hooks/` + `schemas/` (menutup deviasi `spec-03`), kolom Cost Center di `BudgetLineEditor`, tombol Revisi, `ModuleKey` + `'budget'` (G14), 4 item ribbon, 9 entri katalog laporan |

### Penyimpangan dari rencana — fase 3–7

1. **`AuditLogService` dibuat WAJIB, bukan `?AuditLogService = null`.** Rencana menyuruh
   meniru `JournalEntryService`. Pola itu **tidak pernah terisi container** — diverifikasi
   lewat refleksi: parameter dengan nilai default diisi default-nya, jadi `$this->auditLogService`
   selalu `null` dan audit diam-diam tidak menulis apa pun. Modul Budget memakai pola
   `FixedAssetService`/`PeriodEndService` (wajib, tanpa default) yang terbukti bekerja.
   > ⚠️ **Temuan sampingan yang belum ditindaklanjuti:** karena pola yang sama dipakai
   > `JournalEntryService`, `CashPaymentService`, `CashReceiptService`, dan
   > `BankTransferService`, **audit trail keempat service itu kemungkinan besar tidak pernah
   > menulis satu baris pun.** Di luar cakupan rencana ini — butuh perbaikan tersendiri.

2. **Fase 3 sebagian sudah selesai di fase 2.** `BudgetWarningService` mem-query kolom
   `budget_lines.period` yang dihapus fase 1, jadi ia harus dipindah ke resolver saat itu juga
   — kalau tidak, posting jurnal error. Fase 3 karenanya hanya menambah field payload dan test.

3. **`mode=variance` = `mode=summary`.** Rencana tidak mendefinisikan bedanya. Yang
   diimplementasikan: `detail` menambah array `lines` per baris; `summary` dan `variance`
   menghasilkan baris identik. **Kalau `variance` seharusnya menyaring baris, itu keputusan
   produk yang belum diambil.**

4. **`direction: 'mixed'`.** Tidak ada di rencana. Satu baris agregasi bisa mencampur
   pendapatan dan beban (mis. `group_by=[department]` tanpa filter arah), dan "favorable" tidak
   punya makna tunggal di sana — ditandai apa adanya alih-alih diam-diam memilih satu konvensi.

5. **`BudgetComparisonPage.tsx` TIDAK dipindah ke `DataTable`.** Rencana mencantumkannya di
   §Existing files affected, tapi bukan di acceptance criteria. `DataTable` menuntut `id` per
   baris + state paginasi server-side, sementara baris laporan ini hasil agregasi. Halaman
   analisis baru memakai pola tabel manual yang sama, jadi konversinya churn berisiko tanpa
   manfaat. **Sengaja ditunda, bukan kelupaan.**

6. **`BudgetPeriodDetailPage` tab lokal belum dipindah ke `components/ui/tabs`** — sama
   alasannya: kosmetik, di luar acceptance criteria, dan berisiko merusak halaman yang jalan.

7. **`tests/Unit/Budget/` tidak dibuat.** Rencana menaruh test resolver di `tests/Unit/`.
   Resolver butuh koneksi tenant + data, jadi ia feature test (`BudgetMatchResolverTest`) —
   menaruhnya di `tests/Unit/` akan menyesatkan.

8. **`BudgetDirection` memakai `const` biasa, bukan `const string`** — lihat catatan fase 1.

⁵ **Fase 8 (2026-08-14)** — dokumentasi selesai, **verifikasi manual 12 langkah belum
dijalankan** (butuh backend hidup). Status sengaja `🔄 Berjalan`, mengikuti aturan di
`phase-8-dokumentasi.md` §Risks: jangan tandai selesai sebelum 12 langkah itu dijalankan.

## Urutan pengerjaan

```
1 ──▶ 2 ──▶ 3
│     │
│     └──▶ 6 ──▶ 7 ──▶ 8
├──▶ 5 ────┘      │
                  │
4 ────────────────┘   (independen — boleh dikerjakan kapan saja)
```

Fase 4 (dimensi revenue di Sales Invoice) **tidak bergantung pada fase mana pun** dan boleh
dikerjakan lebih dulu. Hasilnya baru terpakai di fase 6.

Fase 0.1 (satukan form baris-item ke `LineItemsTable`) dikerjakan lebih dulu sebelum fase 7 dan
sebelum P1 di `project-dimension-budgeting-readiness-plan.md` — permintaan eksplisit pemilik
produk agar semua form baris-item rapi konsisten seperti form penerimaan (`GoodsReceiptFormPage.tsx`),
sebelum kolom-kolom baru ditambahkan di atasnya.

## Keputusan pemilik produk — jangan diubah tanpa membaca alasannya

Keempatnya diputuskan setelah audit codebase, bukan diasumsikan.

1. **Department = Cost Center.** `cost_centers` tidak ada di seluruh codebase; `departments`
   sudah menjadi dimensi resmi di `journal_entry_lines`. Ditambah `parent_id` supaya
   hierarkis. **Tidak ada dimensi ke-3 di ledger** — menambahkannya berarti menyentuh
   sales, purchase, cash, inventory, fixed asset, `ReportDimensionFilter`, dan 20 report
   request sekaligus.

2. **Redesign skema sekarang.** `budget_periods` = 0 baris di kedua tenant, jadi tidak ada
   data yang perlu dimigrasi. Menunda berarti merombak sambil membawa data.

3. **Perbaiki grouping revenue di Sales Invoice.** Tanpa itu `project_id` tidak pernah sampai
   ke baris jurnal pendapatan, dan Project Profitability mustahil.

4. **MUST HAVE keempatnya**: Versioning, Cash Budget, Project Profitability, perbaikan 4 cacat.

## Keputusan terbuka — masih butuh pemilik produk

**Scoping "Dept hanya lihat pengajuannya sendiri"** tetap ditunda dari rencana sebelumnya.
Tidak ada kolom apa pun yang menghubungkan user ke departemen. Menambahkan
`company_users.department_id` di DB central berarti satu departemen per user untuk **semua**
perusahaan, yang hampir pasti salah.

> ⚠️ Jangan "sekalian saja" menambahkan kolomnya di tengah fase mana pun. Butuh rancangan
> tersendiri.

## Prinsip

- **Actual selalu dari ledger existing.** Tidak ada input actual manual, tidak ada ledger baru.
- **Kalau sebuah angka bisa dihitung, jangan disimpan.** Profit, margin, variance, utilization
  semuanya turunan.
- **Satu logika, banyak pemakai.** Peringatan over-budget dan laporan perbandingan wajib
  memakai resolver yang sama — perbedaan di antara keduanya adalah akar empat cacat lama.
- **Jangan buat komponen UI baru.** Lihat `reference/04-komponen-reusable.md`.
- **Jangan menambah data uji ke tenant demo tanpa membersihkannya.** `budget_periods` harus
  kembali 0 di kedua tenant setelah verifikasi manual.

## Referensi

- Brief: `instruction.md`
- Rencana sebelumnya (Fase 0–3, selesai): `../README.md`
- Rancangan modul asli: `/workspace/frontend/docs/gap_docs/gap-12-budget-module.md`
- Konvensi backend: `/workspace/Finlite_knowladge/reference/02-backend.md`
- Konvensi frontend: `/workspace/Finlite_knowladge/reference/03-frontend.md`
- Komponen reusable: `/workspace/Finlite_knowladge/reference/04-komponen-reusable.md`
- Permission & guard: `/workspace/Finlite_knowladge/reference/05-role-permission-guard.md`
- Modul backend: `/workspace/laravel_backend/app/Modules/Budget/`
- Modul frontend: `/workspace/frontend/src/modules/budget/`
