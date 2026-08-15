# Phase 0 — Temuan, Aturan & Guardrails

**Tidak ada kode di fase ini.** Isinya bukti temuan dan aturan main untuk fase 1–7.

---

## Objective

Mencatat apa yang sebenarnya terjadi di `ProyekFormPage.tsx` (dengan bukti, bukan
dugaan), lalu menetapkan aturan yang mengikat fase berikutnya.

---

## 1. Temuan: tab "Anggaran" di form Proyek tidak terhubung ke apa pun

Pertanyaannya: *"apakah virtual tab input budget di halaman form project terhubung
dengan budgeting yang baru diimplementasikan?"*

**Jawaban: tidak. Tidak terhubung ke modul Budget, dan juga tidak terhubung ke
backend mana pun.** Ini mockup UI yang tidak pernah diselesaikan.

### T1 — `budgetLines` tidak pernah dikirim

`frontend/src/modules/master-data/pages/ProyekFormPage.tsx`

State-nya ada:

```tsx
const [budgetLines, setBudgetLines] = useState<BudgetLine[]>([DEFAULT_BUDGET_LINE])
```

Tapi `onSubmit` tidak menyentuhnya sama sekali:

```tsx
const onSubmit = async (values: ProyekFormValues) => {
  const payload = { ...values, status: formStatus }   // ← budgetLines tidak ada
  ...
  const res = await proyekApi.create(payload)
}
```

Rantai buktinya lengkap sampai ke database:

| Lapis | Bukti |
|---|---|
| Form | `payload` hanya berisi `{ name, status, start_date, end_date }` |
| Skema Zod | `proyekSchema` tidak punya field anggaran |
| Tipe | `CreateProyekPayload` tidak punya field anggaran |
| Request backend | `StoreProjectRequest::rules()` tidak punya field anggaran |
| Service backend | `ProjectService::create()` hanya `Project::query()->create($data)` |

**Dampak bagi pengguna**: mengisi beberapa baris anggaran, melihat ringkasan
Surplus/Defisit terhitung dengan benar di layar, menekan Simpan, mendapat toast
*"Proyek berhasil dibuat"* — dan seluruh anggaran hilang tanpa satu pun pesan
kesalahan. Ini lebih buruk daripada tidak ada tab sama sekali.

### Modelnya juga skema lama, bukan skema baru

Andaikan kabelnya disambung apa adanya, isinya tetap salah:

| Tab Proyek (lama) | Mesin Budget (sekarang) |
|---|---|
| `type: 'revenue' \| 'expense'` dipilih manual oleh pengguna | `direction` **diturunkan** dari `chart_of_accounts.account_type`, tidak pernah diinput |
| `period: 'YYYY-MM'` | `period_month` |
| Tanpa `budget_submission_id` | Setiap baris wajib milik satu submission |
| Tanpa `department_id` | Dimensi cost center |
| Tanpa periode anggaran | Wajib berada dalam satu `budget_period` |

Membiarkan pengguna memilih `type` sendiri berarti mengizinkan akun beban ditandai
sebagai pendapatan — tepat kelas kesalahan yang ditutup fase 1 rencana sebelumnya.

---

## 2. Temuan: dua bug produksi yang berdiri sendiri

Keduanya ditemukan saat menelusuri T1. Tidak berkaitan dengan anggaran, tapi ada
di file yang sama dan harus diperbaiki lebih dulu.

### T2 — Buat Proyek selalu gagal 422

`StoreProjectRequest`:

```php
'code' => ['required', 'string', 'max:50'],
```

`ProjectController::store()` tidak membangkitkan `code`. Tidak ada
`prepareForValidation()`. Tidak ada layanan penomoran dokumen yang dipanggil.

Sementara di frontend, `proyekSchema` maupun `CreateProyekPayload` sama-sekali
tidak punya `code`, dan form tidak me-`register` field itu.

**Jalur buat proyek hanya satu** — `ProyekPage` menavigasi ke
`/master-data/projects/create`, yang merender `ProyekFormPage`. Jadi tidak ada
jalur alternatif yang mengirim `code`.

