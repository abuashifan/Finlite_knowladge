# Fase 14 — Modal Parameter Laporan (Filter Data + Column Selection)

**Prioritas:** B (UX improvement menyeluruh — semua laporan existing terpengaruh)
**Estimasi:** sedang — 1 komponen baru, update semua halaman laporan, tanpa backend baru.

## Tujuan

Mengganti `ReportFilterParameter` yang saat ini adalah form inline statis dengan sebuah
**floating modal/dialog** yang lebih lengkap dan konsisten. Modal ini menambah dua kapabilitas
yang belum ada:

1. **Filter Data kontekstual** — selain tanggal & dimensi existing (dept/project/warehouse),
   tiap laporan bisa mendeklarasikan filter tambahan yang relevan (pelanggan, produk, status,
   jenis akun, dll). Filter ini dikirim ke backend sebagai query param (backend-side filtering).
2. **Column Selection** — user bisa memilih kolom mana yang ditampilkan di tabel laporan.
   State di session (reset saat refresh); tidak perlu backend/localStorage.

Komponen `ReportFilterParameter` **dihapus** dan digantikan sepenuhnya oleh
`ReportParameterModal`. Komponen `ReportCompactBar` tetap ada dan menjadi satu-satunya trigger
pembuka modal. Semua halaman laporan existing diupdate ke pola baru.

## Prasyarat

- Fase 0 ✅ (katalog bersih).
- `npm run build` 0 error di titik mulai.
- Baca `00-conventions.md` §1–5 (pola page, adapter, permission).
- Verifikasi komponen yang ada:
  - `react_frontend/src/modules/reports/components/ReportFilterParameter.tsx` — akan dihapus.
  - `react_frontend/src/modules/reports/components/ReportCompactBar.tsx` — akan diedit.
  - `react_frontend/src/components/ui/dialog.tsx` — sudah ada (Radix Dialog).
  - `react_frontend/src/components/shared/form/SearchableSelect.tsx` — sudah ada.

## Latar Belakang & Keputusan Desain

| Keputusan | Pilihan | Alasan |
|---|---|---|
| Filter lokasi | **Backend** (query param) | Data laporan bisa besar; frontend-only filter buang memori & memperlambat load |
| Column persistence | **Session state** | Cukup untuk kebutuhan ini; localStorage menambah kompleksitas tanpa manfaat nyata |
| Trigger modal | `ReportCompactBar` (tombol "Ubah Filter") | Konsisten dengan pola existing; tidak perlu tombol tambahan di header |
| Komponen modal | Radix `Dialog` (sudah ada di `ui/dialog.tsx`) | Tidak buat komponen baru bila sudah ada |
| Layout modal | 3 section vertikal (bukan tab) | Tab menambah interaksi; section collapsible lebih natural untuk form parameter |

## Arsitektur Komponen Baru

```
ReportParameterModal          ← komponen baru (menggantikan ReportFilterParameter)
  props:
    open: boolean
    onClose: () => void
    params: ReportParams
    onChange: (p: Partial<ReportParams>) => void
    onSubmit: () => void
    mode?: 'range' | 'as_of_date'
    isLoading?: boolean
    dimensions?: DimensionFilterConfig          ← sama seperti sekarang
    extras?: ExtraFilterConfig                  ← sama seperti sekarang
    contextFilters?: ContextFilterConfig        ← BARU
    columns?: ColumnConfig[]                    ← BARU
    visibleColumns: string[]                    ← BARU (dikelola di page)
    onColumnsChange: (cols: string[]) => void   ← BARU

ContextFilterConfig:          ← interface baru di ReportFilterParameter.tsx (atau file sendiri)
  customer?: boolean          ← SearchableSelect ke /contacts?type=customer
  supplier?: boolean          ← SearchableSelect ke /contacts?type=supplier
  product?: boolean           ← SearchableSelect ke /products
  account?: boolean           ← SearchableSelect ke /chart-of-accounts
  contact?: boolean           ← SearchableSelect ke /contacts (umum)
  status?: StatusFilterConfig ← dropdown pilihan status

StatusFilterConfig:
  options: { label: string; value: string }[]

ColumnConfig:
  key: string                 ← kunci unik kolom (dipakai di visibleColumns)
  label: string               ← label header yang tampil di tabel
  defaultVisible?: boolean    ← default true bila tidak disebutkan
```

