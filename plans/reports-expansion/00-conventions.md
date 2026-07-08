# 00 — Konvensi Reports Expansion

> Baca ini setelah `README.md`, sebelum membuka file fase. Singkat tapi wajib.
> Semua path relatif ke root repo `/home/tiny/Desktop/finlite/` kecuali disebut lain.

---

## 1. Anatomi satu laporan (checklist umum)

Setiap laporan baru melewati sebagian atau seluruh langkah ini. File fase menyebut mana yang berlaku.

**Backend (hanya jika endpoint belum ada):**
1. **Service** di `laravel_backend/app/Modules/{Modul}/Services/` — semua query & business logic. Baca `TenantContext` (company scope sudah otomatis lewat `company.access` + global scope tenant). JANGAN taruh logic di controller.
2. **FormRequest** di `.../Requests/` — validasi param. Pakai trait `App\Modules\Reports\Requests\Concerns\HasReportDateFilters` (start_date/end_date) & `HasReportDimensionFilters` (department_id/project_id/warehouse_id) bila relevan, contoh: `app/Modules/Reports/Requests/GeneralLedgerRequest.php`.
3. **Controller** di `.../Controllers/` — tipis: terima FormRequest, panggil service, bungkus `ApiResponseBuilder` (Shared). Contoh: `app/Modules/Reports/Controllers/GeneralLedgerController.php`.
4. **Route** di `.../Routes/api.php` — `->middleware('permission:{permission}')`. Untuk laporan di modul Reports pakai `reports.view`; laporan yang tinggal di modul lain (sales/purchase/inventory) pakai permission modul itu bila memang endpoint modul, atau `reports.view` bila endpoint report.
5. **Feature test** di `laravel_backend/tests/Feature/` — happy path + minimal 1 failure path (mis. tanpa permission → 403, param invalid → 422). WAJIB untuk endpoint baru (AGENTS.md backend §2A).

**Frontend (selalu):**
6. **Type** di `react_frontend/src/modules/reports/types/reports.types.ts` (atau types modul terkait) — shape response STABIL yang dibaca page.
7. **Adapter + method** di `react_frontend/src/modules/reports/services/reportsApi.ts` — `adapt{Nama}(raw)` menormalkan response backend → type stabil (num()/str()/asArray()/asRecord() helpers sudah ada di file). Tambah method `reportsApi.{nama}(params)`. **Tidak boleh** page membaca `res.data.x` mentah.
8. **Page** `react_frontend/src/modules/reports/pages/{Nama}Page.tsx` — pola di §3.
9. **Route** di `react_frontend/src/modules/reports/routes.tsx` — `{ path: '/reports/...', element: wrap(<Page/>) }` (`wrap` = `ProtectedRoute permission="reports.view"`).
10. **Katalog** di `react_frontend/src/modules/reports/constants/reportCategories.ts` — tambah/aktifkan `ReportEntry` (hapus `comingSoon: true` saat halaman siap).
11. **struktur_frontend.md** — daftarkan file baru (`react_frontend/docs/struktur_frontend.md`). Wajib (AGENTS.md §10B).

---

## 2. Pola adapter API (frontend)

`reportsApi.ts` sudah punya helper: `asRecord(v)`, `asArray(v)`, `num(v)`, `str(v)`, `adaptResponse(res, fn)`, `getRawApiResponse(path, params)` (untuk endpoint yang butuh header manual/di luar `http` instance). Tiap laporan baru:

```ts
function adaptSalesByCustomer(raw: Raw): SalesByCustomerReport {
  return {
    rows: asArray(raw.rows).map((r) => ({
      customer_id: num(r.customer_id),
      customer_name: str(r.customer_name),
      invoice_count: num(r.invoice_count),
      total: num(r.total),
    })),
    totals: { total: num(asRecord(raw.totals).total) },
  }
}

// di object reportsApi:
salesByCustomer: (params: ReportParams) =>
  http.get<unknown, ApiResponse<unknown>>('/reports/sales/by-customer', { params })
    .then((res) => adaptResponse(res, adaptSalesByCustomer)),
```

Aturan keras: **setiap number lewat `num()`, setiap string lewat `str()`, setiap array lewat `asArray()`.** Ini yang mencegah crash Phase 36 (A13-232/237/238).

---

## 3. Pola halaman laporan (frontend)

Template minimal (lihat `pages/GeneralLedgerPage.tsx` sebagai referensi lengkap dengan pagination + CSV export + dimension filters):

