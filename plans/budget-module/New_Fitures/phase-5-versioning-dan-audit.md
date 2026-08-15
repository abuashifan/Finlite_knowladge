# Phase 5 — Versioning & Audit Trail

> Prasyarat: fase 1 selesai.

## Objective

Revisi anggaran yang **menjaga riwayat**, plus jejak audit yang selama ini tidak ada sama sekali.

Menutup **G2** (sisi perilaku; sisi skema sudah di fase 1) dan **G12**.

---

## Model versi

| Konsep (dari brief) | Realisasi |
|---|---|
| Original Budget | `version_no = 1` |
| Revised Budget | `version_no ≥ 2`, `parent_submission_id` menunjuk pendahulu |
| Current Active Budget | `is_active = true` — tepat satu per (period, department) |
| Revision History | seluruh baris sekelompok, terurut `version_no` |
| Revision Reason | `revision_reason`, **wajib** saat revisi |
| Created By / Created At | `created_by`, `created_at` (sudah ada) |
| Approval Status | rantai `submitted → approved_by_head → approved` (sudah ada) |
| Effective Period | mewarisi `period_from`/`period_to` dari `budget_periods` |
| Relationship dengan transactions | **tidak ada** — lihat di bawah |

Contoh dari brief terwakili langsung: v1 = 15 jt, v2 = 18 jt, v3 = 20 jt. Ketiganya tetap
terbaca; hanya v3 yang `is_active`.

---

## Apakah approved budget immutable?

**Ya.** `assertEditable()` sudah menolak edit di luar status `draft`/`rejected`, dan aturan itu
dipertahankan apa adanya.

Mengubah anggaran yang sudah disetujui hanya bisa lewat `POST /budget-submissions/{id}/revise`:

1. Salin header + **seluruh** `budget_lines` ke baris baru, `version_no + 1`, status `draft`,
   `parent_submission_id` = id lama, `revision_reason` diisi
2. Versi lama → `status = 'superseded'`, `is_active = false`
3. Versi baru melewati rantai persetujuan yang **sama**; saat mencapai `approved` →
   `is_active = true`

Semuanya dalam satu `DB::transaction`.

### Reject ≠ Revise

**Reject tetap seperti sekarang** — kembali ke `draft`, `revision_number + 1`, di baris yang
sama, approval stamp dikosongkan. Itu koreksi **sebelum** disetujui, bukan revisi anggaran.
Perilaku ini sudah teruji di `test_reject_returns_to_draft_and_increments_revision`;
**jangan diubah**.

Ringkasnya, dua penghitung dengan peran berbeda:

| Kolom | Menghitung |
|---|---|
| `revision_number` | Berapa kali pengajuan ini ditolak sebelum disetujui |
| `version_no` | Versi anggaran keberapa — v1 asli, v2+ hasil revisi setelah approved |

Perbedaan ini **wajib** ditulis di `app/Modules/Budget/README.md`, kalau tidak akan
membingungkan pembaca berikutnya.

---

## Hubungan dengan transaksi

Baris anggaran **tidak pernah** ditunjuk oleh transaksi. Actual selalu dihitung ulang dari
ledger, jadi merevisi anggaran tidak pernah merusak data historis dan tidak butuh migrasi
apa pun.

Laporan default memakai **versi aktif** (`version=active`). `version=all` menampilkan Original
vs Revised berdampingan — berguna untuk menjawab "kenapa anggarannya naik?".
`version={id}` mengunci ke satu versi tertentu.

---

## Audit trail (G12)

Modul Budget saat ini **tidak menulis satu pun** entri audit, padahal seluruh modul transaksi
lain melakukannya.

Pola yang diikuti (dari `JournalEntryService.php:427-448`):

- `AuditLogService` disuntik sebagai **argumen konstruktor nullable terakhir**:
  `private readonly ?AuditLogService $auditLogService = null`
