# Budget Module — Index & Progress Ledger

> **Agent: baca file ini PERTAMA setiap sesi.** Ia menentukan fase mana yang sedang berjalan.
>
> Rencana ini **menghidupkan modul anggaran yang sudah ada**, bukan membangunnya
> dari nol. Backend-nya lengkap dan teruji; frontend-nya ada tapi tidak berfungsi
> dan tidak bisa dijangkau siapa pun.

## Konteks — kenapa rencana ini ada

Ditanyakan pemilik produk 2026-08-08: *"modul untuk anggaran belum kita
terapkan?"*

Jawabannya separuh. Modul Budget dibuat lewat dua commit (`7937589` backend,
`6e5836a` frontend, keduanya "gap-12") lalu tidak pernah disentuh lagi kecuali
ikut terbawa refactor lintas modul. **Frontend-nya tampaknya tidak pernah
dijalankan dengan data nyata** — tiga dari empat cacat di bawah akan langsung
terlihat pada percobaan pertama.

Rancangan aslinya utuh dan masih berlaku:
`/workspace/frontend/docs/gap_docs/gap-12-budget-module.md`. Rencana ini **tidak
mengubah rancangan itu**, hanya menyelesaikan pelaksanaannya.

### Keadaan terverifikasi 2026-08-08

| Lapis | Keadaan |
|---|---|
| Backend | ✅ Lengkap. 3 controller, 3 model, 7 request, 5 service, 16 endpoint, terdaftar di `routes/api.php:25`. `BudgetFlowTest` 6 lulus (rantai persetujuan penuh, reject→revisi, duplikat baris, larangan edit setelah approve, role tak berhak). |
| Peringatan over-budget | ✅ **Berfungsi.** `BudgetWarningService` dipanggil `JournalEntryController.php:103`, ditampilkan sebagai toast di `JournalFormPage.tsx:144`. Jalur ini lewat `journalApi`, bukan `budgetApi`, jadi luput dari cacat di bawah. |
| Frontend | ❌ 5 halaman + 4 komponen ada, tipe sudah cocok dengan backend — tapi tidak berfungsi. |
| Data | Kosong. `budget_periods` = 0 di kedua tenant. Modul ini belum pernah dipakai. |

## Cacat yang ditemukan — semuanya sudah dibuktikan

### A. Seluruh data terbaca `undefined` — penyebab utama

`budgetApi` adalah **satu-satunya** service di seluruh frontend yang menulis
`.then((r) => r.data)` — **16 kali**, di setiap method. Interceptor
`src/services/http.ts:160` sudah mengembalikan `response.data`, jadi itu unwrap
kedua.

Dibuktikan langsung: satu periode anggaran dibuat lewat API, responsnya
`{success, data: [{...}]}`. `http.get()` menyerahkan objek itu apa adanya →
`.then(r => r.data)` memotongnya jadi array → halaman melakukan `data?.data` →
`undefined` → `[]`. **Daftar periode selalu menampilkan "Belum ada periode
anggaran", berapa pun datanya.** (Baris ujinya sudah dihapus.)

Kenapa `npm run build` tetap hijau: `http.get('/budget-periods')` dipanggil
tanpa generic sehingga bertipe `any`. Anotasi `Promise<ApiResponse<...>>` di
service itu berbohong ke type checker, dan `any` menutupinya —
persis larangan `AGENTS.md` §8 tentang `any` tanpa justifikasi.

### B. Tidak ada pintu masuknya

`src/router/moduleConfig.ts` mendefinisikan 10 modul; Budget bukan salah satunya.
Tidak ada ikon topbar, tidak ada entri ribbon. Rutenya terdaftar di router, tapi
aplikasi memakai `createMemoryRouter` — satu-satunya jalan masuk adalah deep link
pada muat pertama.

`BudgetComparisonPage` juga tidak terjangkau: ia dirutekan dari modul Laporan
(`/reports/budget/comparison`) tapi **tidak ada entri di
`reports/constants/reportCategories.ts`**. Kedua pintu masuk yatim.