```tsx
export default function XxxReportPage() {
  const [params, setParams] = useState<ReportParams>({ start_date: firstOfMonth, end_date: today })
  const [activeParams, setActiveParams] = useState<ReportParams | null>(null)
  const [showFilter, setShowFilter] = useState(true)
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['reports', 'xxx', activeParams],
    queryFn: () => reportsApi.xxx(activeParams!),
    enabled: !!activeParams,
  })
  // ...
  return (
    <WorkspaceLayout title="..." breadcrumb={[{ label: 'Laporan', path: '/reports' }, { label: '...' }]}>
      {showFilter
        ? <ReportFilterParameter params={params} onChange={...} onSubmit={handleSubmit} isLoading={isLoading} />
        : <ReportCompactBar params={activeParams!} onEdit={() => setShowFilter(true)} />}
      {isLoading && <Loading/>}
      {isError && <ReportError onRetry={() => refetch()} />}
      {/* tabel + TablePagination + tombol exportCsv */}
    </WorkspaceLayout>
  )
}
```

Komponen wajib dipakai (JANGAN buat baru bila sudah ada):
- `WorkspaceLayout` — shell halaman + breadcrumb.
- `ReportFilterParameter` — panel filter (date range + `dimensions`/`extras` props).
- `ReportCompactBar` — bar ringkas setelah submit.
- `ReportError` — error state + retry.
- `TablePagination` (`@/components/shared/table/TablePagination`) — pagination client-side.
- `exportCsv` (`@/lib/exportCsv`) — tombol Export CSV.
- `formatCurrency` (`@/lib/utils`) + kelas `tabular-nums` untuk SEMUA angka.

Aturan tablet-first (spec-23): halaman full-screen pakai `h-dvh`/`min-h-dvh`, sediakan compact mode `@media(max-height:620px)`. `WorkspaceLayout` sudah menangani sebagian — verifikasi di viewport pendek.

---

## 3A. Peta File (format wajib tiap fase)

Tiap file fase punya bagian **"Peta File"** dengan tiga sub-daftar. Ini kontrak eksplisit supaya agent tahu persis file mana disentuh tanpa mengurai prosa. Legenda:

- **✏️ Ubah** — file existing yang diedit.
- **➕ Tambah** — file baru yang dibuat.
- **🗑️ Hapus** — file yang dihapus (jarang untuk plan ini — mayoritas fase menambah).

Path selalu relatif dari root repo. Prefix repo eksplisit: `react_frontend/…` (FE) atau `laravel_backend/…` (BE). Bila sebuah file "conditional" (hanya disentuh jika endpoint belum ada / opsi tertentu dipilih), tandai `(kondisional: …)`.

Anchor path yang sering dipakai (referensi cepat):

```
# Frontend (react_frontend/src/modules/reports/)
  constants/reportCategories.ts     ✏️ hampir selalu (tambah/aktifkan ReportEntry)
  routes.tsx                        ✏️ tiap kali ada halaman baru
  types/reports.types.ts            ✏️ tiap laporan baru (type + param)
  services/reportsApi.ts            ✏️ tiap laporan baru (adapter + method)
  pages/{Nama}Page.tsx              ➕ tiap halaman laporan baru
  components/*                      ✏️ jarang (reuse; jangan buat baru bila ada)
react_frontend/docs/struktur_frontend.md   ✏️ tiap ada file baru
react_frontend/src/router/moduleConfig.ts  ✏️ HANYA saat menambah kategori ribbon baru (Fase 11)

# Backend (laravel_backend/app/Modules/Reports/)
  Services/{Sub}/{Nama}Service.php        ➕ endpoint baru
  Requests/{Sub}/{Nama}Request.php        ➕ endpoint baru
  Controllers/{Sub}/{Nama}Controller.php  ➕/✏️ endpoint baru
  Routes/api.php                          ✏️ tiap route baru
laravel_backend/tests/Feature/Reports/{Nama}Test.php  ➕ tiap endpoint baru
laravel_backend/database/migrations/tenant/*          ➕ hanya fase yang ubah schema (8, 13; mungkin 11/12)
```

---

## 4. Permission

- Semua route report frontend dibungkus `ProtectedRoute permission="reports.view"` (via `wrap`).
- Kartu/tombol yang butuh permission lain (mis. export pajak) dicek dengan `usePermission`.
- Backend route report pakai `permission:reports.view` kecuali file fase menyebut permission granular baru (mis. `reports.tax.view`) — bila permission baru, daftarkan di seeder permission backend + dokumentasikan.

---

## 5. Katalog & navigasi — cara menambah laporan tanpa membongkar shell

`reportCategories.ts` → `REPORT_DOMAINS[]`. Untuk mengaktifkan laporan:
- Cari domain yang sesuai (`financial`, `gl`, `sales`, `purchase`, `ar`, `ap`, `reconciliation`, `inventory`, `fixed-assets`, `cash-bank`; tambah `tax` di Fase 11).
- Tambah `ReportEntry { id, title, description, path }`. Kalau halamannya belum siap, set `comingSoon: true` (kartu tampil disabled "Segera").
- Ribbon di `router/moduleConfig.ts` grup `reports` menampilkan **kategori** (bukan laporan) — hanya perlu diubah jika **menambah kategori baru** (mis. `tax` di Fase 11). Menambah laporan ke kategori existing TIDAK menyentuh ribbon.
- `DEFAULT_DOMAIN` = `financial` (index `/reports` redirect ke sini).