`ReportCompactBar` diupdate untuk:
- Menerima prop `onOpenModal: () => void` (menggantikan `onEdit`)
- Menampilkan ringkasan filter aktif selain tanggal (misal: "Pelanggan: PT ABC · 4 kolom")

## ReportParams — Penambahan Field

Di `reports.types.ts`, tambah field opsional baru ke `ReportParams`:

```ts
export interface ReportParams extends DateRangeParams {
  // ... existing fields ...
  customer_id?: number      // filter pelanggan
  supplier_id?: number      // filter pemasok
  product_id?: number       // filter produk
  contact_id?: number       // filter kontak umum
  account_id?: number       // sudah ada
  status?: string           // filter status dokumen
}
```

Field baru ini hanya dikirim ke backend jika halaman laporan yang bersangkutan mendukungnya
(diatur via `contextFilters` prop). Backend yang belum mendukung param ini mengabaikannya
(tidak merusak laporan existing).

## Layout Modal (3 Section)

```
┌─────────────────────────────────────────────────┐
│  Parameter Laporan                           [X] │
├─────────────────────────────────────────────────┤
│  ▼ PERIODE                                       │
│  Dari Tanggal [______]   Sampai [______]         │
│                                                  │
│  ▼ FILTER DATA                                   │
│  Departemen   [Semua departemen        ▾]        │
│  Proyek       [Semua proyek            ▾]        │
│  Pelanggan    [Semua pelanggan         ▾]  ← baru│
│  Produk       [Semua produk            ▾]  ← baru│
│  Status       [Semua status            ▾]  ← baru│
│  ☐ Tampilkan akun saldo nol                      │
│                                                  │
│  ▼ KOLOM YANG DITAMPILKAN                        │
│  ☑ Kode Akun  ☑ Nama Akun  ☑ Saldo Awal         │
│  ☑ Debit      ☑ Kredit     ☐ Catatan             │
├─────────────────────────────────────────────────┤
│                      [Batal]  [Tampilkan]        │
└─────────────────────────────────────────────────┘
```

- Section "Filter Data" hanya muncul bila ada minimal 1 `contextFilter` atau `dimension` atau
  `extra` yang aktif.
- Section "Kolom" hanya muncul bila `columns` prop diberikan dan non-empty.
- Modal lebar `max-w-lg`, tinggi auto (tidak fixed-height), scroll internal bila konten panjang.

## Daftar Tugas

### T14.1 — Tambah field baru ke `ReportParams`

- [ ] Buka `react_frontend/src/modules/reports/types/reports.types.ts`.
- [ ] Tambah `customer_id`, `supplier_id`, `product_id`, `contact_id`, `status` ke
  `ReportParams` (semua opsional).
- [ ] Tambah interface `ContextFilterConfig` dan `ColumnConfig` di file yang sama atau di
  file types tersendiri yang di-import oleh komponen baru. Letakkan berdekatan dengan
  `DimensionFilterConfig` yang existing.

### T14.2 — Buat `ReportParameterModal`

- [ ] Buat `react_frontend/src/modules/reports/components/ReportParameterModal.tsx`.
- [ ] Gunakan `Dialog`, `DialogContent`, `DialogHeader`, `DialogTitle`, `DialogFooter`
  dari `@/components/ui/dialog`.
