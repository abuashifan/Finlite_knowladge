# Rencana Implementasi — Temuan Audit 12 Agustus 2026

> Dokumen perencanaan untuk item yang belum selesai atau butuh pembahasan lebih lanjut.
> Temuan #1–#7 dan #10 sudah selesai dikerjakan. Temuan #8, #9, dan backend #10 perlu perencanaan.

---

## Status Keseluruhan

| # | Temuan | Status | Butuh Pembahasan? |
|---|--------|--------|-------------------|
| 1 | Import gagal, tidak ada log error | ✅ Selesai | Tidak |
| 2 | Template jurnal hanya 1 baris debet | ✅ Selesai | Tidak |
| 3 | Form pengeluaran kas kurang compact | ✅ Selesai | Tidak |
| 4 | Jumlah harus input manual | ✅ Selesai | Tidak |
| 5 | Dropdown akun kas/bank tampilkan ID | ✅ Selesai | Tidak |
| 6 | Format angka tanpa pemisah ribuan | ✅ Selesai | Tidak |
| 7 | Label "Nama Periode" ambigu | ✅ Selesai | Tidak |
| **8** | **Realisasi anggaran dari pengeluaran kas** | ⚠️ Butuh implementasi | **Ya** |
| **9** | **Anggaran proyek (pendapatan + pengeluaran)** | ⚠️ Butuh implementasi | **Ya** |
| **10** | **Backend budget tab ProyekFormPage** | ⚠️ Sebagian (frontend sudah) | **Ya** |
| 11 | Portal pegawai pengajuan anggaran | ℹ️ Nanti | Tidak sekarang |

---

## 1. Temuan #8 — Realisasi Anggaran dari Pengeluaran Kas

### Masalah
Form input pengeluaran kas belum punya kolom untuk menghubungkan ke anggaran. Saat ini realisasi anggaran hanya bisa lewat jurnal umum (sudah ada budget warning di `JournalFormPage`).

### Yang Sudah Ada
- **Backend**: `JournalEntryService.createManual()` sudah memeriksa budget dan mengembalikan warning `BudgetWarning` jika realisasi melampaui anggaran.
- **Frontend**: `JournalFormPage` menampilkan toast warning untuk budget overruns.
- **Tabel budget**: `budget_periods`, `budget_submissions`, `budget_lines` (dengan `account_id`, `project_id`, `period`, `amount`).

### Yang Perlu Dibangun

#### A. Backend
1. **Migration**: Tambah kolom `budget_line_id` (nullable) ke tabel cash payment lines (`cash_payment_lines`) dan cash receipt lines.
2. **Model**: Tambah relasi `budgetLine()` di model `CashPaymentLine`.
3. **Service**: Di `CashPaymentService` (atau service baru), saat create/posting cash payment:
   - Cocokkan `account_id` + `project_id` + periode di `budget_lines`
   - Update `realized_amount` di `budget_lines`
   - Trigger warning jika realisasi > anggaran
4. **API**: Endpoint untuk mencari budget lines yang tersedia (per `account_id` + `project_id` + periode aktif).

#### B. Frontend
1. **CashPaymentFormPage**: Tambah kolom "Anggaran" di `LineItemsTable` — dropdown `SearchableSelect` untuk memilih budget line.
2. **Budget selector**: SearchableSelect mencari budget lines berdasarkan akun yang sudah dipilih + proyek + periode.
3. **Real-time check**: Tampilkan sisa anggaran setelah baris diisi.

#### C. Alternatif Desain (Perlu Keputusan)
| Opsi | Deskripsi | Pro | Kontra |
|------|-----------|-----|--------|
| **A** | User pilih budget line manual per baris | Kontrol penuh | Beban input bertambah |
| **B** | Auto-match: akun + proyek + periode otomatis cocokkan ke budget line terdekat | Tanpa input tambahan | Bisa salah cocok |
| **C** | Hybrid: auto-match dengan opsi override manual | Fleksibel | Implementasi lebih kompleks |

**Rekomendasi**: Opsi C — auto-match sebagai default, user bisa override.

---

## 2. Temuan #9 — Anggaran Proyek (Pendapatan + Pengeluaran)

### Masalah
Saat ini hanya ada anggaran pengeluaran (expense budget). Untuk proyek, perlu ada anggaran pendapatan (revenue) juga. Contoh: proyek event punya pendapatan tiket dan pengeluaran operasional.

### Yang Sudah Ada
- `budget_lines` punya `account_id` + `project_id` — artinya budget per proyek SUDAH didukung di level database.
- `budget_submissions` punya relasi ke `budget_period`.

### Yang Perlu Dibangun

