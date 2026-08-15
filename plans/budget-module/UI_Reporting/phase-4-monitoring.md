# Phase 4 — Monitoring & Preset Laporan

**Sisi**: Frontend
**Prasyarat**: —
**Menutup**: view #3, #11, #12, #13, #14

---

## Objective

Mewujudkan cabang `Monitoring` dari tree ANGGARAN:

```
Monitoring
├── Budget vs Actual
├── Variance
├── Utilization
└── Summary
```

Keempatnya **preset dari halaman yang sama**. Tidak ada halaman baru, tidak ada
endpoint baru — hanya URL berparameter yang mendarat di `BudgetAnalysisPage`
dengan filter awal berbeda.

---

## 1. Preset lewat query string

`BudgetAnalysisPage` (425 baris) sudah melayani seluruh kombinasi `group_by`,
`mode`, `direction`, dan `allocation`. Yang belum ada: cara menautkan langsung ke
sebuah kombinasi.

Tambahkan pembacaan `useSearchParams` yang mengisi state filter awal:

| Menu | URL | Parameter awal |
|---|---|---|
| Budget vs Actual | `/budget/analysis?preset=vs-actual` | `group_by=[account]`, `mode=summary` |
| Variance | `/budget/analysis?preset=variance` | `group_by=[account]`, `mode=variance` |
| Utilization | `/budget/analysis?preset=utilization` | `group_by=[account]`, urut serapan tertinggi |
| Summary | `/budget/analysis?preset=summary` | `group_by=[]`, total saja + drill-down |

Nilai `preset` hanya **mengisi state awal**. Setelah halaman terbuka, pengguna bebas
mengubah filter dan URL tidak perlu ikut berubah — ini bukan state yang
disinkronkan dua arah, cukup satu arah saat mount.

Definisikan peta preset sebagai konstanta bertipe, bukan `if` berantai:

```ts
const ANALYSIS_PRESETS = {
  'vs-actual':   { group_by: ['account'], mode: 'summary' },
  'variance':    { group_by: ['account'], mode: 'variance' },
  'utilization': { group_by: ['account'], mode: 'summary', sortBy: 'utilization' },
  'summary':     { group_by: [],          mode: 'summary' },
  'revenue':     { group_by: ['account'], direction: 'revenue' },
  'expense':     { group_by: ['account'], direction: 'expense' },
} as const satisfies Record<string, Partial<BudgetAnalysisParams>>
```

Preset tak dikenal → abaikan, pakai default. Jangan lempar error; URL bisa datang
dari bookmark lama.

---

## 2. View #11 — Remaining Budget

Angkanya sudah ada, namanya yang belum. Backend mengembalikan `variance`
(budget − actual, dengan konvensi arah), yang **untuk baris beban** sama persis
dengan sisa anggaran.

Tambahkan kolom "Sisa Anggaran" di `BudgetAnalysisPage` yang menampilkan `variance`
dengan label berbeda. **Jangan menambah field di backend** — itu akan jadi dua nama
untuk satu angka, dan cepat atau lambat keduanya akan berbeda karena bug.

Satu jebakan: untuk baris **pendapatan**, `variance` positif berarti "melebihi
target" (bagus), bukan "sisa". Karena itu:

- Kolom "Sisa Anggaran" hanya muncul saat tampilan difilter `direction=expense`
- Pada tampilan campuran, kolomnya tetap bernama "Selisih"

Ini bukan kerewelan: menamai kolom "Sisa Anggaran" pada baris pendapatan akan
membuat pengguna membaca surplus penjualan sebagai anggaran yang belum terpakai.

---

## 3. View #3 — Budget Allocation

Parameter `allocation` (`annual_row` | `even`) sudah didukung mesin tapi belum
punya kontrol di UI.

Tambahkan toggle di toolbar `BudgetAnalysisPage`, aktif **hanya** saat `period`
ikut di `group_by` — di luar itu parameternya tidak berpengaruh dan toggle yang
tidak berefek lebih membingungkan daripada tidak ada.

| Nilai | Label | Teks bantu |
|---|---|---|
| `annual_row` | Tampilkan terpisah | Baris tahunan muncul sebagai "Tahunan (belum dialokasikan)" |
| `even` | Ratakan per bulan | Baris tahunan dibagi rata ke seluruh bulan periode |

Teks bantu wajib ada. `even` adalah **keputusan penyajian**, bukan fakta anggaran —
`BudgetAllocationResolver` sengaja tidak menjadikannya default. UI tidak boleh
menyembunyikan bahwa angka bulanan itu hasil pembagian, bukan yang dianggarkan.

---

## 4. View #13 & #14 — Revenue / Expense Budget

Filter `direction` sudah didukung backend. Tambahkan segmented control di toolbar:
**Semua | Pendapatan | Beban**.

Saat "Semua", baris campuran mengembalikan `direction: 'mixed'`. Tampilkan itu apa
adanya (badge "Campuran"), jangan dipaksa jadi salah satu — mesin sengaja menandai
ambiguitas alih-alih diam-diam memilih konvensi.

---

## 5. View #12 — Summary & Drill-down

`/budget/summary` sudah ada. Drill-down bukan endpoint terpisah: ia panggilan ulang
dengan `group_by` lebih panjang dan nilai baris induk sebagai filter.