- [ ] Section **Periode**: sama persis dengan `ReportFilterParameter` existing (range / as_of_date).
- [ ] Section **Filter Data**: render `DimensionFilterConfig` + `ContextFilterConfig` + `ExtraFilterConfig`.
  - `customer_id` → `SearchableSelect` search ke `pelangganApi` / `kontakApi` dengan filter type customer.
  - `supplier_id` → `SearchableSelect` ke kontak type supplier.
  - `product_id` → `SearchableSelect` ke `produkApi`.
  - `contact_id` → `SearchableSelect` ke kontak umum.
  - `status` → `<select>` native atau Shadcn `Select` dengan options dari `StatusFilterConfig`.
  - `dimensions` (dept/project/warehouse) → `SearchableSelect` seperti sekarang.
  - `extras` (checkbox) → di bawah dimension fields.
  - Section ini hanya render bila ada minimal 1 field aktif.
- [ ] Section **Kolom**: render checklist `ColumnConfig[]`; state dikelola di luar (page) via
  `visibleColumns` + `onColumnsChange`.
  - Semua kolom di-check default (`defaultVisible !== false`).
  - Minimal 1 kolom harus selalu checked (disabled unchecking kolom terakhir).
  - Section ini hanya render bila `columns` prop non-empty.
- [ ] Tombol "Batal" menutup modal tanpa apply (`onClose`). Tombol "Tampilkan" memanggil
  `onSubmit` lalu `onClose`.
- [ ] Semua angka lewat `tabular-nums`; styling konsisten dengan design token existing
  (`#64748b`, `#334155`, dll, lihat `ReportFilterParameter` sebagai referensi warna).

### T14.3 — Update `ReportCompactBar`

- [ ] Rename prop `onEdit` → `onOpenModal` (breaking change kecil; update semua caller).
- [ ] Tambah prop opsional `filterSummary?: string` — string ringkasan filter aktif selain
  tanggal (mis. `"Pelanggan: PT ABC"`). Bila diisi, tampilkan di sebelah kanan tanggal.
- [ ] Tambah prop opsional `columnSummary?: string` — mis. `"5 kolom"`. Tampilkan bila diisi.
- [ ] Contoh bar setelah update:
  ```
  [≡] Jan 2026 — Jun 2026 · Pelanggan: PT ABC · 5 kolom   [Ubah Filter]
  ```

### T14.4 — Hapus `ReportFilterParameter`

- [ ] Hapus file `react_frontend/src/modules/reports/components/ReportFilterParameter.tsx`.
- [ ] Hapus semua import `ReportFilterParameter` di seluruh codebase (akan error build bila
  ada yang tertinggal — `npm run build` akan catch).

### T14.5 — Update semua halaman laporan

Untuk setiap halaman di bawah, lakukan pola yang sama:

**Pola baru per page:**
```tsx
// Tambah state
const [modalOpen, setModalOpen] = useState(true)  // buka otomatis saat pertama load
const [visibleColumns, setVisibleColumns] = useState<string[]>(
  COLUMNS.filter(c => c.defaultVisible !== false).map(c => c.key)
)

// Definisikan kolom laporan (konstanta di atas komponen)
const COLUMNS: ColumnConfig[] = [
  { key: 'account_code', label: 'Kode' },
  { key: 'account_name', label: 'Akun' },
  // ...
]

// Render
<ReportCompactBar
  params={activeParams!}
  onOpenModal={() => setModalOpen(true)}
  filterSummary={buildFilterSummary(activeParams)}   // helper lokal atau shared
  columnSummary={`${visibleColumns.length} kolom`}
/>
<ReportParameterModal
  open={modalOpen}
  onClose={() => setModalOpen(false)}
  params={params}
  onChange={(p) => setParams(prev => ({ ...prev, ...p }))}
  onSubmit={handleSubmit}
  columns={COLUMNS}
  visibleColumns={visibleColumns}
  onColumnsChange={setVisibleColumns}
  // dimensions / contextFilters / extras sesuai laporan
/>
// Tabel: sembunyikan kolom bila !visibleColumns.includes(col.key)
```

Halaman yang perlu diupdate:

