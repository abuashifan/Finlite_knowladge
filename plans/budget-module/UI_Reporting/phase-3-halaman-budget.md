# Phase 3 — Halaman Budget: Daftar, Buat, Detail, Revisi

**Sisi**: Frontend
**Prasyarat**: fase 2 (endpoint daftar)
**Menutup**: view #4 (Budget Revision)

---

## Objective

Mewujudkan cabang `Budget` dari tree ANGGARAN dengan **submission** sebagai objek
utama (keputusan **K2**):

```
Budget
├── Daftar Budget      → /budget/submissions
├── Buat Budget        → /budget/submissions/new
├── Detail             → /budget/submissions/:id        (sudah ada)
└── Revision           → /budget/submissions/:id/versions (sudah ada)
```

Period tidak hilang — ia turun jadi master data pendukung di bawah menu terpisah.

---

## 1. Rute

| Rute | Halaman | Status |
|---|---|---|
| `/budget/submissions` | `BudgetSubmissionListPage` | **baru** |
| `/budget/submissions/new` | `BudgetSubmissionCreatePage` | **baru** |
| `/budget/submissions/:id` | `BudgetSubmissionPage` | ada |
| `/budget/submissions/:id/versions` | `BudgetVersionHistoryPage` | ada |
| `/budget/periods` | `BudgetPeriodListPage` | ada, **dipindah** dari `/budget` |
| `/budget/periods/new` | `BudgetPeriodFormPage` | ada |
| `/budget/periods/:id` | `BudgetPeriodDetailPage` | ada |
| `/budget` | redirect → `/budget/submissions` | **berubah** |

### Kenapa `/budget` di-redirect, bukan diganti isinya

`moduleConfig.ts` punya catatan eksplisit bahwa id modul `budget` dipilih agar
`detectModuleFromPath()` mencocokkan seluruh rute `/budget/...` tanpa memindahkan
satu rute pun. Mengubah `/budget` jadi redirect mempertahankan perilaku itu, dan
tautan lama ke `/budget` tetap mendarat di tempat yang masuk akal.

`/budget/periods/:id` bertabrakan dengan pola lama `/budget/periods/:id` — sudah
sama, tidak ada perubahan. Yang berubah hanya `/budget` itu sendiri.

---

## 2. `BudgetSubmissionListPage` (baru)

Sumber: `GET /budget-submissions` dari fase 2. Pakai `DataTable` yang sudah ada —
jangan bikin tabel sendiri.

| Kolom | Isi |
|---|---|
| Periode | `budget_period_name` |
| Departemen | `department_name`, atau "Perusahaan" kalau null |
| Versi | `v{version_no}`, badge "Aktif" bila `is_active` |
| Status | `BudgetStatusBadge` (komponen sudah ada) |
| Total Anggaran | `total_amount`, `tabular-nums`, rata kanan |
| Diajukan | `submitted_at` |

Filter di toolbar: Periode (dropdown), Departemen (`SearchableSelect`), Status
(dropdown), dan toggle "Tampilkan versi lama" (mematikan `is_active=true`).

Sort: kolom Periode, Versi, Status, dan Total. `sortKey` wajib ada di
`$listSortable` backend — kalau tidak, backend diam-diam mengabaikannya dan
pengguna melihat urutan yang tidak berubah.

`onRowClick` → buka tab detail via `openRecordTab`, bukan `navigate()`.

Tombol "Buat Budget" hanya dirender bila `can('budgets.submit')`.

### Departemen null

`department_id` boleh null — artinya anggaran tingkat perusahaan, bukan data hilang.
Tampilkan "Perusahaan", jangan "—". Pembedaan ini sudah dijaga backend
(`create()` memakai `whereNull` eksplisit agar dua anggaran perusahaan tidak bisa
dibuat untuk periode yang sama).

---

## 3. `BudgetSubmissionCreatePage` (baru)

Saat ini submission hanya bisa dibuat dari dalam `BudgetPeriodDetailPage`. Entri
"Buat Budget" di menu butuh halaman yang berdiri sendiri.

Form kecil, React Hook Form + Zod:

| Field | Aturan |
|---|---|
| Periode Anggaran | wajib, hanya periode `status=open` |
| Departemen | opsional — kosong = anggaran tingkat perusahaan, dengan teks bantu yang menjelaskan itu |
| Catatan | opsional |

Submit → `POST /budget-periods/{periodId}/submissions` → buka tab detail submission
yang baru.