### C. "Ajukan Anggaran" menuju rute yang tidak ada

`BudgetPeriodDetailPage.tsx:41` melakukan `navigate('/budget/submissions/new?period_id=…')`,
tapi `budgetRoutes` hanya punya `/budget/submissions/:id`. Jadi `new` terbaca
sebagai id → `Number('new')` = `NaN` → `getSubmission(NaN)`. **Tidak ada UI untuk
membuat pengajuan sama sekali.**

### D. Catatan penolakan tidak pernah tampil

Backend `reject()` menyetel status ke **`draft`** (sengaja — lihat
`test_reject_returns_to_draft_and_increments_revision`), menaikkan
`revision_number`, dan menyimpan `rejection_note`. Frontend memeriksa
`status === 'rejected'` di `BudgetSubmissionPage.tsx:67` dan
`BudgetApprovalActions.tsx:65`. Nilai `'rejected'` ada di enum DB tapi **tidak
pernah ditulis service**. Akibatnya pengajuan yang ditolak tampak seperti draf
biasa tanpa penjelasan apa pun.

Yang benar adalah backend-nya; frontend yang harus menyesuaikan.

### E. Permission tolak lebih sempit dari rancangan

`Routes/api.php:29` hanya memasang `permission:budgets.approve_head`, sedangkan
gap-12 §5 menyebut *"`budgets.approve_head` atau `budgets.approve_finance`"*.
Tidak menggigit role bawaan (`finance` punya keduanya), tapi role khusus yang
hanya diberi `budgets.approve_finance` tidak bisa menolak di tahap
`approved_by_head` — padahal di situlah perannya.

### F. Menyimpang dari pola shell

Halaman budget memakai `navigate()` langsung dan `<table>` manual, bukan
`useRecordTab` + `DataTable`. Karena tidak membuat tab, tab bar tidak sinkron dan
halamannya hilang begitu user berpindah tab.

## Keputusan — jangan diubah tanpa membaca alasannya

Ketiganya diputuskan pemilik produk 2026-08-08.

1. **Anggaran jadi modul sendiri di topbar**, bukan submenu Buku Besar.
   Alurnya (periode → pengajuan → persetujuan → konsolidasi) adalah domain
   tersendiri. Bonus teknis: `detectModuleFromPath()` mencocokkan
   `pathname.startsWith('/' + module.id)`, jadi id modul `budget` langsung cocok
   dengan rute `/budget/...` yang sudah ada — **tidak ada rute yang perlu
   dipindah**.

2. **Perbaiki sekaligus samakan ke pola shell standar.** Alternatifnya
   meninggalkan pola kedua (tabel manual + `navigate()`) yang harus dirawat
   terpisah dari 21 halaman daftar lain.

3. **Scoping departemen ditunda**, dicatat sebagai keputusan terbuka di bawah.

## Keputusan terbuka — butuh pemilik produk

**gap-12 §5 menyebut daftar pengajuan seharusnya "Finance: semua; Dept: milik
sendiri". Itu tidak bisa dikerjakan sekarang** — dan bukan karena terlewat:
**tidak ada kolom apa pun yang menghubungkan user ke departemen.**
`company_users` (central) hanya punya `role`; tabel `departments` (tenant) tidak
punya kaitan ke user. Diperiksa langsung di migrasi, bukan diasumsikan.

Melaksanakannya butuh migrasi central (`company_users.department_id`) **plus** UI
penetapan departemen di modul Akses. Sampai itu diputuskan, semua pemegang
`budgets.view` melihat seluruh pengajuan.

> ⚠️ Jangan "sekalian saja" menambahkan kolomnya di tengah fase mana pun.
> Multi-tenancy di sini satu database per perusahaan; menaruh `department_id`
> di tabel central berarti satu departemen per user **untuk semua perusahaan**,
> yang kemungkinan besar salah. Butuh rancangan tersendiri.