Implementasi di `BudgetAnalysisPage`: klik baris → tambahkan dimensi berikutnya ke
`group_by` dan set filter dari baris itu. Urutan drill-down yang wajar:

```
(total) → department → project → account → period
```

Tampilkan jejaknya sebagai breadcrumb yang bisa diklik mundur. Karena setiap level
memakai mesin yang sama, angka induk selalu sama dengan jumlah anak **secara
konstruksi** — bukan karena dua query kebetulan cocok. Tidak perlu rekonsiliasi.

---

## Existing files affected

| File | Perubahan |
|---|---|
| `frontend/src/modules/budget/pages/BudgetAnalysisPage.tsx` | + preset dari URL, toggle allocation, segmented direction, kolom Sisa Anggaran, drill-down |
| `frontend/src/modules/budget/types/budget.types.ts` | + tipe preset |
| `frontend/src/modules/budget/hooks/useBudgetAnalysis.ts` | tidak berubah — parameternya sudah lengkap |

## New files

| File | Isi |
|---|---|
| `frontend/src/modules/budget/constants/analysisPresets.ts` | Peta `ANALYSIS_PRESETS` |

Halaman baru: **tidak ada**. Kalau fase ini menghasilkan halaman baru, desainnya
menyimpang dari aturan §3.2 fase 0.

---

## Risks

| Risiko | Mitigasi |
|---|---|
| `BudgetAnalysisPage` sudah 425 baris dan akan bertambah | Ekstrak toolbar jadi komponen sendiri bila melewati ~550 baris; jangan pecah jadi banyak halaman |
| Kolom "Sisa Anggaran" menyesatkan pada baris pendapatan | Hanya tampil saat `direction=expense` (§2) |
| Toggle `even` dibaca sebagai anggaran bulanan sungguhan | Teks bantu wajib + label kolom "Tahunan (belum dialokasikan)" tetap ada |
| Drill-down menumpuk `group_by` tanpa batas | Batasi ke urutan tetap 4 level; setelah `period` tidak ada lagi |

---

## Testing

Backend tidak berubah — tidak ada test PHP baru.

Verifikasi manual:

1. Empat URL preset mendarat dengan filter yang benar
2. Preset tak dikenal → default, tidak error
3. Setelah mount, mengubah filter tidak dipaksa balik oleh URL
4. Toggle allocation hanya aktif saat `group_by` memuat `period`
5. `even` membagi rata; totalnya identik dengan `annual_row`
6. `direction=expense` memunculkan kolom "Sisa Anggaran"; "Semua" tidak
7. Baris campuran menampilkan badge "Campuran"
8. Drill-down: total induk = jumlah baris anak di setiap level
9. Breadcrumb drill-down bisa mundur
10. `npm run build` 0 error, `rtk lint` bersih

---

## Acceptance criteria

- [ ] Empat entri Monitoring punya URL preset yang berfungsi
- [ ] View #3, #11, #12, #13, #14 terjangkau dari UI
- [ ] Tidak ada halaman atau endpoint baru
- [ ] Angka drill-down konsisten antar level
- [ ] `npm run build` 0 error

---

## Hasil implementasi — 2026-08-15

### Yang dibuat/diubah

| File | Perubahan |
|---|---|
| `constants/analysisPresets.ts` | **Baru** — 10 preset bertipe + `resolvePreset()` |
| `pages/BudgetAnalysisPage.tsx` | + preset dari URL, + kontrol `mode`, + sort serapan, + kolom "Sisa Anggaran", + badge "Campuran", allocation di-`disabled` di luar `group_by=period`, + wrapper `key` |

Halaman baru: **tidak ada**. Endpoint baru: **tidak ada**. Aturan §3.2 fase 0
bertahan.

### Penyimpangan

- **P7** — `mode` ternyata **tidak pernah** terekspos di UI. Tipenya sudah ada
  (`BudgetAnalysisParams.mode`) dan backend mendukungnya, tapi tidak ada kontrol
  dan `handleApply()` tidak pernah mengirimnya. Preset Variance tidak akan
  berfungsi tanpa itu, jadi kontrol `mode` ikut ditambahkan.
- **P5** — dibutuhkan wrapper `key={preset}`. Keempat entri Monitoring mendarat
  di rute yang sama dan hanya berbeda `?preset=`; React Router tidak me-remount
  saat query berubah, jadi berpindah Variance → Utilization akan mengubah URL
  tapi membiarkan filter milik preset sebelumnya.
- Sort serapan dilakukan **di klien**, bukan lewat parameter backend. Seluruh
  baris sudah di memori, dan `/budget/analysis` sengaja tidak punya opsi sort —
  menambahkannya berarti dua tempat memutuskan urutan. `null` (anggaran 0) selalu
  di bawah; ia bukan "serapan 0%".
- Drill-down, toggle allocation, filter arah, dan export CSV ternyata **sudah
  ada** sejak fase 7 rencana sebelumnya. Yang ditambahkan hanya yang benar-benar
  kurang.

### Verifikasi

`npm run build` 0 error · `rtk lint` bersih.

### Yang belum

10 langkah verifikasi manual.
