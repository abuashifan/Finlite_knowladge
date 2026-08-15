# Phase 5 — Halaman Project

**Sisi**: Frontend
**Prasyarat**: fase 1 (`ProjectFinancialBlocks` sudah diekstrak)
**Menutup**: view #15, #16, #17, #20

---

## Objective

Mewujudkan cabang `Project` dari tree ANGGARAN:

```
Project
├── Project Budget         → #15
├── Project Actual         → #16
├── Project Profitability  → #18 (ada)
├── Project Cash Flow      → #20
└── Project Transactions   → #21 (ada, tertanam)
```

Semua endpoint sudah ada. Yang dibangun hanya penyajian.

---

## 1. Satu halaman bertab, bukan lima halaman

Lima entri menu, tapi **empat dari lima memakai satu endpoint yang sama**
(`/budget/projects/{id}/summary`). Membuat lima halaman terpisah berarti lima kali
memilih proyek dan periode, lima kali fetch endpoint yang identik.

Struktur yang dipakai: `ProjectFinancialSummaryPage` diperluas jadi halaman bertab.
Pemilih proyek + periode ada satu kali di toolbar; tab bertukar tanpa fetch ulang.

```
┌─ Proyek: [Renovasi Kantor ▾]   Periode: [Anggaran 2026 ▾]  [Tampilkan] ─┐
│                                                                          │
│  [Anggaran] [Realisasi] [Profitabilitas] [Arus Kas] [Transaksi]         │
│  ─────────────────────────────────────────────────────────────────      │
│                                                                          │
│  ⚠ {meta.limitation}   ← selalu tampil, di semua tab                    │
│                                                                          │
│  (isi tab)                                                               │
└──────────────────────────────────────────────────────────────────────────┘
```

Setiap entri menu menautkan ke tab-nya lewat query string:

| Menu | URL |
|---|---|
| Project Budget | `/budget/projects?tab=budget` |
| Project Actual | `/budget/projects?tab=actual` |
| Project Profitability | `/budget/projects?tab=profitability` |
| Project Cash Flow | `/budget/projects?tab=cash-flow` |
| Project Transactions | `/budget/projects?tab=transactions` |

Pola yang sama dengan preset di fase 4: query string mengisi state awal, satu arah.

---

## 2. Isi tiap tab

### Tab Anggaran (#15)

Dari `summary.budget` + `summary.revenue_rows`/`cost_rows` sisi anggaran.
Blok Pendapatan / Biaya / Laba / Margin, lalu rincian per akun.

### Tab Realisasi (#16)

Dari `summary.actual` + sisi realisasi baris yang sama. Bentuk identik dengan tab
Anggaran — kesamaan bentuk itu disengaja, supaya mata bisa membandingkan.

### Tab Profitabilitas (#17 + #18 + #19)

Yang sekarang sudah ada: `FinancialBlock` Anggaran & Realisasi berdampingan, blok
Selisih, serapan biaya. Ini sudah view #17 dan #18 sekaligus; `margin_pct` menutup
#19.

Tidak ada yang perlu diubah selain memindahkannya ke dalam tab.

### Tab Arus Kas (#20)

Endpoint `/budget/projects/{id}/cash-flow` sudah ada dan hook
`useProjectCashFlow` **sudah ditulis tapi belum dipakai di mana pun**. Tab ini
tinggal memakainya.

Bentuknya sama dengan `CashBudgetPage` (Beginning + Inflow − Outflow = Ending,
plus rincian per `cash_flow_section`). Ekstrak penyajiannya dari `CashBudgetPage`
jadi komponen bersama:

```
frontend/src/modules/budget/components/CashBudgetView.tsx
```

dipakai `CashBudgetPage` dan tab ini. Jangan menyalin — aturan "dilarang buat
komponen baru jika sudah ada" berlaku dua arah.

**Asumsi akrual wajib tampil.** `meta.assumption` sudah dikembalikan backend dan
sudah ditampilkan `CashBudgetPage`. Komponen hasil ekstraksi harus membawanya,
bukan meninggalkannya di halaman lama.

### Tab Transaksi (#21)

Tabel yang sudah dibangun, dipindahkan ke tab ini. Tambahkan yang belum ada:

- Filter arah (Semua / Pendapatan / Beban) — parameter `direction` sudah didukung
- Filter akun (`SearchableSelect`) — parameter `account_id` sudah didukung
- Kolom Sumber (`source_number`) — sudah dikembalikan backend, belum ditampilkan

Peringatan `truncated` sudah ada; pertahankan.

---

## 3. Hubungan dengan halaman proyek (fase 1)

Tab "Anggaran" di `ProyekFormPage` menampilkan ringkasan yang sama. Tombol "Kelola
Anggaran" di sana menautkan ke halaman ini dengan proyek sudah terpilih:

