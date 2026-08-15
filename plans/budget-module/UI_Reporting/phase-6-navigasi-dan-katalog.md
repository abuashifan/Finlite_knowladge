# Phase 6 — Navigasi ANGGARAN & Katalog LAPORAN

**Sisi**: Frontend
**Prasyarat**: fase 3, 4, 5 (semua halaman yang mau ditautkan sudah ada)

---

## Objective

Menyusun dua tree yang diminta: ribbon modul ANGGARAN dan katalog LAPORAN.

Fase ini terakhir karena menautkan halaman yang belum ada akan menghasilkan menu
yang mengarah ke 404.

---

## 1. Ribbon ANGGARAN

`frontend/src/router/moduleConfig.ts` — modul `budget` sekarang punya 6 entri datar.
Tree yang diminta punya 4 grup.

### Sekarang

```
Periode Anggaran · Analisis Anggaran · Cash Budget ·
Anggaran Proyek · Dashboard Anggaran · Realisasi vs Anggaran
```

### Target

```
ANGGARAN
├── Dashboard
├── Budget
│   ├── Daftar Budget          /budget/submissions
│   ├── Buat Budget            /budget/submissions/new      [budgets.submit]
│   ├── Periode Anggaran       /budget/periods
│   └── Riwayat Revisi         /budget/submissions?has_versions=1
├── Monitoring
│   ├── Budget vs Actual       /budget/analysis?preset=vs-actual
│   ├── Variance               /budget/analysis?preset=variance
│   ├── Utilization            /budget/analysis?preset=utilization
│   └── Summary                /budget/analysis?preset=summary
├── Project
│   ├── Project Budget         /budget/projects?tab=budget
│   ├── Project Actual         /budget/projects?tab=actual
│   ├── Project Profitability  /budget/projects?tab=profitability
│   ├── Project Cash Flow      /budget/projects?tab=cash-flow
│   └── Project Transactions   /budget/projects?tab=transactions
└── Cash Budget                /budget/cash
```

### Dua penyimpangan dari tree yang diminta, dengan alasan

**"Detail" tidak jadi entri menu.** Detail submission butuh `:id`; sebuah entri
menu tidak punya id. Detail dijangkau dengan mengklik baris di Daftar Budget.
Entri menu bernama "Detail" yang tidak bisa diklik ke mana-mana lebih buruk
daripada tidak ada.

**"Revision" jadi "Riwayat Revisi" dan mengarah ke daftar terfilter.** Alasan yang
sama — revisi selalu milik satu submission. Entri ini membuka Daftar Budget dengan
filter yang menampilkan submission yang punya lebih dari satu versi.

Sebagai gantinya, "Periode Anggaran" naik ke grup Budget: ia master data pendukung
yang tetap perlu dijangkau, dan slot yang ditinggalkan "Detail" pas untuknya.

### Apakah `ModuleRibbonItem` mendukung grup?

**Periksa dulu sebelum menulis.** Struktur sekarang datar (`items: [...]`). Kalau
tipenya belum mendukung `group`, ada dua jalan:

| Jalan | Kapan dipakai |
|---|---|
| Tambah `group?: string` opsional, ribbon mengelompokkan yang punya | Modul lain tidak terpengaruh; ini yang didahulukan |
| Biarkan datar, pakai pemisah visual | Kalau perubahan tipe merambat ke banyak modul |

Jangan mengubah bentuk `ModuleRibbonItem` secara wajib (non-optional) — sembilan
modul lain memakainya.

### Permission per entri

Setiap entri wajib punya `permission`. "Buat Budget" → `budgets.submit`, sisanya
`budgets.view`. Aturan proyek: dilarang render tombol aksi tanpa cek permission.

---

## 2. Katalog LAPORAN

`frontend/src/modules/reports/constants/reportCategories.ts`

### Masalah sekarang

Sepuluh laporan anggaran dan proyek semuanya dijejalkan ke domain **`financial`
("Keuangan")**, berdampingan dengan Neraca dan Laba Rugi. Domain itu jadi punya 17
entri dan anggaran tenggelam di dalamnya.

### Target

Pecah jadi domain sendiri sesuai tree:

```
Keuangan          (tinggal 9 entri: Neraca, Laba Rugi, Arus Kas, dst.)
Anggaran          (7 entri)
Project           (4 entri)
Cash & Bank       (2 entri anggaran; domain cash-bank mungkin sudah ada — periksa)
```

| Domain | Entri | Path |
|---|---|---|
| **Anggaran** | Ringkasan Anggaran | `/budget/analysis?preset=summary` |
| | Anggaran vs Aktual | `/budget/analysis?preset=vs-actual` |
| | Analisis Variance | `/budget/analysis?preset=variance` |
| | Anggaran per Akun | `/budget/analysis?preset=vs-actual` |
| | Anggaran per Cost Center | `/budget/analysis` + `group_by=department` |
| | Anggaran per Project | `/budget/analysis` + `group_by=project` |
| | Anggaran per Periode | `/budget/analysis` + `group_by=period` |
| **Project** | Keuangan Project | `/budget/projects?tab=budget` |
| | Profitabilitas Project | `/budget/projects?tab=profitability` |
| | Budget vs Actual Project | `/budget/projects?tab=actual` |
| | Cash Flow Project | `/budget/projects?tab=cash-flow` |
| **Cash & Bank** | Cash Budget vs Actual | `/budget/cash` |

