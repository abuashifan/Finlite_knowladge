# Company Session Layer — Tutup Database, Keluar, dan Scope Cache per Perusahaan

> Status: **SELESAI** (2026-08-08, frontend `2037d39`)
>
> Dokumen ini bukan rencana kerja yang menunggu dikerjakan. Ia catatan tentang
> **kenapa** layer ini ada dan **apa yang tidak boleh diubah tanpa membaca alasannya**.

## Bug yang memicunya

Dilaporkan pemilik produk: buka COA di perusahaan 2, pindah ke perusahaan 1 —
COA yang terbuka ikut terbawa; pindah balik ke perusahaan 2 — datanya tetap milik
perusahaan 1.

Direproduksi di browser sebelum apa pun diubah, dan hasilnya **lebih buruk dari
laporannya**: setelah dua kali berpindah, **nol** request COA dikirim. Isi tabel
tidak pernah berubah dari perusahaan pertama.

```
[1] COA di PT Nusantara     | request: 1 | 1100 | Kas
[2] pindah ke PT Maju Jaya  | request: 0 | 1100 | Kas      <- data perusahaan 2
[3] kembali ke PT Nusantara | request: 0 | 1100 | Kas
```

### Sebab

Dua hal bersamaan:

1. Cache TanStack Query global, dan query key-nya **tidak** memuat id perusahaan
   (`['master-data-coa', params]` sama persis untuk semua tenant).
2. `staleTime: 30_000` di `main.tsx` membuat data tenant lain dianggap masih
   segar, sehingga tidak ada refetch sama sekali.

Header `X-Company-ID` sudah benar sejak awal — request-nya memang tidak pernah
dikirim.

### Kenapa ini bukan sekadar masalah tampilan

Tiap tenant punya file SQLite sendiri dengan autoincrement dari 1. Diverifikasi:

| id | company 1 | company 2 |
|----|-----------|-----------|
| 1 | 1100 Kas Kecil | 1100 Kas |
| 2 | 1110 Bank Operasional | 1110 Bank |

Daftar basi + klik baris membuka `/master-data/coa/5` — id yang **ada** di
perusahaan tujuan sebagai akun berbeda. Menyunting di sana berarti menyunting
record perusahaan lain. Itulah alasan tab ikut ditutup, bukan hanya cache.

## Bentuk akhir yang diminta pemilik produk

Dua aksi terpisah, keduanya mereset state klien:

- **Tutup Database** — menutup perusahaan aktif, sesi login tetap hidup, user
  mendarat di halaman pemilih perusahaan. **Ganti perusahaan berjalan lewat sini**;
  menu "Ganti Perusahaan" dihapus supaya tidak ada jalur pintas.
- **Keluar** — mengakhiri sesi login.

Keduanya **diblokir** (bukan dikonfirmasi) selama ada form dengan isian belum
tersimpan. Tidak ada tombol "lanjutkan saja": kedua aksi menutup semua tab, jadi
melanjutkan berarti membuang pekerjaan tanpa cara membatalkan.

## Peta file

| File | Peran |
|------|-------|
| `src/lib/companyScope.ts` | Berlangganan perubahan `activeCompanyId` → kosongkan cache query + tutup semua tab |
| `src/lib/companySession.ts` | `closeDatabase()`, `logoutFromApp()`, `getUnsavedForms()`, `focusFormTab()` |
| `src/hooks/useCompanySession.ts` | Menjalankan kedua aksi lewat penjaga form |
| `src/hooks/useUnsavedFormTracker.ts` | Melaporkan form yang isinya diubah user |
| `src/stores/useUnsavedFormsStore.ts` | Registry path form yang belum tersimpan |
| `src/components/shared/feedback/UnsavedFormsDialog.tsx` | Dialog pemblokir + tombol Buka |

## Empat hal yang jangan diubah tanpa membaca alasannya

### 1. Reset cache dipasang di `companyScope.ts`, bukan di halaman pemilih perusahaan

Meletakkannya di `CompanyPickerPage` hanya menutup satu jalur. Berlangganan
langsung ke store membuatnya **tidak bisa dilewati** — apa pun yang memanggil
`setActiveCompany()` atau `logout()` ikut tercakup, termasuk kode yang belum
ditulis.

`previousCompanyId` dibaca **setelah** zustand-persist merehidrasi (storage-nya
localStorage, jadi rehidrasi sinkron dan sudah selesai saat modul dijalankan).
Kalau dibaca sebelum rehidrasi, **muat-ulang halaman biasa akan terbaca sebagai
pergantian perusahaan dan menutup semua tab user**.

### 2. `queryClient.clear()`, bukan menambahkan id perusahaan ke setiap query key

