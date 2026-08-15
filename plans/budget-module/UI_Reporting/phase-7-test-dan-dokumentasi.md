# Phase 7 — Test & Dokumentasi

**Sisi**: Backend + dokumen
**Prasyarat**: fase 1–6

---

## Objective

Memastikan yang dibangun benar-benar bekerja, lalu memperbarui dokumen supaya tidak
mengulang kesalahan `backend-missing-modules-audit.md` — dokumen yang menyatakan
modul Budget tidak ada padahal sudah dibangun, dan salah selama enam minggu.

---

## 1. Test backend

Hanya fase 2 yang mengubah backend. Testnya sudah dirinci di dokumen fase itu
(`BudgetSubmissionListTest`, 9 kasus).

Gate akhir:

```bash
rtk php artisan test                       # seluruh suite, bukan hanya Budget
vendor/bin/pint --test app/Modules/Budget tests/Feature/Budget
```

Suite penuh sebelum rencana ini: **1388 passed, 5 skipped, 0 failed**. Angka itu
tidak boleh turun.

### Kebersihan tenant

Aturan yang sudah menggigit sekali di rencana sebelumnya: **jangan jalankan dua
suite bersamaan** terhadap `database/tenants/` yang sama — hasilnya "TENANT FILE
LEAK" dan file DB yang tertinggal.

Setelah selesai, verifikasi:

```bash
ls database/tenants/          # hanya 2 DB demo, tanpa file test
```

dan `budget_periods` tetap 0 baris di **kedua** tenant demo.

---

## 2. Test frontend

Repo ini tidak punya test frontend otomatis. Verifikasinya `npm run build` +
`rtk lint` + langkah manual.

Kumpulkan seluruh langkah manual dari fase 1–6 jadi satu daftar berurut. Totalnya
sekitar 48 langkah:

| Fase | Langkah |
|---|---|
| 1 — Form Proyek | 8 |
| 3 — Halaman Budget | 11 |
| 4 — Monitoring | 10 |
| 5 — Halaman Project | 10 |
| 6 — Navigasi & Katalog | 9 |

Butuh backend hidup. **Jangan tandai fase ini selesai sebelum semuanya dijalankan** —
aturan yang sama dipakai fase 8 rencana sebelumnya, dan fase itu memang ditinggal
di status 🔄 karena langkah manualnya belum dijalankan. Jangan mengulangi dengan
menandainya selesai secara optimistis.

---

## 3. Dokumen yang wajib diperbarui

| Dokumen | Perubahan |
|---|---|
| `frontend/docs/struktur_frontend.md` | Semua file baru fase 1–6 (≈8 file) |
| `laravel_backend/docs/backend-directory-tree.md` | + `ListBudgetSubmissionsRequest`, hitungan direktori |
| `app/Modules/Budget/README.md` | + endpoint daftar submission di daftar rute |
| `frontend/docs/gap_docs/gap-12-budget-module.md` | Tambah catatan: alur approval yang dijelaskan di sana kini punya UI-nya |
| `plans/budget-module/UI_Reporting/README.md` | Ledger progress + penyimpangan |
| Tiap `phase-N-*.md` | Bagian "Hasil implementasi" di akhir |

### Yang harus ditulis, bukan disembunyikan

Bagian "Hasil implementasi" wajib memuat **penyimpangan** dari rencana, bukan hanya
yang berhasil. Rencana sebelumnya mencatat 8 penyimpangan dan itu yang membuat
dokumennya berguna enam minggu kemudian.

Khususnya, catat kalau:

- Salah satu dari T1/T2/T3 ternyata lebih dalam dari dugaan fase 0
- `ModuleRibbonItem` ternyata tidak bisa menerima `group` tanpa merambat
- Preset di fase 4 ternyata butuh perubahan backend (seharusnya tidak — kalau iya,
  itu tanda aturan §3.2 dilanggar)

---

## 4. Yang tetap terbuka setelah rencana ini

Tulis eksplisit di README, jangan dibiarkan tersirat:

