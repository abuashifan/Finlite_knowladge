# Phase 0.1 — Satukan Semua Form Baris-Item ke `LineItemsTable`

> Prasyarat: `phase-0-context-rules-guardrails.md`.
> **Dikerjakan sebelum** `phase-7-frontend.md` (Budget) dan sebelum P1 di
> `project-dimension-budgeting-readiness-plan.md` (Project selector) — keduanya menambah kolom
> baru ke tabel baris transaksi, jadi basisnya harus konsisten dulu.

## Objective

Permintaan pemilik produk: *"rapih seperti form penerimaan lainnya"* — semua form baris-item
(line items) di frontend memakai satu komponen tabel yang sama
(`frontend/src/components/shared/form/LineItemsTable.tsx`, compact table view: header abu
`bg-[#eeeeee]`, sel `px-2.5 py-2`, input `h-8 text-[12px]`), bukan campuran tabel manual di
sana-sini.

Audit menemukan **17 dari 18 form transaksi sudah konsisten** memakai `LineItemsTable`
(termasuk `GoodsReceiptFormPage.tsx`, "form penerimaan" yang jadi acuan). Yang tersisa adalah
**4 form dengan tabel manual yang layak dimigrasi**, dan **2 form + 1 komponen laporan yang
sengaja TIDAK dimigrasi** karena beda konteks interaksi (dijelaskan di bawah, supaya tidak ada
yang "sekalian saja" dipaksa migrasi tanpa alasan).

Dokumen ini **tidak membuat komponen baru** — memperluas `LineItemsTable` yang sudah ada
seperlunya, lalu memindahkan pemakai manual ke sana. Sesuai guardrail "jangan bikin komponen
UI baru bila sudah ada yang bisa dipakai ulang".

---

## Ringkasan audit

| Form/Komponen | Modul | Status sekarang | Baris tabel manual |
|---|---|---|---|
| 17 form (Sales Invoice, Vendor Bill, Cash Payment, Cash Receipt, Stock Adjustment, Stock Movement, Journal, Goods Receipt, Quotation, Proforma, Delivery Order, Sales Order, Sales Return, Purchase Order, Purchase Return, Purchase Request, ProyekFormPage) | berbagai | ✅ Sudah pakai `LineItemsTable` | — |
| `BudgetLineEditor.tsx` | Budget | ❌ Manual (disengaja, ada komentar di file) | ~129 baris |
| `OpeningBalanceBatchPage.tsx` | Opening Balance | ❌ Manual | ~39 baris (+16 picker) |
| `VendorPaymentFormPage.tsx` | Purchase | ❌ Manual | ~43 baris |
| `SalesReceiptFormPage.tsx` | Sales | ❌ Manual (tapi styling **sudah identik** dengan `LineItemsTable`) | ~73 baris |
| `StockOpnameFormPage.tsx` | Inventory | ⚠️ Manual — **TIDAK dimigrasi** | ~73 baris |
| `BankReconciliationFormPage.tsx` | Cash & Bank | ⚠️ Manual — **TIDAK dimigrasi** | ~33 baris |
| `BudgetConsolidationTable.tsx` | Budget | ⚠️ Manual — **TIDAK dimigrasi** (bukan form) | n/a |

### Kenapa 3 yang terakhir TIDAK dimigrasi

- **`StockOpnameFormPage.tsx`** — bukan pola tambah/hapus baris bebas. Baris di-generate tetap
  dari stok gudang, dan disimpan **per-baris individual** (tombol "Simpan" per baris), bukan
  simpan-semua-sekaligus seperti `LineItemsTable`. Memaksakan migrasi berarti mendesain ulang
  pola interaksinya, bukan sekadar mengganti komponen — di luar cakupan "rapikan komponen",
  masuk kategori "ubah UX", butuh keputusan produk terpisah.
- **`BankReconciliationFormPage.tsx`** — bukan tabel input nilai per sel. Ini tabel
  pilih-checkbox untuk transisi status (cleared/uncleared) di atas data read-only. Tidak ada
  `onUpdate` per sel yang analog dengan `LineItemsTable`.
- **`BudgetConsolidationTable.tsx`** — laporan read-only (rowSpan grouping + grand total), bukan
  form input sama sekali. `LineItemsTable` didesain untuk form, bukan laporan.

Memaksakan ketiganya ke `LineItemsTable` akan melanggar guardrail "jangan over-engineer" —
komponennya akan dipenuhi cabang kondisional untuk pola interaksi yang sama sekali berbeda.