```
/budget/projects?project_id={id}&tab=profitability
```

Berarti halaman ini harus menerima `project_id` dari query string juga, bukan hanya
dari pemilih. Perlakukan sama dengan `tab`: mengisi state awal saat mount.

---

## Existing files affected

| File | Perubahan |
|---|---|
| `frontend/src/modules/budget/pages/ProjectFinancialSummaryPage.tsx` | Jadi halaman bertab; tabel transaksi pindah ke tab |
| `frontend/src/modules/budget/pages/CashBudgetPage.tsx` | Pakai `CashBudgetView` hasil ekstraksi |
| `frontend/src/modules/budget/hooks/useProjectFinancials.ts` | Tidak berubah — ketiga hook sudah ada |

## New files

| File | Isi |
|---|---|
| `frontend/src/modules/budget/components/CashBudgetView.tsx` | Penyajian cash budget, dipakai 2 tempat |
| `frontend/src/modules/budget/components/ProjectTransactionsTable.tsx` | Tabel transaksi + filternya |

Halaman baru: **tidak ada**.

---

## Risks

| Risiko | Mitigasi |
|---|---|
| Lima tab dalam satu halaman jadi terlalu besar | Setiap tab satu komponen sendiri; halaman induk hanya toolbar + router tab |
| Ekstraksi `CashBudgetView` menghilangkan `meta.assumption` | Jadikan prop wajib (non-optional), bukan opsional — TypeScript yang menegakkan |
| Tab Anggaran & Realisasi terlihat duplikatif dengan Profitabilitas | Memang tumpang tindih; itu permintaan menu. Profitabilitas menyandingkan, dua tab lain memberi ruang untuk rincian per akun |
| `meta.limitation` hilang di tab selain Profitabilitas | Ditaruh di halaman induk, di luar tab — tampil di semua tab tanpa diulang |

---

## Testing

Backend tidak berubah — tidak ada test PHP baru.

Verifikasi manual:

1. Lima URL tab mendarat di tab yang benar
2. Berpindah tab tidak memicu fetch ulang endpoint `summary`
3. `?project_id=` mengisi pemilih proyek
4. Tab Arus Kas menampilkan angka yang sama dengan `/budget/cash?project_id=…`
5. `meta.assumption` tampil di tab Arus Kas
6. `meta.limitation` tampil di semua tab
7. Filter arah & akun di tab Transaksi mempersempit
8. Total transaksi cocok dengan `actual` di tab Realisasi
9. `CashBudgetPage` masih berperilaku sama setelah ekstraksi
10. `npm run build` 0 error, `rtk lint` bersih

---

## Acceptance criteria

- [ ] Lima entri menu Project punya tab yang berfungsi
- [ ] View #15, #16, #17, #20 terjangkau (#18, #19, #21 sudah)
- [ ] `useProjectCashFlow` akhirnya terpakai
- [ ] `meta.limitation` dan `meta.assumption` tampil di tempat yang tepat
- [ ] Tidak ada penyalinan komponen — `CashBudgetView` dipakai dua tempat
- [ ] `npm run build` 0 error

---

## Hasil implementasi — 2026-08-15

### Yang dibuat/diubah

| File | Perubahan |
|---|---|
| `pages/ProjectFinancialSummaryPage.tsx` | Jadi halaman 5 tab; `?tab=` & `?project_id=` mengisi state awal; wrapper `key` |
| `components/CashBudgetView.tsx` | **Baru** — hasil ekstraksi, dipakai 2 tempat |
| `components/ProjectTransactionsTable.tsx` | **Baru** — tabel + filter arah & akun + kolom Sumber |
| `pages/CashBudgetPage.tsx` | Ramping, pakai `CashBudgetView` |

`useProjectCashFlow` akhirnya terpakai — sebelumnya ditulis tapi tidak dipanggil
di mana pun.

### Penyimpangan

- **P5** — wrapper `key` juga dibutuhkan di sini, alasan sama seperti fase 4.
- Query arus kas hanya dijalankan saat tabnya aktif (`tab === 'cash-flow'`).
  Endpointnya berbeda dari `summary`, jadi memuatnya di muka jadi request yang
  sering tak terpakai.
- `CashBudgetView` menerima `cash` sebagai prop **non-optional** — supaya
  `meta.assumption` tidak bisa hilang tanpa disadari saat komponen dipakai ulang.
  TypeScript yang menegakkan, bukan disiplin.
- Tab Anggaran & Realisasi menampilkan rincian per akun dengan baris total
  sendiri, bukan hanya blok ringkas — kalau isinya persis sama dengan tab
  Profitabilitas, dua tab itu tidak punya alasan ada.

### Verifikasi

`npm run build` 0 error · `rtk lint` bersih.

### Yang belum

10 langkah verifikasi manual.
