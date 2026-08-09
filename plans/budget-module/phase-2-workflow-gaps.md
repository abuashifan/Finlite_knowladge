# Fase 2 — Lubang alur kerja

**Tujuan:** membuat siklus lengkap (buat pengajuan → isi baris → ajukan →
setujui/tolak → revisi) benar-benar bisa dijalani dari UI.

Tiga cacat terpisah, urutannya tidak mengikat.

---

## 2.1 Tidak ada UI untuk membuat pengajuan

`BudgetPeriodDetailPage.tsx:41` melakukan:

```ts
navigate(`/budget/submissions/new?period_id=${periodId}`)
```

`budgetRoutes` hanya punya `/budget/submissions/:id`, jadi `new` terbaca sebagai
id → `Number('new')` = `NaN` → `getSubmission(NaN)`. Tombol **Ajukan Anggaran**
menuju layar rusak.

Backend-nya sudah siap: `POST /budget-periods/{id}/submissions` menerima
`{department_id, notes?}` dan menolak duplikat departemen dengan 422.

### Perubahan

**Cara paling sedikit permukaan barunya: dialog, bukan halaman.** Yang
dibutuhkan hanya dua field, dan `ConfirmDialog` + `SearchableSelect` sudah ada.

Di `BudgetPeriodDetailPage`:

- Tombol **Ajukan Anggaran** membuka dialog berisi
  `SearchableSelect` departemen (`departemenApi.search`, sudah dipakai
  `BudgetComparisonPage`) + `Textarea` catatan opsional.
- Simpan → `budgetApi.createSubmission(periodId, {...})` →
  `invalidateQueries(['budget','submissions',periodId])` → buka pengajuannya.
- Error 422 duplikat departemen ditampilkan sebagai toast, bukan teks generik.
  Pakai `getApiErrorMessage` dari `lib/apiError.ts`.

Ganti `navigate(...)` yang lama; **jangan** menambah rute `/budget/submissions/new`.

> Kalau nanti pengajuan butuh lebih banyak field, barulah naikkan jadi halaman
> form sendiri dengan `FormLayout`. Sekarang dua field tidak menjustifikasi
> halaman penuh.

---

## 2.2 Catatan penolakan tidak pernah tampil

Backend `reject()` menyetel status ke **`draft`** — disengaja, dikunci oleh
`test_reject_returns_to_draft_and_increments_revision` — lalu menaikkan
`revision_number` dan menyimpan `rejection_note`.

Frontend memeriksa `status === 'rejected'` di dua tempat:

| Lokasi | Akibat |
|---|---|
| `BudgetSubmissionPage.tsx:67` | blok "Alasan penolakan" tidak pernah dirender |
| `BudgetApprovalActions.tsx:65` | petunjuk "revisi dan ajukan kembali" tidak pernah muncul |

Nilai `'rejected'` ada di enum DB tapi **tidak pernah ditulis service**.

### Perubahan

**Backend yang benar; frontend yang menyesuaikan.** Ganti syaratnya dari
status menjadi keberadaan catatan:

```ts
// SEBELUM
{submission.status === 'rejected' && submission.rejection_note && (

// SESUDAH — ditolak = draf yang punya catatan penolakan
{submission.status === 'draft' && submission.rejection_note && (
```

Sama untuk `BudgetApprovalActions.tsx:65`.

Tampilkan `revision_number` di samping catatan itu — itulah tanda bahwa
pengajuan ini pernah kembali dari persetujuan.

`BudgetSubmissionPage.tsx:21` (`isEditable`) tidak perlu diubah: `draft` sudah
tercakup, dan cabang `'rejected'`-nya sekadar mubazir.

**Jangan** hapus `'rejected'` dari `BudgetSubmissionStatus` maupun dari
`BudgetStatusBadge` — nilainya sah di enum DB dan mungkin dipakai nanti;
menghapusnya membuat data lama (jika ada) tidak bisa dirender.

---

## 2.3 Permission tolak lebih sempit dari rancangan

`app/Modules/Budget/Routes/api.php:29`:

```php
Route::post('/{id}/reject', [...])->middleware('permission:budgets.approve_head');
```

gap-12 §5 menyebut *"`budgets.approve_head` **atau** `budgets.approve_finance`"*.
Akibatnya role khusus yang hanya diberi `budgets.approve_finance` tidak bisa
menolak di tahap `approved_by_head` — justru tahap yang jadi tanggung jawabnya.

Tidak menggigit role bawaan: `finance` (satu-satunya non-wildcard yang punya
permission budget) memiliki keduanya. Ini menggigit role kustom.

### Perubahan

**Ini satu-satunya perubahan backend di seluruh rencana ini.**

```php
->middleware('permission:budgets.approve_head|budgets.approve_finance');
```

Sintaks `|` sudah didukung `EnsurePermission` (artinya "salah satu cukup") dan
dipakai di tempat lain, mis. `fiscal_year.lock_manage|fiscal_year.view`.

Tambahkan test di `tests/Feature/Budget/BudgetFlowTest.php`: user dengan
**hanya** `budgets.approve_finance` (lewat `company_user_permission_overrides`
atau role kustom) berhasil menolak pengajuan berstatus `approved_by_head`.
Tanpa test ini, perbaikannya tidak terkunci — `BudgetFlowTest` yang ada memakai
role dengan kedua permission, jadi tetap hijau baik sebelum maupun sesudah.

---

## Verifikasi

```bash
rtk proxy php artisan test --filter=Budget      # bukan seluruh suite
rtk proxy vendor/bin/pint --test app/Modules/Budget/ tests/Feature/Budget/
rtk npm run build
```

Manual — jalani siklus penuh sesuai `README.md` §"Cara membuktikan", terutama
langkah 4 (buat pengajuan) dan 6 (tolak → catatan tampil, revisi jadi 2).

Pastikan `transaction_workflow_mode` perusahaan uji **bukan** `simple_auto_post`,
kalau tidak pengajuan langsung `approved` dan rantai persetujuan tidak pernah
terlihat. Setelan ini yang membedakan kedua alur di gap-12 §3.