---

## Gap kapabilitas `LineItemsTable` (dari audit `LineItemsTable.tsx`, 218 baris)

| # | Gap | Dibutuhkan oleh |
|---|---|---|
| G1 | Tidak ada footer/summary row custom (`<tfoot>` Total) — hanya subtotal per baris | `BudgetLineEditor` (Total Nominal), `OpeningBalanceBatchPage` (Total Debit/Kredit/Selisih), `VendorPaymentFormPage` (Total Dibayar) |
| G2 | `onAdd: () => void` mengasumsikan tombol "+ Tambah Item" polos menambah baris kosong — tidak mengakomodasi pola "tambah baris dari hasil pilih `SearchableSelect` eksternal" (baris datang dengan data terisi, bukan kosong) | `OpeningBalanceBatchPage`, `VendorPaymentFormPage`, `SalesReceiptFormPage` |
| G3 | Validasi client-side per sel (bukan dari backend) belum ada mekanisme resmi | `BudgetLineEditor` (format Periode `YYYY-MM`) |

**Yang TERNYATA bukan gap** (dari audit, supaya tidak salah desain): `render` per kolom sudah
bebas merender apa saja termasuk beberapa `SearchableSelect` sekaligus dalam satu baris — jadi
kasus `BudgetLineEditor` (kolom Akun + Proyek, dua `SearchableSelect`) **sudah bisa** dipetakan
langsung ke `LineItemColumn[]` tanpa perubahan komponen. G3 juga **tidak perlu fitur baru** di
komponen — `LineItemsTable` sudah menerima prop `errors: LineItemErrorMap` yang dirender per
baris/sel; validasi client-side cukup dihitung di level pemanggil dan digabung ke bentuk
`LineItemErrorMap` yang sama, bukan jalur terpisah. Jadi G3 turun jadi pola pemakaian, bukan
perubahan komponen.

---

## Existing files affected

| File | Perubahan |
|---|---|
| `frontend/src/components/shared/form/LineItemsTable.tsx` | **G1**: tambah prop opsional `footer?: (items: T[]) => ReactNode` — dirender sebagai `<tfoot>` di bawah baris terakhir, konsisten dengan filosofi komponen ("render callback bebas", sama seperti `column.render`), bukan menambah state/logic baru ke komponen. **G2**: `onAdd` diubah jadi opsional (`onAdd?: () => void`); saat tidak diisi, tombol "+ Tambah Item" bawaan tidak dirender — pemanggil bebas menaruh `SearchableSelect` sendiri di atas `<LineItemsTable>` dan memanggil `onUpdate`/state-nya sendiri untuk menambah baris berisi data |
| `frontend/src/modules/budget/components/BudgetLineEditor.tsx` | Pindah ke `LineItemsTable` + `footer` (Total Nominal) + `columns` untuk Akun/Proyek/Periode/Nominal. Validasi format Periode dihitung client-side, digabung ke `errors` prop dalam bentuk `LineItemErrorMap` yang sama dengan error backend. Hapus komentar baris 91-95 yang menjelaskan alasan deviasi (sudah tidak berlaku) |
| `frontend/src/modules/opening-balance/pages/OpeningBalanceBatchPage.tsx` | Pindah ke `LineItemsTable` + `footer` (Total Debit/Kredit/Selisih). Tambah-baris via `SearchableSelect` eksternal tetap dipertahankan (letakkan di atas `<LineItemsTable onAdd={undefined} .../>`) |
| `frontend/src/modules/purchase/pages/VendorPaymentFormPage.tsx` | Pindah ke `LineItemsTable` + `footer` (Total Dibayar). Pola tambah-baris via `SearchableSelect` eksternal sama seperti di atas |
| `frontend/src/modules/sales/pages/SalesReceiptFormPage.tsx` | Pindah ke `LineItemsTable` — migrasi **paling ringan**, styling sudah identik, tinggal ganti markup `<table>` manual dengan `<LineItemsTable columns={...} items={...} .../>` dan pola tambah-baris via tombol chip invoice tetap dipertahankan lewat `onAdd` opsional |

---

## New files

Tidak ada. Semua perubahan di file existing.

---

## Database changes

Tidak ada — ini murni perubahan komponen React.

## API / service changes

Tidak ada.

## Frontend changes

Sudah dirinci di §"Existing files affected" di atas.

