# Frontend — React SPA

`/workspace/frontend/` · React 19.2 · Vite 8 · TypeScript 6 · TanStack Query 5 ·
Zustand 5 · React Hook Form 7 + Zod 4 · Tailwind 3 + shadcn/Radix · Axios · Recharts

> `CLAUDE.md`/`AGENTS.md` menyebut React 18 — itu sudah tidak akurat, `package.json`
> menyatakan React 19.2.

---

## 1. Struktur

```
src/
  modules/<modul>/        15 modul — semua kode fitur
  components/shared/      37 komponen lintas modul   -> lihat 04-komponen-reusable.md
  components/ui/          shadcn generated — JANGAN DIEDIT
  hooks/                  15 hook global
  stores/                 4 store Zustand
  lib/                    utilitas murni
  services/http.ts        satu-satunya instance Axios
  router/                 router, guard, konfigurasi ribbon
  types/                  tipe lintas modul
```

### Isi standar sebuah modul

```
src/modules/sales/
  pages/       components/   hooks/   services/   schemas/   types/   routes.tsx
```

- `services/` — **semua** panggilan API. Tidak boleh ada `http.get` di komponen.
- `schemas/` — skema Zod untuk form.
- `routes.tsx` — array route, tiap halaman `lazy()`, dibungkus `ProtectedRoute` lewat
  helper lokal `guard()`/`wrap()` (lihat `05-role-permission-guard.md` §7).

---

## 2. Modul & ukuran

145 halaman, 180 route (169 di modul + 11 di router utama), 464 file TS/TSX.

| Modul | Halaman | Route | Service | Hook |
|---|---|---|---|---|
| reports | 42 | 42 | 2 | 4 |
| sales | 21 | 31 | 10 | 9 |
| purchase | 19 | 28 | 17 | 8 |
| master-data | 13 | 16 | 10 | 5 |
| cash-bank | 8 | 12 | 1 | 1 |
| inventory | 8 | 11 | 4 | 4 |
| settings | 9 | 9 | 2 | 2 |
| accounting | 5 | 6 | 4 | 3 |
| budget | 5 | 4 | 1 | 0 |
| fixed-assets | 4 | 8 | 2 | 3 |
| opening-balance | 2 | 2 | 1 | 1 |
| auth | 2 | — (di router utama) | 2 | 0 |
| onboarding | 1 | — | 1 | 0 |
| dashboard | 1 | — | 1 | 1 |
| errors | — | 5 | — | — |

---

## 3. Router — memory router, bukan browser router

**`src/router/index.tsx` memakai `createMemoryRouter`.** Ini menjelaskan perilaku yang
sering disalahpahami:

```ts
const initialEntry = `${location.pathname}${location.search}${location.hash}`
if (window.location.pathname !== '/') {
  window.history.replaceState(window.history.state, '', '/')
}
export const router = createMemoryRouter([...], { initialEntries: [initialEntry] })
```

Konsekuensinya:

- **URL di address bar praktis selalu `/`** dan tidak berubah saat navigasi.
  Jadi `page.url()` di Playwright **tidak bisa dipakai sebagai assertion** — periksa
  isi layar. Ini juga sebabnya layar login bisa tampil sementara URL masih `/`.
- **Deep link hanya berlaku sekali**, pada muat pertama, lewat `initialEntries`.
- **Navigasi Playwright harus lewat UI** (klik ribbon), bukan `page.goto('/sales/...')`.

### Guard rute

`src/router/guards.tsx` — tiga guard, dijelaskan lengkap di `05-role-permission-guard.md`.

Perlu diketahui di sini: **`ProtectedRoute` juga yang merender `AppShell`**. Halaman
yang dipasang di router **tanpa** `ProtectedRoute` (mis. `<Navigate>` telanjang) berada
di luar shell, dan itu pernah menyebabkan shell unmount-mount berulang.

---

## 4. Shell tab — Zustand adalah sumber kebenaran navigasi

Aplikasi memakai tab ala desktop, bukan navigasi URL.

```
Topbar          ikon modul, nama perusahaan, menu pengguna
 └ RibbonPanel  daftar menu modul (overlay)
PrimaryTabs     satu tab per modul yang dibuka, maksimum 10, Dashboard selalu ada
 └ SecondaryTabs  di dalam tab primer: "Daftar" (pinned) + tab record/form
```

`src/stores/useTabStore.ts` (persist **sessionStorage**, `version: 5`) menyimpan
`primaryTabs`, `secondaryTabs`, tab aktif, status ribbon dan sidebar.

`AppShell` menyetir router dari state itu:

```tsx
useEffect(() => { navigate(getActiveContentPath(), { replace: true }) },
          [activePrimaryTabId, activeSecondaryTabId])
```

> **Artinya `navigate(path)` langsung akan ditimpa kembali.** Untuk memindahkan user,
> ubah state tab (`setActivePrimaryTab` + `setActiveSecondaryTab`), bukan router.
> Contoh nyata: `focusFormTab()` di `lib/companySession.ts`.

`migrate` di store membuang tab yang menunya sudah dihapus (`RETIRED_TAB_IDS`).
**Menghapus entri menu wajib disertai menaikkan `version` dan membuang tab lamanya**,
kalau tidak user yang sudah menyimpan tab itu akan terjebak di rute yang tidak ada lagi.