---

## 6. Verifikasi standar per fase

**Frontend:**
```bash
cd /home/tiny/Desktop/finlite/react_frontend
npm run build      # WAJIB 0 error
npm run lint       # 0 error (warning boleh)
```
Runtime (opsional tapi disarankan untuk laporan yang menyentuh data): login `admin@example.com` / `password`, header `X-Company-ID: 2` (company 2 punya data — lihat memory finlite-runtime-bootstrap). Playwright headless chromium untuk cek render + viewport (1440×900, 1180×708, 1024×656).

**Backend (bila diubah):**
```bash
cd /home/tiny/Desktop/finlite/laravel_backend
php artisan test --filter=<TestClassBaru>   # test tersempit, BUKAN suite penuh
vendor/bin/pint --test                       # style, file yang diubah harus lulus
php artisan route:list --path=api | wc -l    # bertambah sesuai jumlah route baru
```
> Catatan: sepanjang refactor modularization user minta skip suite penuh. Untuk plan ini, **feature test per-endpoint-baru tetap wajib ditulis & dijalankan tersempit** (aturan AGENTS.md backend). Suite penuh tetap boleh ditunda ke sesi testing manual user.

---

## 7. Definition of Done per fase

Fase dianggap ✅ Selesai bila:
1. Semua laporan yang dijadwalkan di fase itu: backend (bila perlu) + adapter + type + page + route + katalog + struktur_frontend.md — lengkap.
2. `npm run build` 0 error; `npm run lint` 0 error.
3. Bila backend diubah: feature test baru hijau (tersempit) + `pint --test` hijau + route count bertambah sesuai.
4. Tidak ada `comingSoon: true` tersisa untuk laporan yang seharusnya sudah aktif di fase itu.
5. Ledger `README.md` di-update (`⬜` → `✅` + commit hash) dan di-commit.
6. Runtime smoke (bila fase menyentuh data live): laporan render tanpa crash di company 2, angka masuk akal.
7. **Peta direktori disinkronkan** bila fase menambah file/direktori baru:
   - `react_frontend/docs/struktur_frontend.md` (kanonik) untuk file FE baru — sudah wajib per AGENTS.md.
   - `laravel_backend/docs/backend-directory-tree.md` (kanonik) bila menambah **direktori** BE baru (mis. `Services/Sales/`, `Requests/Tax/`).
   - Lalu **salin ulang keduanya** ke `Finlite_Knowladge/reference/` (lihat `reference/README.md`). Ini mencegah peta di knowledge base jadi basi.

---

## 8. Ranjau & pelajaran (dari Phase 36 / Audit-12/13)

- **Response inventory dibungkus** `{ filters, rows, totals }` — `.map()` langsung pada objek crash. Selalu `asArray(raw.rows)`.
- **Aging** backend pakai key bucket `'1_30'`, `'31_60'`, `'61_90'`, `over_90` (string), bukan camelCase. Lihat `adaptAgingBucket`.
- **Param periode** harus canonical `start_date`/`end_date` (A13-233). Jangan kirim nama param lain ke backend.
- **AR/AP aging** endpoint ada di modul sales/purchase (`/sales/ar/aging`, `/purchase/ap/aging`), BUKAN `/reports/*`. Adapter AP pakai `apAdapters` dari modul purchase. Konsisten: kalau laporan agregasi sales/purchase baru, boleh taruh endpoint di modul sales/purchase ATAU sub-prefix `/reports/sales|purchase/*` — file fase menentukan; default rencana ini pakai **sub-prefix `/reports/sales/*` & `/reports/purchase/*`** agar terkumpul di modul Reports (lebih rapi untuk katalog). Bila memilih modul sales/purchase, dokumentasikan di file fase.
- **Financial summary** dulu salah baca `mode` — pastikan adapter membaca struktur nested `profit_loss`/`balance_sheet`/`cash_flow`.
- **Fixed Assets register** mengembalikan **array langsung** (bukan `{data:{...}}`) — adapter `faRegister` menangani `Array.isArray(res.data)`. Pola ini bisa berulang; selalu cek bentuk response nyata via runtime/tinker sebelum menulis adapter.

---

## 9. Git checkpoint

- Cek dulu branch aktif frontend (`react_frontend`) & backend (`laravel_backend`). Bila di default branch, buat branch dulu (aturan global "commit/push hanya bila user minta" — **jangan push tanpa diminta**).
- Satu commit per fase (frontend + backend perubahan fase itu boleh satu commit bila satu repo; repo terpisah → commit di masing-masing).
- Format commit frontend: `feat(reports): <ringkasan fase>`. Backend: `feat(reports): <ringkasan>` di repo laravel.
- Setelah commit fase, update ledger `README.md` di `Finlite_Knowladge` dan commit terpisah di repo itu.
- Akhiri commit message dengan baris co-author sesuai aturan global.
