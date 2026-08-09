# Fase 3 — Samakan ke pola shell standar

**Tujuan:** membuat halaman anggaran berperilaku seperti 21 halaman daftar lain,
supaya tidak ada pola kedua yang harus dirawat terpisah.

Fase ini murni penyeragaman — setelah Fase 0–2 modulnya sudah berfungsi. Kalau
waktu terbatas, fase inilah yang boleh ditunda, **bukan** yang lain.

## Masalah

Modul budget dibuat sebelum pola shell diseragamkan, jadi ia menyimpang di tiga
hal sekaligus:

| Menyimpang | Akibat nyata |
|---|---|
| `navigate()` langsung, bukan `useRecordTab` | tidak membuat tab; tab bar tidak sinkron, dan halaman hilang begitu user berpindah tab (`AppShell` menyetir router dari state tab) |
| `<table>` manual di 3 tempat | tanpa paginasi, tanpa seleksi baris, tanpa keadaan kosong yang seragam |
| `WorkspaceLayout` tanpa `sidebar` | filter ditaruh di area konten, bukan di `FilterSidebar` seperti halaman lain |

## Perubahan

### `BudgetPeriodListPage.tsx` → pola `KontakListPage`

Acuannya `src/modules/master-data/pages/KontakListPage.tsx`
(lihat `reference/04-komponen-reusable.md` §7).

- Buang `<table>` manual → `DataTable` dengan `ColumnDef<BudgetPeriod>[]`.
- `onRowClick` → `openRecordTab({ label: p.name, path: `/budget/periods/${p.id}` })`,
  ganti tombol "Lihat" dan `navigate()`.
- Tombol "Buat Periode" → `openRecordTab` ke `/budget/periods/new`,
  bukan `navigate`.
- `FilterSidebar` berisi `ListSearchBar` + filter status (Aktif/Ditutup/Semua)
  memakai `SingleCheckboxFilter`.
- Pola `filterKey`: reset `page` ke 1 **dan** kosongkan seleksi tiap filter
  berubah.

> ⚠️ **Backend `/budget-periods` belum mendukung paginasi maupun search.**
> `BudgetPeriodService::list()` mengembalikan `Collection`, bukan paginator, dan
> tidak memakai `AppliesListQuery`. Dua pilihan, ambil satu **dengan sadar**:
>
> - **(a) Frontend saja** — `DataTable` tanpa `pagination`, `totalRows` =
>   `rows.length`. Jujur untuk puluhan baris; satu periode per tahun fiskal, jadi
>   pertumbuhannya sangat lambat. **Ini yang disarankan.**
> - **(b) Ikut pushdown** — pasang `AppliesListQuery` di `BudgetPeriodService`
>   seperti service master data. Rapi, tapi menyentuh backend di luar cacat E
>   dan melanggar prinsip rencana ini.
>
> Jangan memasang UI paginasi yang tidak didukung server — itu persis kesalahan
> yang diperbaiki `plans/list-query-pushdown/`.

### `BudgetPeriodDetailPage.tsx`

- Tabel pengajuan → `DataTable`, `onRowClick` → `openRecordTab` ke
  `/budget/submissions/{id}`.
- Tombol "Detail" per baris dibuang (baris sudah bisa diklik). Kalau ada tombol
  lain yang bertahan di dalam sel, bungkus `stopPropagation` — `DataTable`
  memasang `onRowClick` di seluruh `<tr>`.
- Tab Pengajuan/Konsolidasi buatan sendiri boleh dipertahankan; itu tab **di
  dalam halaman**, bukan tab shell, dan tidak ada komponen bersama untuk itu.

### `BudgetPeriodFormPage.tsx`

- Bungkus dengan `FormLayout`, aksi lewat `FormSaveActions` — bukan tombol lepas.
- Batal → `closeRecordTab(...)`, bukan `navigate('/budget')`.
- Sudah benar dan **jangan diubah**: halaman ini memanggil
  `useUnsavedFormTracker({ control })` sendiri (baris 45) karena tidak memakai
  `usePersistentFormDraft`. Tanpa itu, isian hilang tanpa peringatan saat user
  menutup database.

### `BudgetLineEditor.tsx`

Pertimbangkan `LineItemsTable` dari `components/shared/form/`, tapi **periksa
dulu apakah bentuknya cocok** — komponen itu dirancang untuk baris transaksi
dengan subtotal, sementara baris anggaran punya kolom `period` (YYYY-MM) yang
tidak ada padanannya. **Kalau tidak pas, biarkan tabel manualnya** dan catat
alasannya di komentar; memaksakan komponen bersama yang tidak cocok lebih buruk
daripada tabel khusus yang jujur.

Yang tetap wajib diperbaiki di komponen ini, terlepas dari keputusan di atas:

- `Input type="number"` untuk nominal → samakan dengan format angka halaman lain
  (`tabular-nums` sudah ada; periksa pemformatan ribuan).
- Field `period` teks bebas "2026-01" tanpa validasi. Backend menerima apa saja
  dan `BudgetWarningService` mencocokkannya dengan
  `strftime('%Y-%m', journal_date)` — salah ketik berarti peringatan over-budget
  diam-diam tidak pernah menyala. Validasi pola `^\d{4}-\d{2}$` di klien.

### `BudgetComparisonPage.tsx`

Halaman laporan, jadi acuannya halaman Laporan lain (`hideHeader`, `toolbar`),
bukan halaman daftar. Perubahan paling kecil: pindahkan panel filter ke
`toolbar` supaya sebaris dengan laporan lain.

## Verifikasi

```bash
rtk npm run build
rtk lint
```

Manual:

1. Buka periode dari daftar → **tab record baru muncul di tab sekunder**,
   bukan sekadar berganti isi.
2. Pindah ke tab primer lain lalu kembali → **halaman anggaran masih di tempat
   yang sama.** Inilah yang gagal sebelum fase ini.
3. Tutup tab form yang isiannya belum disimpan → muncul peringatan.
4. Tutup Database saat form anggaran masih kotor → dialog form belum tersimpan
   menyebut halaman itu.
5. Klik baris di tabel pengajuan membuka tab; tombol di dalam sel (kalau masih
   ada) tidak ikut membuka tab.

## Yang TIDAK dikerjakan

- Tidak membuat komponen bersama baru.
- Tidak mengubah `DataTable`/`FormLayout`/`FilterSidebar`.
- Tidak menyentuh backend (kecuali bila (b) dipilih di atas — dan itu harus
  dicatat sebagai penyimpangan dari prinsip rencana, bukan diam-diam).
