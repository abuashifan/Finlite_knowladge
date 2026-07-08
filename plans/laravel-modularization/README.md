# Laravel Modularization — Index & Progress Ledger

> **Agent: baca file ini PERTAMA setiap sesi.** Ia menentukan fase mana yang sedang berjalan.
> Dokumen ini menggantikan `plans/laravel-modularization-plan.md` yang lama (versi ringkas, kurang detail).

Rencana ini memecah refactor backend Laravel menjadi arsitektur modular ke dalam **9 fase yang berdiri sendiri**. Tiap fase dirancang bisa dikerjakan di **sesi terpisah (cold start)** — agent tidak perlu mengingat pekerjaan fase sebelumnya, cukup membaca ledger ini + file fase yang relevan.

## Cara pakai (alur tiap sesi)

1. Baca **`README.md`** ini → lihat tabel ledger di bawah, temukan fase pertama yang `⬜ Belum`.
2. Baca **`00-conventions.md`** → aturan namespace, mekanisme alias, ranjau (morph/factory), perintah verifikasi standar. (Wajib, tapi singkat.)
3. Buka **`phase-N-*.md`** untuk fase itu.
4. Jalankan bagian **Prasyarat** di file fase → verifikasi repo memang ada di titik awal yang benar.
5. Kerjakan mapping file + edit infra + alias sesuai daftar eksplisit di file fase.
6. Jalankan **Checklist Verifikasi** fase.
7. Commit sesuai **Git Checkpoint** fase.
8. **Update ledger di bawah** (`⬜ Belum` → `✅ Selesai` + isi kolom Commit) lalu commit README. **Ini wajib** — inilah memori lintas sesi.

## Progress Ledger

| Fase | Judul | File | Status | Commit |
|------|-------|------|--------|--------|
| 0 | Shared Foundation (tanpa Model) | `phase-0-shared.md` | ✅ Selesai | `d1ab6b7` |
| 1 | Auth · Companies · Tenant | `phase-1-auth-companies-tenant.md` | ✅ Selesai | `27ab9e5` |
| 2 | Access · Settings · Setup | `phase-2-access-settings-setup.md` | ⬜ Belum | — |
| 3 | MasterData · Accounting · Journal | `phase-3-masterdata-accounting-journal.md` | ⬜ Belum | — |
| 4 | CashBank · OpeningBalance · Budget | `phase-4-cashbank-openingbalance-budget.md` | ⬜ Belum | — |
| 5 | Inventory · Sales · Purchase | `phase-5-inventory-sales-purchase.md` | ⬜ Belum | — |
| 6 | FixedAssets · Reports · Dashboard | `phase-6-fixedassets-reports-dashboard.md` | ⬜ Belum | — |
| 7 | Model Migration (central + tenant) | `phase-7-model-migration.md` | ⬜ Belum | — |
| 8 | Cleanup + Architecture Tests | `phase-8-cleanup-archtests.md` | ⬜ Belum | — |

> Status yang boleh: `⬜ Belum`, `🔄 Berjalan`, `✅ Selesai`. Kalau `🔄 Berjalan` tertinggal dari sesi sebelumnya, jalankan Prasyarat fase itu untuk menentukan seberapa jauh sudah dikerjakan sebelum melanjutkan.

## Prinsip desain

- **Non-blocking / bertahap** — tiap fase menyisakan aplikasi dalam keadaan hijau (semua test lulus). Bisa berhenti kapan saja.
- **Alias bridge** — class yang dipindah tetap bisa diakses lewat nama lama (`class_alias`) sampai Fase 8. Referensi lama tidak perlu langsung diubah.
- **Model dipindah paling akhir (Fase 7)** — karena ada ranjau morph-map & factory-resolution (lihat `00-conventions.md`). Fase 0–6 **tidak menyentuh** model.
- **Config & migration tidak dipindah** — tetap di `config/` dan `database/migrations/`. Lihat alasan di `00-conventions.md`.

## Keputusan arsitektur yang sudah dikunci

1. Kode cross-cutting → **`app/Shared/`** (bukan `app/Core/`). Melanjutkan scaffolding `app/Shared/` yang sudah ada + selaras dengan `laravel_backend/docs/backend-modular-monolith-plan.md` (source of truth per `AGENTS.md`). Struktur `Shared/` dilengkapi slot `Models/`, `Http/`, `Providers/`, `Exceptions/`, `Reports/`, `Enums/`.
2. Value object **domain-spesifik ikut modulnya**: `Support/Inventory` → Inventory, `Support/OpeningBalance` → OpeningBalance.
3. **Permission dipecah**: service evaluasi → `Shared/Permission/`, endpoint (`PermissionController`) → modul `Auth`.
4. **Report primitives dipakai lintas modul** (`Data/Reports`, `ReportVisibilityMode`, trait `HasReportVisibility`) → `Shared/Reports/`. Sedangkan `Requests/Concerns` report-filter hanya dipakai modul Reports → ikut modul Reports.
5. 18 modul dipertahankan (tidak digabung/dipecah).