`src/router/moduleConfig.ts` mendefinisikan modul + isi ribbon:
`MODULE_CONFIGS` → `MODULE_MAP` dan `TOP_MODULES`. Flag: `opensListDirectly`
(modul tanpa ribbon, mis. Laporan) dan `flushContent` (toolbar sendiri menempel di tab).

---

## 5. State — empat store, batas tanggung jawabnya tegas

| Store | Persist | Isi | Catatan |
|---|---|---|---|
| `useAuthStore` | localStorage `seaside-auth` | token, user, permissions, companies, `activeCompanyId`, rememberMe | `closeCompany()` = tutup database; `logout()` = akhiri sesi |
| `useCompanyStore` | **tidak** | `activeCompany`, `settings` | hilang saat reload — jangan diandalkan sebagai satu-satunya sumber |
| `useTabStore` | sessionStorage | tab & shell | lihat §4 |
| `useUnsavedFormsStore` | **tidak** | path form yang belum tersimpan | disengaja tidak persist |

> **Aturan keras: jangan simpan data API di Zustand.** Data server milik TanStack Query.

### Cache query ber-scope perusahaan

`src/lib/companyScope.ts` berlangganan perubahan `activeCompanyId` lalu
`queryClient.clear()` + menutup semua tab. Dipasang sekali di `main.tsx`.

Query key **tidak** memuat id perusahaan, jadi mekanisme ini yang menjaga data tidak
bocor antar tenant. Kalau Anda menambahkan jalur baru yang mengubah perusahaan, jalur
itu otomatis tercakup — jangan menduplikasi pembersihan cache di tempat lain.

Setelan default `QueryClient` (`main.tsx`): `staleTime: 30_000`, `gcTime: 5 menit`,
`retry: 1`, `refetchOnWindowFocus: false`.

---

## 6. Alur data satu halaman daftar

```
Halaman  →  hook modul (useQuery)  →  service modul  →  http.ts  →  API
```

```ts
// hooks/useCoaList.ts
export function useCoaList(params: CoaListParams) {
  return useQuery({ queryKey: ['master-data-coa', params], queryFn: () => coaApi.list(params) })
}
```

Di komponen: `data?.data` = baris, `data?.meta.total` = total (lihat `01-arsitektur.md` §2).

Mutasi selalu `invalidateQueries` pada key modulnya:

```ts
const invalidate = () => qc.invalidateQueries({ queryKey: ['master-data-coa'] })
```

---

## 7. Form

Semua form: **React Hook Form + Zod** (`zodResolver`), skema di `schemas/`.

Hook pendukung:

| Hook | Kegunaan |
|---|---|
| `usePersistentFormDraft` | menyimpan isian belum tersimpan ke localStorage, **ber-scope perusahaan** (`company-<id>`), dipakai 26 dari 28 halaman form |
| `useUnsavedFormTracker` | melaporkan form kotor ke `useUnsavedFormsStore`; dipanggil di dalam hook draft, dan langsung oleh 2 halaman yang tidak memakainya |
| `useRecordFormNavigation` | simpan-dan-tutup, tombol Prev/Next antar record |
| `useRecordTab` / `useOpenPrimaryTab` | membuka tab record/modul |
| `useDocumentActions` | approve/post/void beserta konfirmasinya |

> **Halaman form baru yang tidak memakai `usePersistentFormDraft` WAJIB memanggil
> `useUnsavedFormTracker({ control })` sendiri.** Kalau lupa, isian di halaman itu
> hilang tanpa peringatan saat user menutup database atau keluar.
> Dua halaman yang sudah begitu: `BudgetPeriodFormPage`, `FixedAssetFormPage`.

Deteksi "kotor" memakai `formState.dirtyFields`, **bukan `isDirty`** — `isDirty`
menyala pada form yang belum disentuh, karena hampir semua form menyetel
`defaultValues` sebagian sehingga field lain berubah `undefined` → `''` saat didaftarkan.

---

## 8. Design token

`tailwind.config.ts` — pakai token ini, jangan warna ad-hoc:

| Token | Nilai | Untuk |
|---|---|---|
| `sidebar` | `#326273` | topbar & sidebar |
| `canvas` | `#EFEFED` | latar halaman |
| `surface` | `#ffffff` | kartu, tabel |
| `soft` | `#eeeeee` | header tabel |
| `text-base` | `#24323a` | teks utama |
| `text-muted` | `#64748b` | teks sekunder |
| `border-base` | `#d9e2e5` | garis |
| `status.*` | — | pasangan bg/text per status dokumen |

Aksen yang sering muncul di kode: `#5c9ead` (biru primer), `#e39774` (oranye tombol
utama). **Angka wajib `tabular-nums`.**

---

## 9. Perintah

```bash
rtk npm run dev      # Vite di :5173, mem-proxy /api ke 127.0.0.1:8000
rtk npm run build    # tsc -b + vite build — SATU-SATUNYA pengetikan yang nyata
rtk lint             # eslint
```

`npx tsc --noEmit` **tidak** memeriksa apa pun di project ini (sudah dibuktikan dengan
error sengaja). Selalu pakai `npm run build`.