**Kesimpulan: membuat proyek dari UI tidak mungkin berhasil.** Selalu 422 pada
field yang bahkan tidak ditampilkan.

### T3 — Mode edit tidak pernah memuat data

`ProyekFormPage` membaca `id` dari URL:

```tsx
const { id } = useParams()
const isCreate = !id
```

…lalu tidak pernah menggunakannya untuk mengambil data. Tidak ada `useQuery`,
tidak ada panggilan `proyekApi` selain `create`/`update` saat submit.

**Dampak**: membuka proyek yang sudah ada menampilkan form kosong. Menekan Simpan
mengirim `name: ''` — yang akan ditolak Zod, jadi tidak sampai merusak data, tapi
halaman edit tetap tidak berfungsi.

---

## 3. Aturan untuk fase 1–7

### 3.1 Satu pintu tulis untuk anggaran

`PUT /budget-submissions/{id}/lines` adalah **satu-satunya** cara menulis
`budget_lines`. Halaman mana pun yang menampilkan anggaran boleh membaca sesukanya,
tapi menulis harus lewat pintu itu.

Alasannya bukan kerapian: submission adalah yang memegang periode, departemen
pemilik, status approval, dan nomor versi. Baris anggaran yang lahir di luar
submission tidak punya satu pun dari itu.

### 3.2 Halaman baru = preset, bukan mesin

Setiap halaman di fase 4 dan 5 harus bisa dijelaskan sebagai *"panggilan ke
`/budget/analysis` dengan parameter X"*. Kalau tidak bisa, hentikan dan tanyakan —
jangan tambahkan query agregasi baru.

### 3.3 Aturan proyek yang tetap berlaku

Dari `CLAUDE.md` dan `AGENTS.md`, yang paling sering tersandung di pekerjaan ini:

```
❌ DILARANG edit src/components/ui/
❌ DILARANG fetch di komponen — TanStack Query saja
❌ DILARANG simpan data API di Zustand
❌ DILARANG `any` tanpa justifikasi
❌ DILARANG hardcode URL API
❌ DILARANG render tombol aksi tanpa cek permission
✅ WAJIB React Hook Form + Zod untuk semua form
✅ WAJIB tabular-nums untuk semua angka
✅ WAJIB update docs/struktur_frontend.md kalau ada file baru
✅ WAJIB npm run build lulus 0 error
✅ WAJIB Pint + test backend kalau backend disentuh
```

Ditambah dua kebiasaan yang tercatat di memori sesi:

- Salin file UI lama ke scratchpad sebelum diedit, supaya bisa dibatalkan.
- Konfirmasi TypeScript dengan `npm run build`, bukan hanya `rtk tsc`.

### 3.4 Navigasi

Aplikasi memakai memory router dengan sistem tab. Navigasi antar record memakai
`useRecordTab`/`openRecordTab`, **bukan** `navigate()` langsung.

`ProyekFormPage` saat ini memakai `navigate()` langsung. Itu pelanggaran yang sudah
ada sebelum rencana ini; fase 1 menyentuh file tersebut, jadi sekalian dirapikan —
tapi jangan merambat ke file lain yang tidak diminta.

### 3.5 Peringatan G11 wajib tetap tampil

Selama Sales Return, Purchase Bill/Return, StockMovementJournalService, dan Fixed
Assets belum meneruskan `project_id` ke jurnal, angka **Actual** proyek bisa lebih
kecil dari kenyataan.

`meta.limitation` sudah dikembalikan backend dan sudah ditampilkan
`ProjectFinancialSummaryPage`. Setiap halaman baru di fase 5 wajib menampilkannya
juga. Menyajikan angka yang diam-diam kurang lebih berbahaya daripada tidak
menyajikan.

---

## Files affected

Tidak ada. Fase ini hanya dokumen.

---

## Acceptance criteria

- [ ] T1, T2, T3 terverifikasi ulang oleh pelaksana sebelum fase 1 dimulai
- [ ] K1 (tab read-only) dan K2 (submission sebagai objek utama) dipahami
- [ ] Aturan §3.1 dan §3.2 disepakati — keduanya membatasi fase 3–5
