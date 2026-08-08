# Komponen Reusable

`src/components/shared/` — **37 file**. Aturan project: *jangan membuat komponen baru
kalau sudah ada*. File ini supaya Anda tahu apa yang sudah ada tanpa memindai folder.

`src/components/ui/` adalah shadcn generated — **dilarang diedit**. Kalau butuh varian,
bungkus di `shared/`.

---

## 1. Kerangka halaman

### `layout/WorkspaceLayout` — kerangka SEMUA halaman daftar

```tsx
<WorkspaceLayout
  title="Chart of Accounts"
  breadcrumb={[{ label: 'Master Data' }, { label: 'COA' }]}
  sidebar={sidebar}                       // FilterSidebar
  action={<Button>Tambah Akun</Button>}   // tombol kanan atas
>
  <DataTable … />
</WorkspaceLayout>
```

Props lain: `hideHeader` (dipakai halaman Laporan — nama halaman sudah terbaca di tab;
jangan digabung dengan `sidebar` karena tombol toggle sidebar ada di header) dan
`toolbar` (baris alat melebar penuh di luar area scroll).

### `layout/FormLayout` — kerangka SEMUA halaman form

Props: `title`, `documentNumber`, `status`, `breadcrumb`, `isSystemGenerated`,
`readOnly` + `readOnlyReason`, dan **dua slot aksi yang saling menggantikan**:
`bottomBar` (bar bawah tetap) atau `headerActions` (tombol di header).

### `layout/FilterSidebar` + `FilterSection`

Sidebar filter dengan penghitung filter aktif dan tombol Reset. `FilterSection`
adalah blok yang bisa dilipat. **Kotak pencarian ditempatkan di sini**, di atas
section pertama — bukan di area konten.

### `layout/FixedBottomBar`

Bar aksi tetap di bawah form. Melaporkan tingginya sendiri lewat CSS variable
`--shell-bottom-bar-actual-h`, sehingga `FormLayout` menyediakan padding scroll persis
— termasuk saat tombol turun ke baris kedua di layar sempit.

### Shell (jarang disentuh langsung)

`layout/AppShell`, `Topbar`, `RibbonPanel`, `PrimaryTabs`, `SecondaryTabs` — lihat
`03-frontend.md` §4.

---

## 2. Tabel

### `table/DataTable` — satu-satunya tabel daftar

```tsx
<DataTable
  data={rows} columns={columns} totalRows={data?.meta.total ?? 0}
  isLoading={isLoading} isFetching={isFetching}
  pagination={{ pageIndex: page - 1, pageSize: perPage }}
  onPaginationChange={(s) => { setPage(s.pageIndex + 1); setPerPage(s.pageSize) }}
  selectedRows={selectedIds} onRowSelect={setSelectedIds} bulkActions={bulkActions}
  onRowClick={(row) => openRecordTab({ label: row.code, path: `/master-data/coa/${row.id}` })}
  emptyTitle="Belum ada akun"
/>
```

`ColumnDef<T>`: `{ id, header, cell({ original, id, isSelected }), size?, meta? }`.
`meta` mendukung `sticky`, `stickyLeft`, `className`, `headerClassName`.

Yang perlu diketahui:
- **Kolom checkbox muncul hanya kalau `onRowSelect` DAN `bulkActions` sama-sama diisi.**
- Checkbox-nya Radix → di DOM berupa `button[role="checkbox"]`, **bukan**
  `input[type=checkbox]`. Penting untuk selector Playwright.
- `onRowClick` dipasang di seluruh `<tr>` — tombol di dalam sel wajib
  `stopPropagation` (kolom `_select` sudah otomatis).
- `TablePagination` sudah termasuk di dalam; jangan menambah paginasi sendiri.

### `table/BulkActionBar`

Muncul hanya saat ada baris terpilih. `BulkAction`:
`{ id?, label, icon?, onClick(selectedIds), permission?, variant? }`.
`permission` dibungkus otomatis dengan `PermissionGuard`.

### `table/TablePagination`

Dipakai `DataTable`. Menampilkan "Menampilkan x–y dari N", pemilih ukuran halaman,
dan navigasi halaman.

---

## 3. Filter

| Komponen | Untuk |
|---|---|
| `filter/ListSearchBar` | kotak cari (punya debounce sendiri), diletakkan di dalam `FilterSidebar` |
| `filter/SingleCheckboxFilter` | pilihan **saling meniadakan** lewat deretan checkbox; `clearValue` menentukan nilai saat opsi aktif dilepas |
| `filter/MultiCheckboxFilter` | pilihan **jamak** (mis. status dokumen) |
| `filter/DateRangeFilterSection` | rentang tanggal `from`/`to` |
| `filter/dateRangeUtils` | utilitas rentang tanggal |

Semuanya menerima `note?` untuk keterangan kecil di bawah judul.

> Filter **harus** dikirim ke server sebagai parameter query, bukan dipakai menyaring
> array hasil di browser. Menyaring di browser hanya mengenai baris halaman yang sedang
> tampil — ini pernah terjadi di 9 halaman sekaligus (`plans/list-filters-frontend/`).
>
> **Mengirimnya belum cukup.** `AppliesListQuery` hanya menangani `search`, `status`,
> `date_from`/`date_to`, dan sort. **Filter khusus modul harus dipasang sendiri oleh
> service-nya** sebelum `applyListQuery()` dipanggil — kalau tidak, parameternya
> diabaikan tanpa error. Persis ini yang terjadi pada filter kategori di daftar produk
> (2026-08-08): frontend mengirim `product_category_id` dengan benar selama berbulan-bulan,
> `ProductService::list()` tidak pernah membacanya. Tanda pengenalnya: parameter terlihat
> di tab Network, tapi `meta.total` tidak bergerak saat filter diubah.

