# Fase 1 — Navigasi: modul topbar + katalog laporan

**Tujuan:** membuat modul Anggaran bisa dijangkau user tanpa deep link.

## Masalah

`src/router/moduleConfig.ts` punya 10 modul; Budget bukan salah satunya —
tidak ada ikon topbar, tidak ada ribbon. Karena aplikasi memakai
`createMemoryRouter`, satu-satunya jalan masuk adalah deep link saat muat
pertama. Praktisnya tidak ada user yang bisa membukanya.

`BudgetComparisonPage` juga yatim dari sisi lain: rutenya terdaftar di
`src/modules/reports/routes.tsx:79` tapi tidak ada entri di
`src/modules/reports/constants/reportCategories.ts`.

## Perubahan

### `src/router/moduleConfig.ts`

Tambahkan satu `ModuleConfig` **dengan `id: 'budget'`**. Id itu bukan pilihan
bebas: `detectModuleFromPath()` mencocokkan `pathname.startsWith('/' + m.id)`,
jadi `budget` langsung cocok dengan rute `/budget/...` yang sudah ada. Memakai
id lain berarti harus memindahkan seluruh rute.

```ts
{
  id: 'budget',
  label: 'Anggaran',
  path: '/budget',
  ribbonItems: [
    { id: 'budget-periods',    label: 'Periode Anggaran',      icon: CalendarRange, path: '/budget',                     permission: 'budgets.view' },
    { id: 'budget-comparison', label: 'Realisasi vs Anggaran', icon: GitCompare,    path: '/reports/budget/comparison',  permission: 'budgets.view' },
  ],
},
```

Ikon diambil dari `lucide-react` dan **wajib ditambahkan ke blok import di atas
file** — daftar import di sana eksplisit, bukan wildcard.

Letakkan setelah `accounting` (Buku Besar) dan sebelum `cash-bank`, supaya
urutan topbar mengikuti alur kerja akuntansi.

> `TOP_MODULES` diturunkan otomatis dari `MODULE_CONFIGS` dengan membuang
> `dashboard` — tidak ada yang perlu diubah di sana.

### `src/modules/reports/constants/reportCategories.ts`

Tambahkan `Realisasi vs Anggaran` ke domain yang paling pas (`financial`),
mengikuti bentuk entri yang sudah ada:

```ts
{ id: 'budget-comparison', title: 'Realisasi vs Anggaran',
  description: 'Perbandingan anggaran disetujui dengan realisasi jurnal',
  path: '/reports/budget/comparison', permission: 'budgets.view' },
```

### `src/modules/budget/routes.tsx`

`budgetRoutes` sekarang memakai `permission="budgets.view"` untuk **semua** rute.
Sesuaikan supaya mengikuti pola modul lain — rute yang membuat memakai permission
membuat:

| Rute | Permission |
|---|---|
| `/budget` | `budgets.view` |
| `/budget/periods/new` | `budgets.manage` |
| `/budget/periods/:id` | `budgets.view` |
| `/budget/submissions/:id` | `budgets.view` |

Rute pengajuan baru ditambahkan di Fase 2, bukan di sini.

## Yang TIDAK diubah

- **Tidak memindahkan rute apa pun.** Id modul `budget` sudah cocok dengan
  `/budget/*`.
- **Tidak menambah alias di `PERMISSION_ALIASES`.** Frontend memakai
  `budgets.view` dst. persis seperti backend, jadi `usePermission` mencocokkannya
  pada percobaan pertama. Diperiksa, bukan diasumsikan.
- **Tidak menaikkan `version` di `useTabStore`.** Itu hanya perlu saat entri menu
  **dihapus**; menambah entri tidak membuat tab lama jadi tidak sah.

## Verifikasi

```bash
rtk npm run build
```

Manual:

1. Login → topbar menampilkan **Anggaran**; klik membuka ribbon berisi dua entri.
2. Klik **Periode Anggaran** → tab primer Anggaran terbuka di halaman daftar.
3. Klik **Realisasi vs Anggaran** → halaman perbandingan terbuka.
4. Laporan → katalog memuat **Realisasi vs Anggaran** dan tautannya jalan.
5. **Uji dengan role selain `owner`/`admin`** — keduanya wildcard `*` dan akan
   selalu lolos, jadi tidak membuktikan apa pun. Role `finance` punya kelima
   permission `budgets.*`; role `sales` tidak punya satu pun, jadi ikon
   Anggaran harus hilang untuknya.