## Progress Ledger

| Fase | Judul | File | Status | Commit |
|------|-------|------|--------|--------|
| 0 | Perbaiki kontrak service `budgetApi` | `phase-0-service-contract.md` | ⬜ Belum | — |
| 1 | Navigasi: modul topbar + katalog laporan | `phase-1-navigation.md` | ⬜ Belum | — |
| 2 | Lubang alur kerja: buat pengajuan, penolakan, permission | `phase-2-workflow-gaps.md` | ⬜ Belum | — |
| 3 | Samakan ke pola shell standar | `phase-3-shell-conformance.md` | ⬜ Belum | — |

> Status yang boleh: `⬜ Belum`, `🔄 Berjalan`, `✅ Selesai`.

**Fase 0 wajib lebih dulu, tanpa kecuali.** Selama double-unwrap masih ada,
setiap perbaikan lain tidak akan terlihat hasilnya — layarnya kosong apa pun yang
Anda kerjakan. Fase 1 berikutnya, karena tanpa menu tidak ada cara menguji
manual selain deep link.

## Prinsip

- **Rancangan gap-12 adalah acuan, bukan bahan negosiasi.** Kalau kode dan
  gap-12 berbeda, gap-12 yang menang — kecuali dicatat sebagai koreksi
  bersama alasannya (cacat D adalah satu-satunya: di situ kode backend yang
  benar dan dokumennya sudah konsisten dengan kode).
- **Backend hanya disentuh untuk cacat E.** Kalau ternyata butuh perubahan
  backend lain, berhenti dan catat — berarti ada asumsi rencana ini yang salah.
- **Jangan buat komponen baru.** Semua yang dibutuhkan sudah ada; lihat
  `reference/04-komponen-reusable.md`.
- **Jangan menambah data uji ke tenant demo tanpa membersihkannya.**
  `budget_periods` sekarang 0 di kedua tenant; kembalikan ke keadaan itu.

## Cara membuktikan modulnya benar-benar hidup

Bukan "halamannya terbuka" — itu sudah terjadi sejak dulu, hanya isinya kosong.
Yang membuktikan: **data yang dibuat muncul kembali di layar.**

1. Login sebagai `admin@example.com` / `password`, pilih sebuah perusahaan.
2. Topbar → **Anggaran** → Periode Anggaran → **Buat Periode**. Simpan.
3. **Daftar periode harus menampilkan baris itu.** Sebelum Fase 0, langkah
   inilah yang gagal — daftarnya tetap berbunyi "Belum ada periode anggaran".
4. Buka periodenya → **Ajukan Anggaran** → pilih departemen → simpan.
   Sebelum Fase 2, tombol ini menuju rute yang tidak ada.
5. Isi baris anggaran (akun + nominal) → Simpan Baris → **Ajukan**.
6. Setujui sebagai Kepala, lalu **Tolak** di tahap finance dengan alasan.
   **Alasan penolakan harus tampil** dan `revision_number` naik jadi 2.
   Sebelum Fase 2, catatan itu tidak pernah muncul.
7. Tab **Konsolidasi** menampilkan total per departemen setelah pengajuan
   berstatus `approved`.
8. Buat jurnal yang melampaui anggaran akun tersebut → toast peringatan muncul.
   Jalur ini sudah berfungsi sebelum rencana ini; ini uji regresi.
9. Laporan → **Realisasi vs Anggaran** terjangkau dari katalog laporan.

Bersihkan data uji setelah selesai.

## Referensi

- Rancangan asli: `/workspace/frontend/docs/gap_docs/gap-12-budget-module.md`
- Pola halaman daftar & form acuan: `reference/04-komponen-reusable.md` §7–8
- Aturan permission & guard: `reference/05-role-permission-guard.md`
- Shell tab & memory router: `reference/03-frontend.md` §3–4
- Backend modul: `app/Modules/Budget/`, test `tests/Feature/Budget/BudgetFlowTest.php`
