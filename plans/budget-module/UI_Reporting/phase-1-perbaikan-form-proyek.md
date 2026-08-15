# Phase 1 — Perbaikan Form Proyek

**Sisi**: Frontend + Backend
**Prasyarat**: fase 0 dibaca
**Menutup**: T1, T2, T3

---

## Objective

Membuat `ProyekFormPage` benar-benar berfungsi, lalu mengganti tab "Anggaran" yang
mati dengan ringkasan **read-only** yang bersumber dari mesin Budget.

Fase ini didahulukan karena T2 dan T3 adalah bug yang sudah menyala: membuat proyek
dari UI selalu gagal, dan mengedit proyek menampilkan form kosong. Halaman-halaman
baru di fase 3–5 akan menautkan ke halaman proyek, jadi memperbaikinya belakangan
berarti membangun di atas yang rusak.

---

## 1. T2 — `code` proyek

Dua pilihan, dan pilihannya bukan selera:

| Opsi | Konsekuensi |
|---|---|
| **A. Backend membangkitkan `code`** | Konsisten dengan dokumen lain yang bernomor otomatis, tapi `projects` tidak terdaftar di layanan penomoran dokumen — perlu entri baru |
| **B. Form menampilkan field `code`** | Paling sedikit perubahan; `code` proyek memang biasanya ditentukan manusia ("PRJ-RENOV-01"), bukan berurut |

**Pilih B.** Kode proyek bersifat bermakna bagi pengguna, tidak seperti nomor
invoice yang harus berurut. Membangkitkannya otomatis justru mengambil kendali yang
diinginkan pengguna.

Perubahan:

```
frontend/src/modules/master-data/schemas/proyekSchema.ts
  + code: z.string().min(1, 'Kode proyek wajib diisi').max(50)

frontend/src/modules/master-data/types/proyek.types.ts
  + CreateProyekPayload.code: string

frontend/src/modules/master-data/pages/ProyekFormPage.tsx
  + FormField "Kode Proyek" (required), di sebelah kiri Nama
  + disabled saat mode edit — mengubah kode proyek yang sudah dipakai
    transaksi akan membingungkan; backend memang mengizinkan, tapi UI tidak
    perlu menawarkannya
```

Backend **tidak diubah** — `StoreProjectRequest` sudah benar, frontendnya yang
kurang. `ProjectService::create()` sudah menolak kode duplikat dengan
`DUPLICATE_PROJECT_CODE`; pastikan `applyApiValidationErrors` memetakannya ke field
`code`.

### Catatan status

`StoreProjectRequest` mengizinkan `active,completed,on_hold,cancelled`; frontend
`ProyekStatus` hanya punya tiga (tanpa `on_hold`). Tambahkan `on_hold` ke tipe dan
`STATUS_OPTIONS` supaya proyek yang di-`on_hold` lewat API tidak merusak dropdown.

---

## 2. T3 — memuat data di mode edit

```
frontend/src/modules/master-data/services/proyekApi.ts
  + get: (id: number) => http.get<unknown, ApiResponse<Proyek>>(`/master-data/projects/${id}`)
```

Endpoint `GET /master-data/projects/{id}` **sudah ada** (`ProjectController::show`),
hanya belum pernah dipanggil frontend.

```
frontend/src/modules/master-data/pages/ProyekFormPage.tsx
  + useQuery(['master-data-proyek', id], enabled: !isCreate)
  + reset(data) lewat useEffect saat data tiba
  + skeleton/disabled selama isLoading
```

Gunakan `reset()` dari React Hook Form, bukan `defaultValues` — data datang setelah
render pertama, dan `defaultValues` tidak dievaluasi ulang.

`formStatus` disimpan di `useState` terpisah dari RHF. Itu sumber kebenaran ganda
yang akan luput saat `reset()`. Pindahkan `status` ke dalam RHF (`Controller`),
supaya satu `reset()` mengisi seluruh form.

---

## 3. T1 — tab "Anggaran" jadi read-only

Sesuai keputusan **K1**. Tab tetap ada, isinya berubah total.

### Yang dihapus

- `interface BudgetLine`, `DEFAULT_BUDGET_LINE`, state `budgetLines`
- `budgetColumns` (5 kolom `LineItemColumn`)
- `LineItemsTable` di tab anggaran
- Perhitungan `totalRevenue`/`totalExpense`/`surplus` dari state lokal

