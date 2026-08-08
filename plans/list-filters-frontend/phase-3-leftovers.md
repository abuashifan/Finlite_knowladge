# Fase 3 — Paginasi COA + sisa temuan

> **✅ Selesai 2026-08-08 — commit `533c409`.** Lihat [§Hasil](#hasil).

Kumpulan temuan kecil dari audit 2026-08-07 yang berhubungan dengan halaman
daftar tapi bukan soal filter. Ditaruh di sini supaya tidak hilang.

## 3.1 — `CoaListPage`: dari batas 100 senyap → paginasi hierarkis

**Diselesaikan dua kali.** Riwayatnya penting supaya tidak diputar balik.

**Keadaan awal (bug):** halaman terkunci `page: 1, per_page: 100` tanpa UI
paginasi. Perusahaan dengan lebih dari 100 akun kehilangan sisanya tanpa
pemberitahuan apa pun.

**Perbaikan pertama (commit `533c409`):** `page`/`per_page` dihapus sama sekali
supaya backend mengirim seluruh baris, karena halaman ini merender pohon
parent/child lewat `buildTree()` dan paginasi biasa memutusnya. Diverifikasi
dengan 150 akun.

⚠️ **Itu memindahkan batas, bukan menghapusnya.** Aman untuk ratusan baris,
menurun perlahan tanpa peringatan saat menembus ribuan — persis kelas masalah
yang dibereskan `list-query-pushdown`.

**Perbaikan kedua (commit backend `fc1dda1`, frontend `745f1d9`):** pemilik
produk memberi screenshot aplikasi acuan yang melakukan **keduanya** — hierarki
berindentasi DAN paginasi. Di acuan itu halaman 1 berakhir di `1104` dan halaman
2 dimulai dari `1104.01`, artinya paginasi diterapkan pada daftar yang **sudah
diratakan dan diurut pre-order**, bukan pada akun induk saja.

Itulah bentuk final sekarang:

- Backend `ChartOfAccountService::hierarchicalQuery()` memakai **recursive CTE**
  untuk menghitung `depth` dan `hierarchy_path` di query time. Tanpa migrasi,
  tanpa kolom turunan tersimpan, tanpa backfill.
- Tiap baris membawa `depth`-nya sendiri, jadi indentasi tetap benar walau
  induknya berada di halaman lain.
- `buildTree()` dan `CoaRow` rekursif **dihapus**; halaman kini memakai
  `DataTable` bersama seperti 21 halaman lain. Tombol lipat/buka juga hilang —
  konsekuensi yang disetujui pemilik produk, dan acuan pun tidak punya.

### Tiga detail yang jangan diubah tanpa membaca alasannya

1. **Pemisah path `char(1)`, bukan titik.** Dengan titik, root `1101.02`
   menyelip **di antara** `1101` dan anaknya `1101.5`. Dibuktikan lewat
   perbandingan langsung kedua pemisah; dikunci
   `test_kode_berprefiks_sama_tidak_mengacaukan_urutan`.
2. **Alias `chart_of_accounts` pada `fromRaw()`** — supaya `where()`/`orderBy()`
   dari `AppliesListQuery` tetap resolve tanpa kualifikasi nama tabel.
3. **`MAX_DEPTH = 10` berpasangan dengan dua penjaga tulis.** Rekursi wajib
   punya batas (kalau tidak, siklus induk membuatnya berputar tanpa henti), dan
   batas itu membuat baris di luarnya LENYAP senyap. Karena itu `create()` dan
   `update()` menolak siklus (`INVALID_PARENT_ACCOUNT`) dan kedalaman berlebih
   (`MAX_ACCOUNT_DEPTH_EXCEEDED`). Jangan naikkan salah satunya tanpa yang lain.

### Kenapa BUKAN kolom `depth`/`hierarchy_path` tersimpan

Ada ≥3 jalur tulis di luar service (dua seeder memakai raw `upsert()`, plus
factory), jadi kolom turunan akan basi diam-diam. Dan `account_code` belum
divalidasi hierarkis — menyimpan path turunan dari kode yang aturannya masih
cair berarti menanam bug kaskade sebelum aturannya ada.

### Perilaku mode datar

Saat **pencarian** atau **sort kolom** aktif, CTE dilewati: daftarnya rata,
`depth` tidak dikirim, frontend memakai indentasi 0. Disengaja — hasil
pencarian adalah himpunan tersebar, jadi anak menjorok tanpa induknya di layar
justru menyesatkan. Bonus: picker akun induk (`coaApi.search`) tidak pernah
membayar biaya rekursi.

### Verifikasi

`tests/Feature/MasterData/ChartOfAccountHierarchyListTest.php` — 11 test,
termasuk skenario acuan (induk halaman 1, anak halaman 2 dengan depth benar),
jebakan prefiks, mode datar, dan kedua penjaga tulis. `tests/Feature/MasterData`
86 hijau.

Diverifikasi di browser: halaman 1 berakhir di induk `1600` (indent 0px),
halaman 2 dimulai dari `1600.01` dan `1600.02` yang **tetap menjorok 20px**
walau induknya tertinggal di halaman sebelumnya. Pencarian → semua indentasi
0px.

## 3.1b — Paginasi palsu di lima halaman master data sederhana

Ditemukan saat mengerjakan Fase 4. Berbeda bentuk dari COA di atas, tapi
sekerabat.

`SatuanPage`, `GudangPage`, `DepartemenPage`, `PaymentTermsPage`, dan
`ProyekPage` memakai:

```tsx
pagination={{ pageIndex: 0, pageSize: 25 }}
onPaginationChange={() => {}}     // ← tidak melakukan apa pun
```

Tombol halaman berikutnya ada tapi mati. Halaman menampilkan apa pun yang
dikirim server tanpa cara berpindah. `KategoriProdukPage` sudah benar
(punya state `page`) dan bisa dipakai sebagai contoh di modul yang sama.

Backend sudah memaginasi dengan benar sejak `list-query-pushdown` Fase 6, dan
API service-nya sudah menerima `page`/`per_page` sejak Fase 4 rencana ini —
tinggal sisi halaman.

## 3.1c — `KategoriProdukPage` tidak punya entri menu

Halamannya ada, route-nya ada (`/master-data/product-categories`), tapi tidak
ada entri di `moduleConfig.ts`. Hanya terjangkau lewat URL langsung.

Delapan master data lain punya entri menu. Perlu keputusan pemilik produk:
tambahkan entri ribbon, atau memang disengaja dikelola dari form produk saja.

## 3.1d — Hapus perusahaan uji `ZZ Uji Filter (dummy)`

Dibuat saat Fase 1 untuk memenuhi uji penentu (butuh > 25 baris; data demo cuma
1–6 per modul). **Company 3**, tenant `company_000003.sqlite`, berisi 60 sales
invoice dummy bernomor `INV-UJI-*`.

Dibiarkan hidup atas keputusan pemilik produk — masih berguna untuk menguji
Fase 2 dan 3 yang juga butuh data banyak. **Hapus setelah Fase 2 dan 3 selesai
diuji**, jangan sebelum itu.

Ia muncul di daftar pilih perusahaan, jadi jangan lupa — kalau tertinggal,
pengguna akan melihat perusahaan bernama "dummy" di produksi.

```bash
rm /workspace/laravel_backend/database/tenants/company_000003.sqlite
# lalu hapus baris terkait di DB pusat: companies id=3, company_users, tenant_databases
```

Backup kedua tenant asli (company 1 & 2) diambil sebelum Fase 1 dimulai; kalau
perlu dipulihkan, lihat commit log Fase 1.

## 3.2 — Searchbox Persediaan belum memakai `ListSearchBar`

Tiga halaman Persediaan (Mutasi, Penyesuaian, Opname Stok) sudah menaruh kotak
pencarian di sidebar, tapi memakai `<Input>` biasa di dalam
`<FilterSection title="Cari">`:

```tsx
<FilterSection title="Cari">
  <Input value={search} onChange={(e) => { setSearch(e.target.value); resetSelection() }} ... />
</FilterSection>
```

Akibatnya: **tidak ada debounce** (request per ketikan huruf) dan tidak ada
tombol bersihkan. Ke-22 halaman lain memakai `ListSearchBar` yang punya
keduanya (debounce 400 ms).

Perbaikannya kecil, tapi perhatikan `resetSelection()` di `onChange` — perilaku
itu harus dipertahankan. `ListSearchBar` memanggil `onChange` dengan nilai
ter-debounce, jadi:

```tsx
onChange={(v) => { setSearch(v); resetSelection() }}
```

## 3.3 — Filter akun untuk Kas & Bank (opsional, butuh keputusan)

`CashBankListParams` mendeklarasikan `cash_bank_account_id`, dan backend sudah
menerimanya untuk Penerimaan Kas, Pengeluaran Kas, dan Rekonsiliasi (Fase 4
`list-query-pushdown`). **UI-nya belum ada.**

Kalau diinginkan, tambahkan dropdown akun kas/bank di sidebar ketiga halaman
itu. Ini fitur baru — konfirmasi dulu.

⚠️ **Transfer Bank dikecualikan** dan itu disengaja: ia punya dua akun
(`from_cash_bank_account_id`, `to_cash_bank_account_id`), sehingga filter
tunggal ambigu — akun asal, tujuan, atau salah satu? Butuh keputusan pemilik
produk sebelum diimplementasikan. Alasannya sudah ditulis di docblock
`BankTransferService::list()`.

## Checklist Verifikasi

- [ ] COA: buat > 100 akun, pastikan halaman 2 terjangkau dan `total` benar
- [ ] COA: kalau ternyata dipakai sebagai pohon, catat keputusannya di file ini
- [ ] Persediaan: mengetik cepat tidak lagi memicu request per huruf
- [ ] Persediaan: `resetSelection()` masih jalan saat pencarian berubah
- [ ] `npm run build` hijau
- [ ] Backend tidak diubah

## Git Checkpoint

```
fix(master-data): paginasi daftar akun, bukan batas 100 baris diam-diam

CoaListPage mengunci page:1 per_page:100 tanpa UI paginasi, sehingga
perusahaan dengan lebih dari 100 akun kehilangan sisanya tanpa pemberitahuan.
```

## Hasil

Selesai 2026-08-08, commit `533c409`. Empat dari lima butir dikerjakan.

### 3.1 COA — jawabannya justru MENGHAPUS paginasi

Rencana menduga COA mungkin dipakai sebagai pohon dan meminta dicek dulu.
**Ternyata benar**: `CoaListPage` punya `buildTree()` yang menyusun
parent/child dan merender `<CoaRow level={n}>` bersarang. Paginasi biasa
justru merusaknya — anak di halaman 2 yang induknya di halaman 1 jadi yatim.

Jadi perbaikannya **bukan** menambah paginasi, melainkan **menghapus
`page`/`per_page` sama sekali** sehingga backend mengirim seluruh baris
(kontrak `AppliesListQuery::applyListQuery()`). Menaikkan `per_page` jadi
angka besar hanya memindahkan batasnya — itu yang dilarang §Prinsip.

`CoaListParams.page`/`per_page` dijadikan opsional, dan alasannya ditulis
panjang di `CoaListPage` supaya tidak ada yang "memperbaikinya" balik jadi
paginasi.

Diverifikasi dengan **150 akun**: semuanya termuat. Sebelumnya terpotong di
100 tanpa pemberitahuan apa pun.

### 3.1b Lima halaman — bug-nya lebih besar dari "tombol mati"

Selain `onPaginationChange={() => {}}`, kelima halaman **tidak mengirim
`page`/`per_page`** sama sekali. Akibatnya respons backend tidak beramplop
paginasi, `data.meta.total` `undefined`, dan `totalRows` **selalu 0** —
jumlah data yang ditampilkan pun salah, bukan cuma tombolnya.

Ini tidak tercatat di rencana; ketahuan saat memeriksa bentuk respons nyata
(`meta` ternyata `[]`, array kosong).

Kini paginasi sungguhan + reset ke halaman 1 saat filter berubah.

### 3.1c & 3.2 — sesuai rencana

Entri menu `Kategori Produk` ditambahkan (ikon `Tags`). Rencana menandainya
"perlu keputusan"; diputuskan **ditambahkan** karena delapan master data lain
punya entri dan halamannya sudah lengkap — ini kelupaan, bukan kesengajaan.

Tiga halaman Persediaan pindah ke `ListSearchBar`. Mengetik 5 huruf kini
menghasilkan **1 request, bukan 5**. `resetSelection()` dipertahankan.

### 3.1d Perusahaan uji — sudah dihapus

`ZZ Uji Filter (dummy)` (company 3) dihapus setelah Fase 2 dan 3 selesai
diuji, sesuai rencana: baris `companies`/`company_users`/`tenant_databases`
di DB pusat dan file `company_000003.sqlite`. Diperiksa dulu seluruh tabel
pusat yang punya kolom `company_id` — hanya dua yang merujuknya.

Diverifikasi: daftar pilih perusahaan kembali berisi dua perusahaan asli, dan
COA PT Maju Jaya tetap 28 baris (tidak tersentuh).

### 3.3 — TIDAK dikerjakan, disengaja

Filter akun Kas & Bank ditandai opsional dan butuh keputusan pemilik produk
sejak rencana ditulis. Tetap terbuka.

### Verifikasi

| Butir | Hasil |
|---|---|
| Kategori Produk | menu muncul, halaman terbuka, `Menampilkan 1–2 dari 2 data` |
| COA | request tanpa `page`/`per_page`; 150 akun tampil semua |
| Satuan | `page=1&per_page=25`; total benar (dulu 0) |
| Mutasi Stok | 5 ketikan = 1 request |

Tanpa console error. `npm run build` hijau. Backend tidak diubah;
`tests/Feature/MasterData` + `tests/Feature/Inventory` 189 hijau.

## Setelah selesai

- [x] Update ledger `README.md`: Fase 3 → `✅ Selesai` + hash commit.
- [x] Tandai rencana ini **SELESAI** di `Finlite_knowladge/README.md` §Plans.
