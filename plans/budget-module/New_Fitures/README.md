# Unified Multidimensional Budgeting — Index & Progress Ledger

> **Agent: baca file ini PERTAMA setiap sesi**, lalu `phase-0-context-rules-guardrails.md`.
> Phase 0 memuat aturan main yang mengikat seluruh fase — jangan mulai fase mana pun
> sebelum membacanya.
>
> Rencana ini **menyempurnakan modul anggaran yang sudah ada**, bukan membangunnya dari nol.

## Konteks — kenapa rencana ini ada

Brief pemilik produk ada di `instruction.md` (834 baris): satu budget engine, banyak dimensi,
banyak view — bukan lima engine terpisah. Instruction itu melarang coding dan hanya meminta
audit + implementation plan. Audit sudah dilakukan; hasilnya ada di `phase-0`.

Rencana sebelumnya (`../README.md`, Fase 0–3, selesai 2026-08-09) **menghidupkan** modul yang
mati: memperbaiki kontrak service, menambah pintu masuk, menutup lubang alur kerja, dan
menyamakan ke pola shell. Rencana ini melanjutkannya ke lapis berikutnya — **mengubah bentuk
data supaya benar-benar multidimensi.**

## Peta dokumen

| Fase | Judul | File | Status |
|------|-------|------|--------|
| 0 | Context, Rules & Guardrails | `phase-0-context-rules-guardrails.md` | ⬜ Belum |
| 0.1 | Satukan Form Baris-Item ke `LineItemsTable` | `phase-0.1-reusable-line-items-component.md` | ⬜ Belum |
| 1 | Fondasi Data | `phase-1-fondasi-data.md` | ⬜ Belum |
| 2 | Mesin Inti | `phase-2-mesin-inti.md` | ⬜ Belum |
| 3 | Perbaikan 4 Cacat | `phase-3-perbaikan-cacat.md` | ⬜ Belum |
| 4 | Dimensi Revenue | `phase-4-dimensi-revenue.md` | ⬜ Belum |
| 5 | Versioning & Audit | `phase-5-versioning-dan-audit.md` | ⬜ Belum |
| 6 | View Turunan & Permission | `phase-6-view-turunan-dan-permission.md` | ⬜ Belum |
| 7 | Frontend | `phase-7-frontend.md` | ⬜ Belum |
| 8 | Dokumentasi | `phase-8-dokumentasi.md` | ⬜ Belum |
| — | Project Dimension & Budgeting Readiness (audit + plan, menggantikan/memperluas bagian Project di fase 4 & 6) | `project-dimension-budgeting-readiness-plan.md` | ✅ Plan selesai — implementasi belum dimulai |

> Status yang boleh: `⬜ Belum`, `🔄 Berjalan`, `✅ Selesai`.

## Urutan pengerjaan

```
1 ──▶ 2 ──▶ 3
│     │
│     └──▶ 6 ──▶ 7 ──▶ 8
├──▶ 5 ────┘      │
                  │
4 ────────────────┘   (independen — boleh dikerjakan kapan saja)
```

Fase 4 (dimensi revenue di Sales Invoice) **tidak bergantung pada fase mana pun** dan boleh
dikerjakan lebih dulu. Hasilnya baru terpakai di fase 6.

Fase 0.1 (satukan form baris-item ke `LineItemsTable`) dikerjakan lebih dulu sebelum fase 7 dan
sebelum P1 di `project-dimension-budgeting-readiness-plan.md` — permintaan eksplisit pemilik
produk agar semua form baris-item rapi konsisten seperti form penerimaan (`GoodsReceiptFormPage.tsx`),
sebelum kolom-kolom baru ditambahkan di atasnya.

## Keputusan pemilik produk — jangan diubah tanpa membaca alasannya

Keempatnya diputuskan setelah audit codebase, bukan diasumsikan.

1. **Department = Cost Center.** `cost_centers` tidak ada di seluruh codebase; `departments`
   sudah menjadi dimensi resmi di `journal_entry_lines`. Ditambah `parent_id` supaya
   hierarkis. **Tidak ada dimensi ke-3 di ledger** — menambahkannya berarti menyentuh
   sales, purchase, cash, inventory, fixed asset, `ReportDimensionFilter`, dan 20 report
   request sekaligus.

2. **Redesign skema sekarang.** `budget_periods` = 0 baris di kedua tenant, jadi tidak ada
   data yang perlu dimigrasi. Menunda berarti merombak sambil membawa data.

3. **Perbaiki grouping revenue di Sales Invoice.** Tanpa itu `project_id` tidak pernah sampai
   ke baris jurnal pendapatan, dan Project Profitability mustahil.

4. **MUST HAVE keempatnya**: Versioning, Cash Budget, Project Profitability, perbaikan 4 cacat.

## Keputusan terbuka — masih butuh pemilik produk

**Scoping "Dept hanya lihat pengajuannya sendiri"** tetap ditunda dari rencana sebelumnya.
Tidak ada kolom apa pun yang menghubungkan user ke departemen. Menambahkan
`company_users.department_id` di DB central berarti satu departemen per user untuk **semua**
perusahaan, yang hampir pasti salah.

> ⚠️ Jangan "sekalian saja" menambahkan kolomnya di tengah fase mana pun. Butuh rancangan
> tersendiri.

## Prinsip

- **Actual selalu dari ledger existing.** Tidak ada input actual manual, tidak ada ledger baru.
- **Kalau sebuah angka bisa dihitung, jangan disimpan.** Profit, margin, variance, utilization
  semuanya turunan.
- **Satu logika, banyak pemakai.** Peringatan over-budget dan laporan perbandingan wajib
  memakai resolver yang sama — perbedaan di antara keduanya adalah akar empat cacat lama.
- **Jangan buat komponen UI baru.** Lihat `reference/04-komponen-reusable.md`.
- **Jangan menambah data uji ke tenant demo tanpa membersihkannya.** `budget_periods` harus
  kembali 0 di kedua tenant setelah verifikasi manual.

## Referensi

- Brief: `instruction.md`
- Rencana sebelumnya (Fase 0–3, selesai): `../README.md`
- Rancangan modul asli: `/workspace/frontend/docs/gap_docs/gap-12-budget-module.md`
- Konvensi backend: `/workspace/Finlite_knowladge/reference/02-backend.md`
- Konvensi frontend: `/workspace/Finlite_knowladge/reference/03-frontend.md`
- Komponen reusable: `/workspace/Finlite_knowladge/reference/04-komponen-reusable.md`
- Permission & guard: `/workspace/Finlite_knowladge/reference/05-role-permission-guard.md`
- Modul backend: `/workspace/laravel_backend/app/Modules/Budget/`
- Modul frontend: `/workspace/frontend/src/modules/budget/`