| Halaman | dimensions | contextFilters | columns |
|---|---|---|---|
| `GeneralLedgerPage` | dept, project | — | kode, nama, saldo awal, debit, kredit, saldo akhir |
| `TrialBalancePage` | dept | — | kode, nama, saldo awal debit, saldo awal kredit, mutasi debit, mutasi kredit, saldo akhir debit, saldo akhir kredit |
| `AccountLedgerPage` | dept, project | account | tanggal, no. jurnal, keterangan, debit, kredit, saldo |
| `ProfitLossPage` | dept, project | — | kode, nama, jumlah |
| `BalanceSheetPage` | — | — | kode, nama, jumlah |
| `CashFlowPage` | — | — | keterangan, jumlah |
| `FinancialSummaryPage` | — | — | (tidak ada tabel kolom; skip columns) |
| `ReconciliationPage` | warehouse | — | (tab-based; columns per tab opsional — defer bila terlalu kompleks) |
| `ArAgingReportPage` | dept, project | customer | pelanggan, 1-30, 31-60, 61-90, >90, total |
| `ApAgingReportPage` | dept, project | supplier | pemasok, 1-30, 31-60, 61-90, >90, total |
| `CashBankStatementPage` | — | account | tanggal, keterangan, referensi, debit, kredit, saldo |
| `StockReportPage` | warehouse | product | (lihat kolom existing di halaman) |
| `InventoryAnalysisPage` | warehouse | product | (lihat kolom existing) |
| `FixedAsset*Page` (4 halaman) | — | — | (lihat kolom existing masing-masing) |

> Catatan: halaman laporan yang ditambah di Fase 1–13 **juga perlu diupdate** saat fase
> tersebut diimplementasikan. File fase tersebut harus menyebut "gunakan `ReportParameterModal`"
> (bukan `ReportFilterParameter` yang sudah tidak ada). Setelah Fase 14 selesai, `00-conventions.md`
> diupdate untuk mengganti referensi `ReportFilterParameter` → `ReportParameterModal`.

### T14.6 — Update `00-conventions.md`

- [ ] Ganti semua referensi `ReportFilterParameter` → `ReportParameterModal` di `00-conventions.md`.
- [ ] Tambah penjelasan singkat `ContextFilterConfig` dan `ColumnConfig` di §1 (checklist anatomi
  laporan) dan §3 (pola halaman laporan).
- [ ] Update contoh pola page di §3 untuk mencerminkan pola modal baru.

### T14.7 — Update `docs/struktur_frontend.md`

- [ ] Tambah `ReportParameterModal.tsx` ke daftar komponen reports.
- [ ] Hapus entri `ReportFilterParameter.tsx`.

## Peta File

**✏️ Ubah**
- `react_frontend/src/modules/reports/types/reports.types.ts` — tambah `customer_id`, `supplier_id`, `product_id`, `contact_id`, `status` ke `ReportParams`; tambah `ContextFilterConfig`, `ColumnConfig`.
- `react_frontend/src/modules/reports/components/ReportCompactBar.tsx` — rename `onEdit` → `onOpenModal`, tambah `filterSummary` + `columnSummary`.
- `react_frontend/src/modules/reports/pages/GeneralLedgerPage.tsx` — pola baru.
- `react_frontend/src/modules/reports/pages/TrialBalancePage.tsx` — pola baru.
- `react_frontend/src/modules/reports/pages/AccountLedgerPage.tsx` — pola baru.
- `react_frontend/src/modules/reports/pages/ProfitLossPage.tsx` — pola baru.
- `react_frontend/src/modules/reports/pages/BalanceSheetPage.tsx` — pola baru.
- `react_frontend/src/modules/reports/pages/CashFlowPage.tsx` — pola baru.
- `react_frontend/src/modules/reports/pages/FinancialSummaryPage.tsx` — pola baru (tanpa columns).
- `react_frontend/src/modules/reports/pages/ReconciliationPage.tsx` — pola baru (columns opsional, defer bila terlalu kompleks).
- `react_frontend/src/modules/reports/pages/ArAgingReportPage.tsx` — pola baru + contextFilters customer.
- `react_frontend/src/modules/reports/pages/ApAgingReportPage.tsx` — pola baru + contextFilters supplier.
- `react_frontend/src/modules/reports/pages/CashBankStatementPage.tsx` — pola baru + contextFilters account.
- `react_frontend/src/modules/reports/pages/StockReportPage.tsx` — pola baru + contextFilters product + warehouse.
- `react_frontend/src/modules/reports/pages/InventoryAnalysisPage.tsx` — pola baru + contextFilters product.
- `react_frontend/src/modules/reports/pages/FixedAssetRegisterReportPage.tsx` — pola baru.
- `react_frontend/src/modules/reports/pages/FixedAssetDepreciationReportPage.tsx` — pola baru.
- `react_frontend/src/modules/reports/pages/FixedAssetDisposalsReportPage.tsx` — pola baru.
- `react_frontend/src/modules/reports/pages/FixedAssetReconciliationReportPage.tsx` — pola baru.
- `react_frontend/docs/struktur_frontend.md` — tambah `ReportParameterModal`, hapus `ReportFilterParameter`.
- `Finlite_Knowladge/plans/reports-expansion/00-conventions.md` — update referensi komponen.