### Yang menggantikan

Sumber data: `GET /budget/projects/{id}/summary?budget_period_id=…` — endpoint yang
sudah dipakai `ProjectFinancialSummaryPage`.

Muncul masalah kecil: endpoint itu **wajib** `budget_period_id`, sementara halaman
proyek tidak tahu periode mana yang dimaksud. Tiga cara, pilih yang ketiga:

| Cara | Masalah |
|---|---|
| Kirim tanpa periode | 404/422 — periode wajib di `resolvePeriod()` |
| Pilih periode di dalam tab | Menambah kontrol di halaman master data; canggung |
| **Default ke periode `open` yang mencakup hari ini, dengan dropdown kecil untuk pindah** | Tidak ada; ini yang dipakai |

Isi tab:

```
┌─ Anggaran ────────────────────────────────────────────────┐
│  Periode: [Anggaran 2026 ▾]        (default: periode open) │
│                                                            │
│  ⓘ  Anggaran proyek dikelola di modul Anggaran.           │
│     Tab ini hanya menampilkan.        [Kelola Anggaran →]  │
│                                                            │
│  ┌──────────────┬──────────────┐                          │
│  │ Anggaran     │ Realisasi    │                          │
│  │ Pendapatan   │ Pendapatan   │                          │
│  │ Biaya        │ Biaya        │                          │
│  │ Laba         │ Laba         │                          │
│  │ Margin %     │ Margin %     │                          │
│  └──────────────┴──────────────┘                          │
│                                                            │
│  ⚠ {meta.limitation}                                       │
│                                                            │
│  Rincian per akun (revenue_rows + cost_rows)               │
└────────────────────────────────────────────────────────────┘
```

Komponen `FinancialBlock` sudah ada di `ProjectFinancialSummaryPage.tsx`. **Jangan
menyalinnya.** Ekstrak ke `src/modules/budget/components/ProjectFinancialBlocks.tsx`
dan impor dari dua tempat — aturan "dilarang buat komponen baru jika sudah ada".

Impor lintas modul (`master-data` → `budget`) sah di frontend; tidak ada
`ModuleBoundariesTest` di sisi ini.

### Kalau proyek belum punya anggaran

Tampilkan empty state, bukan angka nol. "Rp 0" terbaca sebagai "dianggarkan nol",
sedangkan yang sebenarnya terjadi adalah "belum dianggarkan". Bedanya penting.

```
Proyek ini belum punya baris anggaran pada periode {nama}.
[Buat Anggaran →]   (→ /budget, permission budgets.submit)
```

### Permission

Seluruh tab dibungkus `can('budgets.view')`. Pengguna master data yang tidak
memegang izin anggaran tidak melihat tab sama sekali — bukan melihat tab kosong.

---

## 4. Navigasi

`ProyekFormPage` memakai `navigate()` langsung di tiga tempat. Aplikasi memakai
memory router bertab; ganti ke `useRecordTab`/`openRecordTab` sesuai pola modul lain.

Batasi hanya pada file ini. Jangan merambat ke `ProyekPage` atau modul lain — itu
di luar permintaan.

---

## Existing files affected

| File | Perubahan |
|---|---|
| `frontend/src/modules/master-data/pages/ProyekFormPage.tsx` | Perbaikan besar: `code`, fetch on edit, tab anggaran read-only, navigasi |
| `frontend/src/modules/master-data/schemas/proyekSchema.ts` | + `code` |
| `frontend/src/modules/master-data/types/proyek.types.ts` | + `code` di payload, + `on_hold` di `ProyekStatus` |
| `frontend/src/modules/master-data/services/proyekApi.ts` | + `get(id)` |
| `frontend/src/modules/budget/pages/ProjectFinancialSummaryPage.tsx` | Pakai `FinancialBlock` hasil ekstraksi |

## New files

| File | Isi |
|---|---|
| `frontend/src/modules/budget/components/ProjectFinancialBlocks.tsx` | `FinancialBlock` + `VarianceItem`, diekstrak |
| `frontend/src/modules/budget/hooks/useProjectBudgetForProject.ts` | Query ringkasan anggaran untuk satu proyek + resolusi periode default |

## Database changes

Tidak ada.

## Backend changes

