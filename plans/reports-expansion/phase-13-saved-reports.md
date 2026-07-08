# Fase 13 — Laporan Tersimpan (Saved Reports)

**Prioritas:** C (design-I2 §2 "Laporan Tersimpan" khusus, §7, §9)
**Estimasi:** besar — fitur UX baru (bukan sekadar laporan). Backend baru (persist config).

## Tujuan

design-I2 §9: "Laporan Tersimpan adalah konsep UX (user menyimpan filter/config laporan), bukan list laporan tetap — desain tersendiri dibutuhkan." Memungkinkan user menyimpan kombinasi (laporan + filter periode/dimensi) dengan nama, lalu membukanya kembali.

## Prasyarat

- **Fase A/B (1–8) selesai** — supaya ada cukup laporan + filter yang bermakna untuk disimpan. Fase C lain tidak wajib.
- **Desain UX tersendiri diperlukan** (design-I2 §9). Sebelum coding, buat mini design-doc atau konfirmasi dengan user: apa yang disimpan (report id + params), scope (per user / per company), UI (dropdown "simpan filter ini" di tiap halaman laporan + daftar tersimpan).
- Baca `00-conventions.md` §1–5.

## Daftar tugas

### T13.1 — Backend: persist saved report config
- [ ] Migration tabel `saved_reports` (tenant): id, company_id, user_id, report_key (mis. 'general-ledger'), name, params (json), created_at. Model + relasi.
- [ ] Endpoints CRUD: `GET/POST /reports/saved`, `GET/PUT/DELETE /reports/saved/{id}`. FormRequest validasi report_key (whitelist) + params json. Controller + route `permission:reports.view`. Feature test (CRUD, scope per user/company, tidak bisa akses milik user lain bila per-user).

### T13.2 — Frontend: hook + service
- [ ] `savedReportsApi` (list/create/delete) + types. TanStack Query hooks. Store: TIDAK simpan data API di Zustand (hard rule) — pakai Query cache.

### T13.3 — Frontend: UI simpan & buka
- [ ] Komponen reusable `SaveReportButton` di header laporan (`ReportCompactBar` atau `WorkspaceLayout` actions) — "Simpan Laporan Ini" → dialog nama → POST params aktif.
- [ ] Halaman/panel "Laporan Tersimpan" — daftar saved reports; klik → navigate ke report_key route dengan params ter-restore (via query param atau state). Route `/reports/saved`, katalog: entri khusus (kategori sendiri atau di index).
- [ ] Restore params: halaman laporan membaca saved params saat dibuka dari saved report.

### T13.4 — Integrasi ke halaman existing
- [ ] Tambahkan `SaveReportButton` ke halaman laporan utama (GL, TB, PL, BS, dst) — minimal beberapa yang paling sering dipakai; rollout bertahap.

### T13.5 — struktur_frontend.md
- [ ] Daftarkan komponen + halaman + service baru.

## Peta File

> Fitur UX baru — satu-satunya fase (selain kondisional 12) yang **menambah migration & model**. Ada komponen reusable + integrasi ke halaman existing.

**➕ Tambah — Backend**
- `laravel_backend/database/migrations/tenant/xxxx_create_saved_reports_table.php`
- `laravel_backend/app/Modules/Reports/Models/SavedReport.php` *(model tenant; daftarkan di morphMap bila perlu — cek pola SharedServiceProvider)*
- `laravel_backend/app/Modules/Reports/Services/SavedReportService.php`
- `laravel_backend/app/Modules/Reports/Requests/SavedReportRequest.php`
- `laravel_backend/app/Modules/Reports/Controllers/SavedReportController.php` *(CRUD)*
- `laravel_backend/tests/Feature/Reports/SavedReportTest.php`

**➕ Tambah — Frontend**
- `react_frontend/src/modules/reports/services/savedReportsApi.ts`
- `react_frontend/src/modules/reports/hooks/useSavedReports.ts` *(TanStack Query hooks)*
- `react_frontend/src/modules/reports/components/SaveReportButton.tsx`
- `react_frontend/src/modules/reports/pages/SavedReportsPage.tsx`

**✏️ Ubah — Backend**
- `laravel_backend/app/Modules/Reports/Routes/api.php` — `GET/POST /reports/saved`, `GET/PUT/DELETE /reports/saved/{id}`.

**✏️ Ubah — Frontend**
- `react_frontend/src/modules/reports/types/reports.types.ts` — `SavedReport`, `SavedReportParams`.
- `react_frontend/src/modules/reports/routes.tsx` — `/reports/saved`.
- `react_frontend/src/modules/reports/constants/reportCategories.ts` — entri/kategori "Laporan Tersimpan".
- `react_frontend/src/modules/reports/pages/{GeneralLedger,TrialBalance,ProfitLoss,BalanceSheet,...}Page.tsx` — sisipkan `SaveReportButton` + baca saved params saat restore (rollout bertahap, T13.4).
- `react_frontend/docs/struktur_frontend.md`.

**🗑️ Hapus** — Tidak ada.

## Checklist Verifikasi

- [ ] `npm run build`/`lint` 0 error.
- [ ] Backend test CRUD hijau; `pint --test` hijau; migration jalan; route naik.
- [ ] Runtime company 2: simpan filter GL → muncul di daftar tersimpan → buka → filter ter-restore & laporan render.
- [ ] Scope benar: user lain / company lain tidak melihat saved report yang bukan miliknya (tenant + user scope).

## Git Checkpoint

- Commit backend: `feat(reports): saved reports CRUD + migration (phase 13)`.
- Commit frontend: `feat(reports): saved reports UX (phase 13)`.
- Update ledger Fase 13 → ✅.

## Catatan penutup

Setelah Fase 13, seluruh visi design-I2 (nav + konten A/B/C) tercakup. Laporan yang design-I2 tandai "tidak akan diimplementasi" (serial tracking, per-cabang/departemen/proyek sebagai laporan, valuasi FIFO, format impor) **sengaja tidak ada fase** — jangan tambahkan tanpa keputusan user baru.