Catatan: "Cash Flow" (arus kas akuntansi) sudah ada di domain Keuangan sebagai
`/reports/cash-flow`. Jangan dipindah — itu laporan keuangan, bukan anggaran.
Yang masuk ke Cash & Bank hanya **Cash Budget vs Actual**.

### `reportKeyRoutes.ts`

Sembilan entri budget sudah ada tapi semuanya mengarah ke `/budget/analysis` polos
tanpa preset. Setelah fase 4, tambahkan query string preset supaya klik dari
katalog mendarat dengan filter yang benar — itu seluruh gunanya memisahkan report
key.

### `budget-comparison` — pertahankan

`/reports/budget/comparison` masih dipakai `BudgetComparisonPage` dan endpointnya
sengaja dipertahankan backend sebagai alias tipis. Biarkan di domain Keuangan
dengan nama "Realisasi vs Anggaran". Menghapusnya memutus halaman yang berfungsi
demi kerapian — tidak sepadan.

---

## Existing files affected

| File | Perubahan |
|---|---|
| `frontend/src/router/moduleConfig.ts` | Restrukturisasi entri modul `budget` jadi 4 grup |
| `frontend/src/modules/reports/constants/reportCategories.ts` | Pecah domain: Anggaran, Project, Cash & Bank |
| `frontend/src/modules/reports/constants/reportKeyRoutes.ts` | + preset di path, + key baru |
| `frontend/src/components/.../Ribbon*.tsx` | Hanya bila `group` ditambahkan ke tipe |

## New files

Tidak ada.

---

## Risks

| Risiko | Mitigasi |
|---|---|
| Mengubah `ModuleRibbonItem` merambat ke 9 modul lain | Field `group` **opsional**; modul lain tidak menyentuhnya |
| Memindahkan laporan memutus fitur "simpan laporan" pengguna | Report **key** tidak berubah, hanya domainnya. Kalau ada penyimpanan yang menyimpan `categoryPath`, periksa dulu sebelum memindah |
| Entri menu mengarah ke halaman fase 3–5 yang belum jadi | Karena itu fase ini terakhir |
| `detectModuleFromPath()` salah kenal karena query string | Deteksi memakai pathname; query string tidak ikut. Verifikasi tetap perlu |

---

## Testing

Verifikasi manual:

1. Setiap entri ribbon membuka halaman yang benar dengan filter yang benar
2. Tidak ada entri yang 404
3. Pengguna tanpa `budgets.submit` tidak melihat "Buat Budget"
4. Pengguna tanpa `budgets.view` tidak melihat modul ANGGARAN sama sekali
5. Membuka halaman anggaran menyorot modul ANGGARAN di ribbon (`detectModuleFromPath`)
6. Katalog laporan: domain Anggaran, Project, Cash & Bank muncul dengan isi yang benar
7. Domain Keuangan tidak lagi memuat entri anggaran kecuali `budget-comparison`
8. Klik entri katalog mendarat dengan preset aktif
9. `npm run build` 0 error, `rtk lint` bersih

---

## Acceptance criteria

- [ ] Tree ANGGARAN sesuai permintaan, dengan dua penyimpangan yang tercatat & beralasan
- [ ] Tree LAPORAN sesuai permintaan
- [ ] Tidak ada entri menu yang mengarah ke 404
- [ ] Semua entri punya `permission`
- [ ] Tipe `ModuleRibbonItem` tetap kompatibel untuk 9 modul lain
- [ ] `npm run build` 0 error

---

## Hasil implementasi — 2026-08-15

### Yang dibuat/diubah

| File | Perubahan |
|---|---|
| `router/moduleConfig.ts` | + `group?` opsional di `RibbonItem`; modul `budget` 6 → **14 entri** dalam 5 grup |
| `components/shared/layout/RibbonPanel.tsx` | + garis pemisah antar grup |
| `reports/constants/reportCategories.ts` | Domain **Anggaran** (8) & **Project** (5) baru; Cash Budget masuk domain `cash-bank` yang sudah ada; domain Keuangan 17 → 10 entri |
| `reports/constants/reportKeyRoutes.ts` | Semua path anggaran membawa `?preset=`; + 4 key project |

### Penyimpangan

- **P1** — grup ditandai **garis pemisah vertikal**, bukan menu bertingkat.
  `RibbonPanel` adalah strip horizontal `fixed` setinggi 64px berisi tombol ikon;
  menambah tingkat berarti mendesain ulang layout bersama yang dipakai 9 modul
  lain, dan mengubah tingginya merambat ke offset konten di tempat lain. Field
  `group?` dibuat **opsional** sehingga modul lain dirender persis seperti
  sebelumnya. Nama grup tetap hidup di breadcrumb halaman dan di katalog Laporan.
- **P2** — domain laporan `cash-bank` **sudah ada** (berisi "Mutasi Rekening").
  Cash Budget ditambahkan ke situ alih-alih membuat domain kedua bernama sama.
- Dua penyimpangan yang sudah diantisipasi rencana tetap berlaku: "Detail" tidak
  jadi entri menu (butuh `:id`), dan slotnya dipakai "Periode Anggaran".
  "Revision" diwakili riwayat versi yang dijangkau dari detail — entri menu
  terpisah untuk itu akan mengarah ke tempat yang tidak bisa ditentukan.
- "Arus Kas" akuntansi (`/reports/cash-flow`) **tidak** dipindah ke Cash & Bank.
  Itu laporan keuangan, bukan anggaran.

### Verifikasi

`npm run build` 0 error · `rtk lint` bersih.

### Yang belum

9 langkah verifikasi manual.