Tidak ada. Semua endpoint yang dibutuhkan sudah ada.

---

## Risks

| Risiko | Mitigasi |
|---|---|
| Menghapus tab input bisa dianggap kemunduran fitur | Bukan — fitur itu tidak pernah bekerja. Tautan "Kelola Anggaran" memberi jalan yang benar-benar menyimpan. |
| `reset()` menimpa isian pengguna kalau query re-fetch | `staleTime` memadai + `reset` hanya pada perubahan `id`, bukan setiap `data` |
| Periode default tidak ketemu (tidak ada periode `open`) | Tampilkan empty state "Belum ada periode anggaran", bukan spinner selamanya |
| `code` disabled saat edit menutup kebutuhan sah mengganti kode | Backend tetap mengizinkan lewat API; kalau nanti diminta, cukup lepas `disabled` |

---

## Testing

Backend tidak berubah, jadi tidak ada test PHP baru.

Verifikasi manual (butuh backend hidup):

1. Buat proyek baru → berhasil, tidak 422
2. Buat proyek dengan kode duplikat → error muncul di field `code`, bukan toast generik
3. Buka proyek yang ada → semua field terisi
4. Ubah nama, simpan, muat ulang → perubahan bertahan
5. Tab Anggaran pada proyek yang punya anggaran → angka cocok dengan `/budget/projects`
6. Tab Anggaran pada proyek tanpa anggaran → empty state, bukan Rp 0
7. Pengguna tanpa `budgets.view` → tab Anggaran tidak muncul
8. `npm run build` 0 error, `rtk lint` bersih

---

## Acceptance criteria

- [ ] Buat proyek dari UI berhasil (T2 tertutup)
- [ ] Edit proyek memuat data (T3 tertutup)
- [ ] Tab Anggaran read-only, angkanya identik dengan `/budget/projects` untuk proyek & periode yang sama (T1 tertutup)
- [ ] Tidak ada jalur tulis `budget_lines` di luar `PUT /budget-submissions/{id}/lines`
- [ ] `FinancialBlock` hanya ada satu definisi di seluruh repo
- [ ] `npm run build` 0 error

---

## Hasil implementasi — 2026-08-15

### Yang dibuat/diubah

| File | Perubahan |
|---|---|
| `master-data/pages/ProyekFormPage.tsx` | Ditulis ulang: `code`, fetch on edit lewat `reset()`, `status` pindah ke RHF `Controller`, `key` remount, `useRecordTab` |
| `master-data/pages/ProjectBudgetTab.tsx` | **Baru** — tab anggaran read-only |
| `master-data/schemas/proyekSchema.ts` | + `code`, + `description`, + `on_hold`, + `refine` tanggal |
| `master-data/types/proyek.types.ts` | + `code`/`description` di payload, + `on_hold`, + `description` di `Proyek` |
| `master-data/services/proyekApi.ts` | + `get(id)` |
| `master-data/hooks/useSimpleLists.ts` | + `useProyek(id)` |
| `master-data/pages/ProyekPage.tsx` | `STATUS_LABELS`/`STATUS_COLORS` + `on_hold` |
| `budget/components/ProjectFinancialBlocks.tsx` | **Baru** — `FinancialBlock` + `VarianceItem` hasil ekstraksi |
| `budget/hooks/useProjectBudgetForProject.ts` | **Baru** — resolusi periode default + ringkasan |
| `budget/pages/ProjectFinancialSummaryPage.tsx` | Pakai komponen hasil ekstraksi |

### Penyimpangan

- **P6** — menambah `on_hold` ke `ProyekStatus` membuat `ProyekPage` gagal kompilasi:
  `STATUS_LABELS`/`STATUS_COLORS` bertipe `Record<ProyekStatus, string>`. Ikut
  diperbaiki. Itu bukan efek samping yang tidak diinginkan — tipenya memang
  sedang bekerja.
- Resolusi periode default dibuat lebih hati-hati dari rencana: periode `open`
  yang mencakup hari ini → periode `open` mana pun → periode dengan tahun fiskal
  terbesar. Tanpa langkah ketiga, proyek lama tampak tidak punya anggaran padahal
  punya di periode lampau.

### Verifikasi

`npm run build` 0 error · `rtk lint` bersih. Backend tidak disentuh.

### Yang belum

8 langkah verifikasi manual (butuh backend hidup).
