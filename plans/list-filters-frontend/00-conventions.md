# Konvensi — List Filters Frontend

> Wajib dibaca sebelum mengerjakan fase mana pun.

## 1. Bentuk akhir yang dituju

**Sebelum** (kelompok C — menyaring di browser):

```tsx
const FILTER_HINT = 'Filter multi-select dan tanggal berlaku pada data halaman yang sedang dimuat.'

const { data, isLoading } = useSalesInvoiceList({
  page: page + 1,
  per_page: 25,
  search: search || undefined,
  customer_id: filterCustomer ?? undefined,
})

const rows = data?.data ?? []
const visibleRows = rows.filter((invoice) => {
  const matchesStatus = filterStatuses.length === 0 || filterStatuses.includes(invoice.status)
  const matchesDate = isDateInRange(invoice.invoice_date, dateRange.from, dateRange.to)
  return matchesStatus && matchesDate
})

// ...
<DataTable data={visibleRows} totalRows={data?.meta.total ?? 0} />
```

**Sesudah** (semua ke server):

```tsx
const { data, isLoading } = useSalesInvoiceList({
  page: page + 1,
  per_page: 25,
  search: search || undefined,
  customer_id: filterCustomer ?? undefined,
  status: filterStatuses.length > 0 ? filterStatuses.join(',') : undefined,
  date_from: dateRange.from || undefined,
  date_to: dateRange.to || undefined,
})

const rows = data?.data ?? []

// ...
<DataTable data={rows} totalRows={data?.meta.total ?? 0} />
```

Yang hilang: `FILTER_HINT`, `visibleRows`, dan helper `isDateInRange` bila tidak
dipakai lagi di file itu.

> ⚠️ **`totalRows` tetap dari `data.meta.total`.** Jangan diganti
> `visibleRows.length` "supaya cocok" — justru ketidakcocokan itulah bug yang
> sedang diperbaiki. Setelah server yang memfilter, `meta.total` sudah benar.

## 2. Status multi-pilih dikirim comma-separated

UI-nya multi-select (`filterStatuses: string[]`), backend menerima
`?status=draft,posted` dan memecahnya jadi `whereIn`. Jadi:

```ts
status: filterStatuses.length > 0 ? filterStatuses.join(',') : undefined
```

`undefined` saat kosong, **bukan** `''` — string kosong tetap terkirim sebagai
parameter dan membuat cache key TanStack Query berbeda tanpa alasan.

⚠️ Tipe `status` saat ini enum tunggal (`status?: SalesInvoiceStatus`), jadi
`join(',')` tidak lolos type check. Halaman Persediaan menyiasatinya dengan
`as StockMovementStatus` — **jangan ditiru**, itu berbohong ke type checker dan
melanggar aturan `any`/cast tanpa justifikasi di `AGENTS.md`. Perbaikan tipenya
ada di Fase 0.

## 3. Reset halaman saat filter berubah

Kalau pengguna sedang di halaman 5 lalu memfilter sampai hasilnya tinggal 2
halaman, ia akan melihat daftar kosong dan mengira filternya rusak.

Halaman yang ada sudah punya pola ini untuk `search` — ikuti persis, jangan
buat mekanisme baru:

```tsx
if (search !== prevSearch) {
  setPrevSearch(search)
  setPage(0)
}
```

Terapkan hal yang sama untuk perubahan status dan rentang tanggal. Pola
"adjust state on prop change saat render" ini dipilih supaya tidak memicu
cascading render dari `useEffect` — jangan diubah jadi effect.

## 4. Nama parameter tanggal

Backend menerima **dua** pasangan nama (lihat `AppliesListQuery::applyListQuery()`):

- `date_from` / `date_to`
- `start_date` / `end_date`

**Pakai `date_from`/`date_to`.** Itu yang sudah dipakai kelompok A dan yang
tertulis di semua tipe params. Jangan mencampur keduanya.

Kolom tanggal yang difilter adalah **tanggal dokumen** (`invoice_date`,
`bill_date`, `receipt_date`, …), bukan `created_at` — sudah ditetapkan per
modul di `$listDateColumn` dan disetujui pemilik produk saat merancang
`list-query-pushdown` (§4 conventions rencana itu).

## 5. Yang TIDAK boleh dilakukan

- ❌ Mengubah backend. Rencana ini murni frontend. Kalau terasa butuh perubahan
  backend, berhenti dan catat — ada asumsi yang salah.
- ❌ Menghapus `FILTER_HINT` sebelum halaman itu benar-benar diperbaiki.
- ❌ Mengganti `totalRows` jadi panjang array hasil filter.
- ❌ Memakai `as SomeStatus` untuk memaksa `join(',')` lolos type check.
- ❌ Menyentuh 5 halaman kelompok A "sekalian dirapikan".
- ❌ Menambah filter baru yang belum diminta (mis. filter jatuh tempo) —
  lihat §6.

## 6. `due_from` / `due_to` — tipe yang berbohong

`SalesInvoiceListParams` mendeklarasikan `due_from` dan `due_to`. **Backend
tidak pernah menerimanya** — `grep -rn "due_from" app/` nihil di seluruh
backend (diverifikasi 2026-08-06 saat Fase 2 `list-query-pushdown`).

Jadi dua field itu janji kosong. Pilihannya:

- **hapus dari tipe** (rekomendasi — tidak ada yang memakainya), atau
- implementasikan di backend, yang berarti keluar dari cakupan rencana ini.

Diputuskan di Fase 0. Jangan diam-diam dipakai.

## 7. Definition of Done per fase

- [ ] Halaman mengirim `status`/`date_from`/`date_to` ke server
- [ ] Tidak ada `visibleRows` atau `.filter()` sisa di halaman itu
- [ ] `FILTER_HINT` dihapus dari halaman yang sudah diperbaiki
- [ ] `totalRows` tetap dari `data.meta.total`
- [ ] Halaman kembali ke 1 saat filter berubah
- [ ] `npx tsc --noEmit` bersih — **tanpa** menambah `as` atau `any`
- [ ] `npm run build` hijau
- [ ] Backend **tidak diubah**; `php artisan test` tetap hijau
- [ ] Diuji di browser dengan data > 25 baris: filter menjangkau halaman ≥ 2
      dan `total` ikut menyusut (lihat README §Cara membuktikan)
- [ ] Ledger `README.md` diperbarui + commit

## 8. Catatan lingkungan

- `npm run build` wajib hijau sebelum selesai (aturan `frontend/CLAUDE.md`).
  `rtk tsc` saja tidak cukup — pakai `npm run build` untuk konfirmasi.
- Uji browser: dev server frontend di `5173`, backend `php artisan serve` di
  `8000`. Login `admin@example.com` / `password`. Setelah login, **kartu pilih
  perusahaan bisa muncul tanpa mengubah URL** — klik "PT Maju Jaya" dulu,
  jangan langsung mencari tombol ribbon.
- Navigasi harus lewat ribbon (`button[aria-label="Penjualan"]`), bukan
  `page.goto` ke URL dalam — sistem tab akan mengarahkan balik ke `/`.