| Terbuka | Milik siapa |
|---|---|
| **G11** — dimensi bocor di Sales Return, Purchase Bill/Return, StockMovementJournalService, Fixed Assets | `../New_Fitures/project-dimension-budgeting-readiness-plan.md` |
| Export PDF/Excel laporan anggaran (`budgets.export` sudah ada, implementasi belum) | belum dijadwalkan |
| `PeriodLockService::isDateReadOnly()` belum terhubung ke pembuatan/revisi anggaran | `../New_Fitures/` fase 8, tersisa |
| Audit trail `JournalEntryService`, `CashPaymentService`, `CashReceiptService`, `BankTransferService` — pola `?AuditLogService = null` membuat dependensinya tidak pernah terisi | temuan sampingan rencana sebelumnya, belum diperbaiki |

Yang terakhir itu temuan serius yang ditemukan saat mengerjakan modul Budget:
Laravel mengisi parameter ber-default dengan nilai defaultnya, jadi audit log di
empat service itu kemungkinan besar tidak pernah tertulis. Sudah diperbaiki di
service Budget, belum di empat itu.

---

## Files affected

Dokumen saja, kecuali perbaikan yang muncul dari verifikasi.

---

## Acceptance criteria

- [ ] Suite backend penuh hijau, jumlah test tidak turun dari 1388
- [ ] Pint bersih untuk file yang disentuh rencana ini
- [ ] `npm run build` 0 error, `rtk lint` bersih
- [ ] `database/tenants/` bersih; `budget_periods` 0 di kedua tenant demo
- [ ] 48 langkah verifikasi manual dijalankan dan hasilnya dicatat
- [ ] Enam dokumen di §3 diperbarui
- [ ] Penyimpangan tercatat, bukan hanya keberhasilan
- [ ] Empat item terbuka di §4 tertulis eksplisit di README

---

## Hasil implementasi — 2026-08-15

### Suite backend

```
1407 tests · 1402 passed · 5 skipped · 0 failed · exit 0
```

Naik dari 1393 sebelum rencana ini (+14: 11 `BudgetSubmissionListTest` +
3 `test_project_transactions_*` yang ditambahkan lebih dulu bersama endpoint
Project Transactions).

Pint bersih untuk `app/Modules/Budget` dan `tests/Feature/Budget`. Utang lama di
Sales/Imports/config/bootstrap sengaja tidak disentuh.

### Frontend

`npm run build` 0 error dan `rtk lint` bersih di akhir **setiap** fase, bukan
hanya di akhir — enam kali total.

### Kebersihan tenant

`database/tenants/` hanya berisi dua DB demo, tanpa file test.

Satu catatan yang harus jujur ditulis: `company_000002.sqlite` berisi **1 baris
`budget_periods`** ("Pelatihan Peningkatan Kinerja", dibuat 2026-08-12) beserta 1
submission dan 1 baris anggaran. Itu **data demo yang sudah ada sebelumnya**,
bukan kebocoran dari pekerjaan ini — `created_at` mendahului rencana ini, dan
mtime kedua file tenant masih 2026-08-12/13 meski suite dijalankan 2026-08-15.
Artinya suite memang tidak menyentuh DB demo sama sekali. Tidak ada yang
dibersihkan, karena tidak ada yang dikotori.

### Dokumen yang diperbarui

| Dokumen | Perubahan |
|---|---|
| `frontend/docs/struktur_frontend.md` | +9 file budget, +2 file master-data (`ProyekFormPage` ternyata belum pernah terdaftar) |
| `app/Modules/Budget/README.md` | + `BudgetProjectService`/`BudgetCashService` di tabel mesin, + bagian "Dua jalur daftar submission" |
| `frontend/docs/gap_docs/gap-12-budget-module.md` | + catatan bahwa alur approval kini punya UI-nya |
| `UI_Reporting/README.md` | Ledger + 8 penyimpangan (P1–P8) |
| `phase-1` … `phase-6` | Bagian "Hasil implementasi" |

### Penyimpangan

- **P8** — `backend-directory-tree.md` **tidak** disentuh. Dokumen itu hanya
  mendaftar direktori, dan rencana ini tidak menambah satu pun direktori backend
  (dua request baru masuk ke `Modules/Budget/Requests` yang sudah ada).
  Memperbarui tanggalnya tanpa perubahan struktural hanya menambah noise.

### Yang belum

**48 langkah verifikasi manual belum dijalankan** — butuh backend hidup.
Fase ini tetap 🔄, bukan ✅, mengikuti aturannya sendiri di §2. Rencana
sebelumnya meninggalkan fase 8 di status yang sama karena alasan yang sama;
menandainya selesai secara optimistis akan mengulangi kesalahan yang persis
dihindari di sana.