- Private helper `audit(string $event, Model $m, ?int $userId, array $meta = [])` di tiap service
- Target tenant (`tenant: true`) → `tenant_audit_logs`
- Kegagalan audit tidak pernah merusak request (sudah di-try/catch di dalam logger)

Jalur tulis yang wajib mencatat:

| Aksi | Event |
|---|---|
| Buat / ubah periode | `budget.period.created` / `.updated` |
| Tutup periode | `budget.period.closed` |
| Buat / ubah pengajuan | `budget.submission.created` / `.updated` |
| Simpan baris | `budget.submission.lines_updated` |
| Ajukan | `budget.submission.submitted` |
| Setujui kepala | `budget.submission.approved_head` |
| Setujui finance | `budget.submission.approved` |
| Tolak | `budget.submission.rejected` |
| Revisi | `budget.submission.revised` |

Konstanta ditambahkan ke `App\Shared\Audit\AuditEvent`. `metadata` menyertakan
`version_no`, `revision_reason`, dan total nominal supaya perubahan angka terlacak.

---

## Database changes

Tidak ada — semuanya sudah dipasang di fase 1 (`parent_submission_id`, `version_no`,
`is_active`, `revision_reason`, status `superseded`).

---

## New files

- `app/Modules/Budget/Services/BudgetRevisionService.php`
- `app/Modules/Budget/Requests/ReviseBudgetSubmissionRequest.php` — `revision_reason` wajib,
  min 10 karakter
- `app/Modules/Budget/README.md` — menjelaskan perbedaan `revision_number` vs `version_no`

---

## Existing files affected

| File | Perubahan |
|---|---|
| `Services/BudgetSubmissionService.php` | + `AuditLogService` nullable; + panggilan audit di setiap jalur tulis; `approveFinance()` menyetel `is_active = true` dan menonaktifkan versi lain |
| `Services/BudgetPeriodService.php` | + `AuditLogService` nullable + panggilan audit |
| `Controllers/BudgetSubmissionController.php` | + `versions()`, `revise()` |
| `Routes/api.php` | + 2 route |
| `config/permissions.php` | + `budgets.revise` (detail lengkap di fase 6) |
| `App\Shared\Audit\AuditEvent` | + 9 konstanta |

---

## API / service changes

| Method | Path | Permission |
|---|---|---|
| GET | `/budget-submissions/{id}/versions` | `budgets.view` |
| POST | `/budget-submissions/{id}/revise` | `budgets.revise` |

`GET .../versions` mengembalikan seluruh rantai versi (naik lewat `parent_submission_id`
sampai akar, lalu turun) dengan ringkasan total nominal per versi — cukup untuk halaman
riwayat tanpa memuat semua baris.

`ApiErrorCode` baru: `BUDGET_ALREADY_APPROVED` (revisi pada versi non-approved),
`BUDGET_VERSION_NOT_ACTIVE`. Daftarkan di class **dan** `config/api_errors.php`.

---

## Frontend changes

Tidak ada di fase ini; halaman riwayat versi ada di fase 7.

---

## Dependencies

Fase 1.

---

## Risks

| Risiko | Mitigasi |
|---|---|
| Dua penghitung mirip (`revision_number` vs `version_no`) membingungkan | Didokumentasikan di `app/Modules/Budget/README.md` dan di label UI: "Revisi ke-N" vs "Versi N". |
| Lebih dari satu `is_active = true` karena race condition | `approveFinance()` menonaktifkan versi lain **di dalam** `DB::transaction` yang sama, dengan `lockForUpdate()` pada grup versi. |
| Revisi menyalin ratusan baris jadi lambat | Salin lewat satu `INSERT ... SELECT` atau bulk `insert()`, bukan loop `create()` per baris — pola sama dengan `updateLines()`. |
| Audit log membanjiri `tenant_audit_logs` | Hanya jalur tulis yang dicatat, bukan pembacaan. Volume anggaran jauh lebih kecil dari transaksi. |