---

## Dependencies

`phase-0-context-rules-guardrails.md`. Fase ini sendiri **mem-block**:
- `phase-7-frontend.md` (Budget) — halaman baru di fase 7 (`BudgetAnalysisPage`,
  `BudgetVersionHistoryPage`, dst.) tidak bersinggungan langsung dengan `LineItemsTable`, tapi
  `BudgetLineEditor.tsx` yang dipakai `BudgetSubmissionPage`/`BudgetPeriodDetailPage` sebaiknya
  sudah konsisten dulu sebelum fase 7 menambah fitur di atasnya.
- P1 di `project-dimension-budgeting-readiness-plan.md` — menambah kolom Project ke 7 form
  transaksi. Kolom baru itu ditambahkan ke `columns` array `LineItemsTable` yang sudah ada di
  form-form tersebut; **tidak bergantung** pada migrasi 4 form manual di dokumen ini (form-form
  manual bukan target Project selector). Fase ini tetap dikerjakan lebih dulu semata untuk
  merapikan basis komponen sesuai permintaan eksplisit pemilik produk, bukan karena blocking
  teknis ke P1.

---

## Risks

| Risiko | Mitigasi |
|---|---|
| `footer` prop baru mengubah struktur `<table>` (nambah `<tfoot>`) — berpotensi memengaruhi 17 pemakai existing yang tidak memakai prop ini | Prop opsional, default `undefined` → tidak ada `<tfoot>` dirender sama sekali kalau tidak diisi. 17 form existing nol perubahan visual |
| `onAdd` jadi opsional — TypeScript akan menandai pemanggilan lama yang selalu mengisi `onAdd` sebagai tetap valid, tapi perlu dipastikan tidak ada pemanggil yang secara tidak sengaja lupa mengisi lalu kehilangan tombol tambah | `npm run build` akan menangkap penghapusan tak sengaja hanya kalau ada type error terkait, jadi wajib **verifikasi visual manual** ke 17 form existing setelah perubahan, bukan cuma type-check |
| Migrasi `BudgetLineEditor` mengubah validasi format Periode dari pesan inline khusus (baris 162-164 lama) ke jalur `errors` prop bersama — bentuk pesannya harus tetap sejelas sebelumnya | Bandingkan screenshot sebelum/sesudah; test manual submit dengan Periode invalid |
| `SalesReceiptFormPage`/`VendorPaymentFormPage`/`OpeningBalanceBatchPage` — pola "tambah baris dari hasil pilih SearchableSelect eksternal" harus tetap mencegah invoice/bill/akun yang sama dipilih dua kali | Pertahankan logika dedup yang sudah ada di masing-masing file (filter opsi yang sudah dipakai), pindahkan apa adanya, jangan tulis ulang |
| Menyentuh 4 form transaksi sekaligus | Migrasi satu file per commit/PR, regresi manual per form sebelum lanjut ke form berikutnya — jangan migrasi serentak |

---

## Testing

Tidak ada test runner otomatis untuk frontend di repo ini (konsisten dengan fase 7). Verifikasi:

```bash
cd /workspace/frontend
npm run build
npm run lint
```

Manual, per form yang dimigrasi:
1. Tambah baris, isi semua kolom, submit — data tersimpan identik dengan sebelum migrasi
2. Hapus baris — baris lain tidak berubah urutan/datanya
3. Footer Total menghitung benar setelah tambah/hapus/edit baris
4. Error dari backend (422) tetap muncul di baris/sel yang benar
5. Mode read-only (dokumen sudah bukan draft) — semua sel jadi non-editable, tombol tambah/hapus hilang
6. **Regresi 17 form existing** — buka masing-masing sekali, pastikan tampilan & fungsi tidak berubah sama sekali (prop baru harus 100% backward-compatible)

---

## Hasil implementasi — 2026-08-14

Dikerjakan bersama fase 0. Status: **selesai secara kode**, verifikasi visual manual belum.

### Yang berubah