Menyisipkan id ke key juga benar, tapi berarti menyentuh ~60 hook dan setiap hook
baru harus ingat melakukannya. `clear()` berlaku untuk semua hook yang ada maupun
yang belum ditulis. Cache yang hilang memang biaya yang dituju.

### 3. Penjaga di interceptor http hanya untuk GET

Balasan yang tiba setelah perusahaan berganti ditolak karena request-nya memakai
`X-Company-ID` lama. **Hanya GET** — mutasi sudah dieksekusi server, jadi
menolaknya di klien akan melaporkan gagal padahal datanya sudah berubah.

### 4. Deteksi "belum tersimpan" memakai `dirtyFields`, bukan `isDirty`

`isDirty` membandingkan seluruh nilai form dengan `defaultValues` lewat deep
equal. Hampir semua form di sini menyetel `defaultValues` sebagian saja (mis.
`CoaFormPage` hanya `account_type` + `parent_account_id`), sehingga field lain
berubah dari `undefined` ke `''` begitu didaftarkan.

**Diuji di browser:** form "Akun Baru" yang dibuka lalu didiamkan memblokir Tutup
Database. `dirtyFields` hanya terisi lewat event perubahan, jadi mendaftarkan
field tidak membuatnya kotor.

Keberadaan draft di localStorage juga **tidak** dipakai sebagai sinyal, dengan
alasan yang sama: draft ditulis untuk form yang baru dibuka juga.

### 5. Entri registry bertahan melewati unmount

Form ikut unmount saat user cuma berpindah tab — padahal tabnya masih terbuka.
**Diuji:** isi form COA, pindah ke tab Kontak, lalu Keluar — tanpa perilaku ini
aksinya lolos tanpa peringatan. Saat form di-mount lagi `dirtyFields`-nya kosong
(draft dipulihkan lewat `reset()`), jadi statusnya tidak pernah kembali sendiri.

Yang mencabut pendaftaran adalah **penutupan tabnya** di `useTabStore`
(`discardFormWork`). Entri yang tabnya sudah tidak ada diabaikan
`getUnsavedForms()`, jadi entri basi tidak bisa memblokir apa pun.

## Jebakan pemeliharaan

**Halaman form baru wajib melaporkan status belum-tersimpan.** 26 dari 28 halaman
form mendapatkannya gratis karena memakai `usePersistentFormDraft`, yang memanggil
`useUnsavedFormTracker` di dalamnya. Dua halaman memanggilnya langsung karena
tidak memakai hook draft:

- `src/modules/budget/pages/BudgetPeriodFormPage.tsx`
- `src/modules/fixed-assets/pages/FixedAssetFormPage.tsx`

Halaman form baru yang tidak memakai `usePersistentFormDraft` **harus** memanggil
`useUnsavedFormTracker({ control })` sendiri. Kalau lupa, isian di halaman itu
hilang tanpa peringatan saat user menutup database.

## Yang sengaja tidak dikerjakan

- **Logout otomatis karena sesi habis tidak lewat penjaga.** Sesi yang sudah
  kedaluwarsa tidak bisa ditahan state klien. Isian tetap ada sebagai draft di
  localStorage — kuncinya memuat `company-<id>` — dan muncul lagi setelah login
  ulang.
- **Tidak ada endpoint "deselect" di backend.** Tenancy ditentukan per-request
  lewat header `X-Company-ID`, jadi menutup database cukup di klien.
- **URL tidak selalu mengikuti layar.** `AppShell` menyetir router dari state tab,
  jadi setelah logout URL bisa tertinggal di `/` walau layar login sudah tampil.
  Perilaku lama, bukan dari perubahan ini; tidak mengganggu karena muat-ulang di
  `/` tetap diarahkan ke `/login`.

## Verifikasi

`npm run build` hijau, ESLint bersih, dan 9 skenario browser:

| # | Skenario | Hasil |
|---|----------|-------|
| 1 | Menu punya "Tutup Database" + "Keluar" terpisah | ✓ |
| 2 | Tutup Database → picker, tab tereset ke Dashboard | ✓ |
| 3 | Buka perusahaan lain → request baru, data ikut berganti | ✓ |
| 4 | Kembali ke perusahaan semula → data benar (inti bug) | ✓ |
| 5 | Form kotor memblokir Tutup Database | ✓ |
| 6 | Form kotor memblokir Keluar | ✓ |
| 7 | Form dibuka tapi belum disentuh **tidak** memblokir | ✓ |
| 8 | Tombol "Buka" memindahkan fokus, isian utuh | ✓ |
| 9 | Setelah Simpan & Tutup, kedua aksi jalan | ✓ |

Tiga akun uji yang terbuat di `company_000002.sqlite` selama pengujian sudah
dihapus setelah dipastikan tidak dirujuk kolom `*_account_id` mana pun (49 akun,
kembali seperti semula).