Backend menolak duplikat dengan pesan yang sudah jelas ("A company-level submission
already exists for this period." / versi departemen). Tampilkan pesan itu apa
adanya di field Periode; jangan diganti pesan generik.

Halaman ini **tidak** mengisi baris anggaran. Baris diisi di halaman detail lewat
`BudgetLineEditor` yang sudah ada. Memisahkan keduanya menjaga satu pintu tulis
(aturan §3.1 fase 0).

---

## 4. Detail & Revisi — yang sudah ada

`BudgetSubmissionPage` dan `BudgetVersionHistoryPage` sudah berfungsi. Yang kurang
hanya keterjangkauan:

| Perubahan | File |
|---|---|
| Tombol "Riwayat Versi" di header detail | `BudgetSubmissionPage.tsx` |
| Tombol "Revisi" (bila `status=approved` && `can('budgets.revise')`) | `BudgetSubmissionPage.tsx` |
| Breadcrumb ke Daftar Budget | keduanya |
| Dari baris riwayat versi → buka detail versi itu | `BudgetVersionHistoryPage.tsx` |

Aksi revisi memanggil `POST /budget-submissions/{id}/revise` dengan
`revision_reason` — sudah ada di `budgetApi.revise`. Wajib ada dialog alasan;
`ReviseBudgetSubmissionRequest` mensyaratkannya.

---

## Existing files affected

| File | Perubahan |
|---|---|
| `frontend/src/modules/budget/routes.tsx` | + 2 rute, `/budget` jadi redirect, periode pindah ke `/budget/periods` |
| `frontend/src/modules/budget/services/budgetApi.ts` | + `listSubmissions()` lintas periode |
| `frontend/src/modules/budget/types/budget.types.ts` | + `BudgetSubmissionListRow`, + params |
| `frontend/src/modules/budget/pages/BudgetSubmissionPage.tsx` | + tombol Riwayat Versi & Revisi, breadcrumb |
| `frontend/src/modules/budget/pages/BudgetVersionHistoryPage.tsx` | + tautan ke detail versi, breadcrumb |

## New files

| File |
|---|
| `frontend/src/modules/budget/pages/BudgetSubmissionListPage.tsx` |
| `frontend/src/modules/budget/pages/BudgetSubmissionCreatePage.tsx` |
| `frontend/src/modules/budget/hooks/useBudgetSubmissions.ts` |
| `frontend/src/modules/budget/schemas/budgetSubmissionSchema.ts` |

---

## Risks

| Risiko | Mitigasi |
|---|---|
| Memindahkan `/budget` memutus bookmark/tautan lama | Redirect, bukan hapus |
| `detectModuleFromPath()` gagal mengenali rute baru | Semua rute tetap di bawah prefix `/budget` — tidak ada yang keluar |
| Daftar penuh versi lama, membingungkan | Default `is_active=true`; toggle eksplisit untuk melihat sisanya |
| `sortKey` tidak cocok dengan allowlist backend | Cocokkan satu per satu saat implementasi; sort yang diabaikan tidak memberi error, jadi harus diuji manual |

---

## Testing

Tidak ada test PHP baru (backend tidak berubah di fase ini).

Verifikasi manual:

1. `/budget` → mendarat di Daftar Budget
2. Daftar menampilkan submission lintas periode
3. Filter periode/departemen/status mempersempit
4. Toggle "versi lama" memunculkan yang `superseded`
5. Anggaran tingkat perusahaan tampil "Perusahaan", bukan "—"
6. Buat Budget → submission baru terbuka di tab detail
7. Buat duplikat → pesan backend muncul di field Periode
8. Detail approved → tombol Revisi muncul; tanpa `budgets.revise` → tidak muncul
9. Revisi tanpa alasan → ditolak dengan pesan
10. Riwayat versi terjangkau dari detail
11. `npm run build` 0 error, `rtk lint` bersih

---

## Acceptance criteria

- [ ] Empat entri menu Budget punya halaman yang berfungsi
- [ ] Submission bisa dibuat tanpa masuk ke detail periode dulu
- [ ] Revisi dan riwayat versi terjangkau dari detail (view #4 tertutup)
- [ ] Tidak ada tabel/agregasi baru — daftar memakai `DataTable` & endpoint fase 2
- [ ] `npm run build` 0 error

---

## Hasil implementasi — 2026-08-15

### Yang dibuat/diubah

| File | Perubahan |
|---|---|
| `pages/BudgetSubmissionListPage.tsx` | **Baru** — `DataTable`, paginasi & sort server-side |
| `pages/BudgetSubmissionCreatePage.tsx` | **Baru** — `FormSection`, RHF + Zod |
| `hooks/useBudgetSubmissions.ts` | **Baru** |
| `schemas/budgetSubmissionSchema.ts` | **Baru** |
| `services/budgetApi.ts` | + `listAllSubmissions()` |
| `types/budget.types.ts` | + `BudgetSubmissionListRow`, `BudgetSubmissionListParams` |
| `routes.tsx` | `/budget` → redirect, + 2 rute, periode pindah ke `/budget/periods` |
| `pages/BudgetSubmissionPage.tsx` | Breadcrumb |
| `pages/BudgetVersionHistoryPage.tsx` | Breadcrumb |
| `pages/BudgetPeriodListPage.tsx` | Judul & breadcrumb jadi "Periode Anggaran" |

### Penyimpangan

- **P4** — tombol "Riwayat Versi" dan "Revisi Anggaran" ternyata **sudah ada**
  di `BudgetSubmissionPage`, lengkap dengan `PermissionGuard budgets.revise` dan
  dialog alasan. Yang benar-benar kurang hanya breadcrumb. Rencana menganggapnya
  belum ada; memverifikasi lebih dulu menghemat pekerjaan yang tidak perlu.
- Zod di repo ini versi 4: `invalid_type_error` sudah tidak ada, diganti `error`.
- Form dibuat mengikuti konvensi form penerimaan (`FormSection`, label
  `text-[11px] uppercase`, input `h-9 text-[13px]`) sesuai permintaan.

### Verifikasi

`npm run build` 0 error · `rtk lint` bersih.

### Yang belum

11 langkah verifikasi manual.