---

## Testing

`tests/Feature/Budget/BudgetVersioningTest.php`:

- v1 approved → revise → v2 draft, v1 `superseded` dan `is_active = false`
- Baris v1 **masih terbaca** setelah revisi, nominalnya tidak berubah
- v2 approved → `is_active = true`, dan hanya satu yang aktif dalam grup
- Revise pada versi berstatus `draft` → 422 `BUDGET_ALREADY_APPROVED`
- Revise tanpa `revision_reason` → 422 validasi
- Revise tanpa permission `budgets.revise` → 403
- Edit langsung pada versi `approved` → tetap 422 (immutability terjaga)
- Reject tetap berperilaku lama: `draft`, `revision_number + 1`, di baris yang sama
- `GET /versions` mengembalikan rantai terurut dengan total per versi
- Audit log tertulis untuk setiap aksi, dengan `version_no` di metadata

```bash
cd /workspace/laravel_backend
vendor/bin/pint --test
php artisan test tests/Feature/Budget
```

---

## Hasil implementasi — 2026-08-14

Status: **selesai**.

`BudgetRevisionService` (revise + versions), `ReviseBudgetSubmissionRequest`
(`revision_reason` wajib min 10 karakter), 2 route baru, 11 konstanta `AuditEvent`, dan
panggilan audit di seluruh jalur tulis `BudgetPeriodService` + `BudgetSubmissionService`.

`markActiveVersion()` sudah dipasang lebih awal di fase 1 (mesin fase 2 butuh
`version=active`); fase ini menambah `lockForUpdate()` pada grup versi di dalam transaksi
revisi, sesuai mitigasi race condition di §Risks.

### Penyimpangan penting — audit trail

Rencana menyuruh menyuntik `AuditLogService` sebagai **argumen konstruktor nullable terakhir**
mengikuti `JournalEntryService`. **Pola itu tidak bekerja.** Container Laravel mengisi parameter
bernilai default dengan default-nya, sehingga `$this->auditLogService` selalu `null` dan
`audit()` langsung `return` — diverifikasi lewat refleksi, bukan dugaan.

Modul Budget karenanya memakai pola `FixedAssetService`/`PeriodEndService`: dependensi
**wajib**, tanpa nilai default. Test `test_every_write_leaves_an_audit_entry` gagal dengan pola
lama dan lulus dengan pola baru.

> ⚠️ Konsekuensinya di luar modul ini: `JournalEntryService`, `CashPaymentService`,
> `CashReceiptService`, dan `BankTransferService` memakai pola nullable yang sama, jadi
> **audit trail keempatnya kemungkinan besar tidak pernah menulis**. Belum diperbaiki —
> di luar cakupan rencana ini.

### Verifikasi

`tests/Feature/Budget/BudgetVersioningTest.php` — 10 test, mencakup seluruh daftar di §Testing:
v1→v2 supersede · baris v1 utuh setelah revisi · v2 approved jadi satu-satunya aktif ·
rantai v1/v2/v3 terbaca dengan total masing-masing (15jt/18jt/20jt persis contoh brief) ·
revise pada draft → 422 `BUDGET_ALREADY_APPROVED` · alasan revisi wajib & min 10 karakter ·
403 tanpa `budgets.revise` · approved tetap tidak bisa diedit langsung · **reject tetap
berperilaku persis seperti sebelumnya** · audit log tertulis dengan `version_no` di metadata.

---

## Acceptance criteria

1. Versi 1 (15 jt) → 2 (18 jt) → 3 (20 jt): ketiganya terbaca, hanya v3 aktif.
2. Anggaran yang sudah approved tidak bisa diedit langsung — hanya lewat `revise`.
3. Tepat satu `is_active` per (period, department) di setiap keadaan.
4. Reject tetap berperilaku persis seperti sebelum fase ini.
5. Setiap aksi tulis di modul Budget meninggalkan entri di `tenant_audit_logs`.