#### A. Backend
1. **Migration**: Tambah kolom `type` (`revenue` / `expense`) ke `budget_lines`, atau buat dua submission terpisah.
   - **Opsi 1**: Kolom `type` di `budget_lines` — satu submission bisa campur revenue + expense.
   - **Opsi 2**: Dua `budget_submissions` terpisah — satu untuk revenue, satu untuk expense.
   - **Rekomendasi**: Opsi 1 — lebih sederhana, satu submission per proyek.

2. **Service**: Update `BudgetService` untuk:
   - Menerima `type` di setiap budget line
   - Validasi: revenue line pakai akun pendapatan (type COA `revenue`), expense line pakai akun biaya (type COA `expense`)
   - Tracking realisasi per line

3. **API**: Endpoint budget project:
   - `POST /budget/projects/{project_id}/submissions` — buat submission budget proyek
   - `GET /budget/projects/{project_id}/submissions` — list submission
   - Realisasi: match transaksi ke budget line via `account_id` + `project_id` + periode

#### B. Frontend
1. **ProyekFormPage tab Anggaran** — SUDAH dibuat dengan:
   - Line items: Jenis (Pendapatan/Pengeluaran), Akun, Periode, Jumlah, Catatan
   - Ringkasan: Total Pendapatan, Total Pengeluaran, Surplus/Defisit
   - Yang kurang: wiring ke backend API + load/save data budget

2. **BudgetPeriodDetailPage** — tampilkan tab/section untuk budget proyek.

---

## 3. Temuan #10 (Lanjutan) — Backend Budget Tab ProyekFormPage

### Yang Sudah Ada (Frontend)
- `ProyekFormPage.tsx` — form page penuh dengan tabs **Detail** + **Anggaran**
- Tab Anggaran: `LineItemsTable` untuk input baris budget (jenis, akun, periode, jumlah, catatan)
- Ringkasan total pendapatan, pengeluaran, surplus/defisit
- Routes: `/master-data/projects/create` dan `/master-data/projects/:id`
- `ProyekPage.tsx` — navigasi ke form page (bukan modal)

### Yang Perlu Dibangun (Backend)

1. **API endpoint budget project**:
   ```
   GET    /api/budget/projects/{project}/lines          — ambil semua budget lines proyek
   POST   /api/budget/projects/{project}/lines          — simpan/update budget lines proyek
   DELETE /api/budget/projects/{project}/lines/{id}     — hapus satu budget line
   ```

2. **Controller**: `ProjectBudgetController` atau extend `BudgetController` yang sudah ada.

3. **Service**: `ProjectBudgetService`:
   - Simpan/update array budget lines dalam satu transaksi
   - Validasi: akun harus aktif, period format valid
   - Hitung total revenue, expense, surplus

4. **Frontend wiring**:
   - Hook `useProjectBudget(projectId)` untuk load/save budget lines
   - `budgetApi` service — method baru untuk project budget
   - `ProyekFormPage` — load existing budget data, save on submit

---

## Prioritas & Urutan Implementasi

```
Phase A: Budget Project Backend (2-3 hari)
  ├── A1. Migration: tambah type ke budget_lines
  ├── A2. ProjectBudgetService + Controller
  ├── A3. API endpoint CRUD budget project
  └── A4. Backend test

Phase B: Budget Project Frontend (1-2 hari)
  ├── B1. Hook useProjectBudget + budgetApi method
  ├── B2. Wiring ProyekFormPage tab Anggaran
  └── B3. BudgetPeriodDetailPage tampilkan budget proyek

Phase C: Realisasi Budget dari Cash Payment (2-3 hari)
  ├── C1. Migration: budget_line_id ke cash_payment_lines
  ├── C2. Auto-match service + budget realization tracking
  ├── C3. Frontend: budget selector di CashPaymentFormPage
  └── C4. Integration test cash payment → budget realization
```

---

## Pertanyaan yang Perlu Diputuskan

1. **Budget line type**: Kolom `type` (revenue/expense) di `budget_lines` vs dua submission terpisah?
2. **Realisasi**: Auto-match (akun + proyek + periode) atau user pilih manual?
3. **Multiple budget period**: Apakah satu proyek bisa punya budget di beberapa periode berbeda?
4. **Approval workflow**: Apakah budget proyek perlu approval sebelum aktif?
5. **Portal pegawai (#11)**: Timeline untuk fitur pengajuan budget lewat portal?

---

## Catatan Teknis

- Semua perubahan backend wajib melalui migration, bukan edit database langsung.
- Test backend wajib untuk happy path + failure path.
- `npm run build` wajib 0 error sebelum selesai.
- Update `docs/struktur_frontend.md` jika ada file baru.
- Commit format: `feat(budget): ...` / `feat(cash-bank): ...` / `feat(projects): ...`

---

_Dibuat: 12 Agustus 2026 — Menunggu pembahasan sebelum implementasi._