---

## 4. Form

| Komponen | Untuk |
|---|---|
| `form/FormSection` | kartu bersekat, grid 1 atau 2 kolom |
| `form/FieldError` | pesan error satu field |
| `form/SearchableSelect` | dropdown dengan pencarian async; mendukung single & `multiple` |
| `form/LineItemsTable` | tabel baris transaksi (tambah/hapus/ubah, subtotal, error per baris) |
| `form/FormSummary` | ringkasan nilai: subtotal, diskon, DPP, pajak, grand total, dibayar, sisa |
| `form/RecordNavButtons` | Prev/Next antar record — **keduanya menyimpan dulu** |
| `layout/FormSaveActions` | pasangan Batal / Simpan & Tutup; `children` untuk tombol ekstra (mis. Aktifkan/Nonaktifkan) |

`SearchableSelect` menerima `onSearch: (q) => Promise<SelectOption[]>` — sambungkan ke
endpoint `search` modul terkait, jangan memuat seluruh daftar ke memori.

`LineItemsTable.errors` menerima error per baris dari backend (`getApiLineErrors` di
`lib/apiError.ts`) dan menandai baris yang bermasalah.

---

## 5. Dokumen & status

| Komponen | Untuk |
|---|---|
| `document/DocumentStatusBadge` | badge status dokumen (`draft`…`void`), ukuran `xs`/`sm`/`md` |
| `badge/ActiveStatusBadge` | badge Aktif/Nonaktif untuk master data — **selalu pakai ini**, jangan styling sendiri |
| `document/DocumentActionBar` | tombol lifecycle; `placement: 'bottom' | 'header'` |
| `document/ConfirmDialog` | konfirmasi umum, varian `primary`/`destructive` |
| `document/VoidConfirmDialog` | konfirmasi void — **mewajibkan alasan minimal 10 karakter** |
| `document/DocumentLockedBanner` | menjelaskan dokumen hilir yang mengunci dokumen ini |
| `document/SystemGeneratedBadge` | menandai dokumen buatan sistem |
| `document/documentEditPolicy` | menurunkan alasan read-only dari status |

---

## 6. Umpan balik & penjaga

| Komponen | Untuk |
|---|---|
| `feedback/EmptyState` | keadaan kosong (dipakai `DataTable`, bisa berdiri sendiri) |
| `feedback/ErrorBoundary` | menangkap error render |
| `feedback/SessionWarningDialog` | hitung mundur sesi habis |
| `feedback/UnsavedFormsDialog` | menahan Tutup Database / Keluar saat ada form belum tersimpan |
| `PermissionGuard` | menyembunyikan elemen tanpa hak akses — lihat `05-role-permission-guard.md` |

---

## 7. Pola halaman daftar standar

Acuan yang sudah diseragamkan: **`src/modules/master-data/pages/KontakListPage.tsx`**.
Ikuti ini saat membuat halaman daftar baru.

```tsx
const [page, setPage] = useState(1)
const [perPage, setPerPage] = useState<25 | 50 | 100>(25)
const [search, setSearch] = useState('')
const [filterActive, setFilterActive] = useState<boolean | undefined>(true)
const [selectedIds, setSelectedIds] = useState<string[]>([])

const { data, isLoading, isFetching } = useXList({ page, per_page: perPage, search: search || undefined, … })

// kembali ke halaman 1 + kosongkan seleksi saat filter berubah
const [prevFilters, setPrevFilters] = useState('')
const filterKey = `${search}|${String(filterActive)}`
if (filterKey !== prevFilters) { setPrevFilters(filterKey); setPage(1); setSelectedIds([]) }
```

Empat hal yang tidak boleh terlewat:

1. **Reset ke halaman 1** saat filter berubah — kalau tidak, user mendarat di halaman
   kosong setelah hasil menyusut.
2. **Kosongkan seleksi** saat pindah halaman atau ganti filter — aksi massal tidak boleh
   mengenai baris yang sudah tidak terlihat.
3. **`totalRows` dari `data?.meta.total`** — bukan `rows.length`.
4. **Aksi massal Aktifkan/Nonaktifkan** memakai `Promise.allSettled`, bukan loop
   `await` berurutan, supaya satu kegagalan (mis. akun induk yang masih punya anak
   aktif) tidak menghentikan sisanya tanpa kabar.

## 8. Pola halaman form standar

Acuan: **`src/modules/master-data/pages/KontakFormPage.tsx`**.

- `key` di wrapper default export supaya form di-remount saat id record berubah
- `usePersistentFormDraft` untuk menyimpan isian yang belum tersimpan
- `useRecordFormNavigation` untuk simpan-dan-tutup + Prev/Next
- `FormLayout.headerActions` berisi `ActiveStatusBadge` + `FormSaveActions`, dengan
  `RecordNavButtons` dan tombol Aktifkan/Nonaktifkan sebagai `children`
- Batal memanggil `formDraft.clearDraft()` lalu `closeRecordTab(...)`
- Error backend disalurkan ke field lewat `applyApiValidationErrors(error, setError)`
  **dan** ditampilkan sebagai toast — jangan menggantinya dengan teks generik