**➕ Tambah**
- `react_frontend/src/modules/reports/components/ReportParameterModal.tsx` — komponen modal baru.

**🗑️ Hapus**
- `react_frontend/src/modules/reports/components/ReportFilterParameter.tsx` — digantikan `ReportParameterModal`.

## Checklist Verifikasi

- [ ] `npm run build` 0 error — tidak ada import `ReportFilterParameter` tersisa.
- [ ] `npm run lint` 0 error.
- [ ] Modal terbuka saat klik "Ubah Filter" di `ReportCompactBar`.
- [ ] Modal terbuka otomatis saat pertama kali masuk halaman laporan (sebelum ada `activeParams`).
- [ ] Tombol "Batal" menutup modal tanpa memuat data.
- [ ] Tombol "Tampilkan" menutup modal + trigger query + tampil `ReportCompactBar`.
- [ ] Section "Filter Data" tidak muncul bila tidak ada filter yang dikonfigurasi.
- [ ] Section "Kolom" tidak muncul bila `columns` tidak diberikan.
- [ ] Column selection: unchecking semua kolom kecuali 1 → kolom terakhir tidak bisa di-uncheck.
- [ ] Filter pelanggan (ArAgingReportPage): pilih pelanggan → param `customer_id` terkirim ke API.
- [ ] Filter pemasok (ApAgingReportPage): pilih pemasok → param `supplier_id` terkirim ke API.
- [ ] `ReportCompactBar` menampilkan ringkasan filter aktif (nama pelanggan/pemasok dll).
- [ ] Runtime smoke: buka General Ledger → modal terbuka → isi tanggal → klik Tampilkan → data muncul.
- [ ] Viewport 768px (iPad mini): modal tidak overflow, scroll internal bekerja.

## Catatan untuk Fase Berikutnya (1–13)

Setelah Fase 14 selesai, semua fase laporan baru (Fase 1–13 yang belum dikerjakan) harus:
- Gunakan `ReportParameterModal` (bukan `ReportFilterParameter`).
- Definisikan `COLUMNS: ColumnConfig[]` di atas komponen page.
- Sertakan `contextFilters` yang relevan (lihat tabel T14.5 sebagai panduan).
- `00-conventions.md` sudah diupdate dengan pola baru setelah T14.6.

## Git Checkpoint

- Branch frontend: `feat/reports-parameter-modal` (branch baru dari base branch aktif).
- Satu commit: `feat(reports): replace filter panel with floating modal + column selection`.
- Update ledger `README.md` Fase 14 → ✅ + commit hash, commit di repo `Finlite_Knowladge`.
- Update `00-conventions.md` di commit yang sama (atau commit terpisah kecil `docs(reports): update conventions for ReportParameterModal`).