| File | Hasil |
|---|---|
| `components/shared/form/LineItemsTable.tsx` | `onAdd` jadi opsional (tombol "+ Tambah Item" hanya dirender bila diisi **dan** tidak read-only); prop `footer` baru dirender sebagai `<tfoot className="border-t border-[#d9e2e5] bg-[#f8fafc]">`. `colSpan` empty-state dirapikan memakai `columnCount` yang sudah ada (sebelumnya ekspresi yang sama ditulis dua kali) |
| `modules/budget/components/BudgetLineEditor.tsx` | Pindah ke `LineItemsTable` (kolom Akun/Proyek/Periode/Nominal) + `footer` Total. Komentar deviasi baris 91-95 dihapus. `_key`/`nextKey` dibuang — identitas baris kini indeks, sama seperti 17 form lain |
| `modules/opening-balance/pages/OpeningBalanceBatchPage.tsx` | Pindah ke `LineItemsTable` tanpa `onAdd`; kotak total terpisah di bawah tabel diganti dua baris `<tfoot>` (Total Debit/Kredit, lalu Selisih dengan pewarnaan hijau/merah yang sama) |
| `modules/purchase/pages/VendorPaymentFormPage.tsx` | Pindah ke `LineItemsTable` tanpa `onAdd` + `footer` Total Dibayar. `footer` sengaja `undefined` saat 0 baris supaya perilakunya identik dengan `tfoot` lama yang hanya muncul bila ada baris |
| `modules/sales/pages/SalesReceiptFormPage.tsx` | Pindah ke `LineItemsTable` tanpa `onAdd`. Blok chip "Invoice terbuka" pindah ke kotak sendiri **di bawah** tabel (dulu di dalam container tabel manual, sekarang container itu milik komponen) |

### Deviasi dari rencana

1. **Path `OpeningBalanceBatchPage.tsx`** — rencana menyebut `modules/accounting/pages/`; lokasi
   sebenarnya `modules/opening-balance/pages/`. Sudah dikoreksi di dokumen ini.
2. **Signature `footer`** — rencana menulis `footer?: (items: T[]) => ReactNode`. Yang dipakai
   `footer?: (items: T[], cellCount: number) => React.ReactNode`. Argumen kedua adalah jumlah sel
   per baris (kolom `#` + kolom data + Subtotal bila ada + kolom aksi); tanpa itu setiap pemanggil
   harus menebak `colSpan` dari jumlah kolom internal komponen. Ini superset — callback yang
   ditulis sesuai signature lama tetap type-check.
3. **G3 tidak menambah fitur komponen**, sesuai temuan audit: validasi format Periode dihitung di
   `BudgetLineEditor` lalu digabung ke `errors` (`LineItemErrorMap`) yang sama dengan error 422.
   Sekalian: error backend kini benar-benar dipetakan ke barisnya lewat `getApiLineErrors` —
   indeksnya diremap karena payload membuang baris tanpa akun, jadi pesan "baris ke-N" backend
   tidak menempel di baris yang salah.

### Verifikasi yang sudah dijalankan

```
npm run build   → ✅ 0 error (script = `tsc -b && vite build`)
npm run lint    → ✅ 0 error, 0 warning
```

Backward-compatibility 17 form lama dicek statis: seluruhnya masih mengoper `onAdd` dan tidak ada
satu pun yang mengoper `footer`, sehingga `<tfoot>` tidak dirender dan tombol tambah tetap ada —
nol perubahan markup.

### Belum dijalankan — sisa untuk pemilik produk

- **Regresi visual manual 17 form existing** (§Testing poin 6) dan uji manual poin 1–5 per form
  yang dimigrasi. Butuh backend hidup; belum dilakukan.
- Tidak ada test runner otomatis frontend di repo ini, jadi tidak ada test baru yang bisa ditulis.

---

## Acceptance criteria

1. `BudgetLineEditor.tsx`, `OpeningBalanceBatchPage.tsx`, `VendorPaymentFormPage.tsx`,
   `SalesReceiptFormPage.tsx` memakai `LineItemsTable`, bukan tabel manual.
2. `StockOpnameFormPage.tsx`, `BankReconciliationFormPage.tsx`, `BudgetConsolidationTable.tsx`
   **sengaja tidak diubah** — dicatat di dokumen ini alasannya, tidak "kelupaan".
3. Tidak ada komponen tabel baru dibuat — hanya `LineItemsTable` yang diperluas.
4. Ke-17 form yang sudah memakai `LineItemsTable` sebelumnya **tidak berubah** tampilan/perilaku
   sama sekali (prop baru sepenuhnya opsional & backward-compatible).
5. `npm run build` dan `npm run lint` hijau, nol error.
6. Semua form yang dimigrasi mempertahankan fitur yang ada sekarang (footer total, dedup pilihan,
   validasi format) — tidak ada capability yang hilang saat pindah komponen.
