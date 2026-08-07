# Fase 4 — Seragamkan fitur Aktif/Nonaktif di 9 halaman master data

**Halaman acuan: `KontakListPage`.** Permintaan pemilik produk 2026-08-07:
semua halaman daftar yang punya fitur aktif/nonaktif mengikuti formatnya.

⚠️ Ini **tentang `is_active`**, bukan `void`. Halaman transaksi (invoice,
jurnal, dsb.) memakai siklus status dokumen dengan void/batal — **di luar
cakupan fase ini**, dan memang seharusnya berbeda.

## Peta keadaan — audit 2026-08-07

Sembilan halaman punya fitur aktif/nonaktif. **Tidak ada dua yang sama.**

| Halaman | Filter Aktif/Nonaktif/Semua | Badge status | Kirim `is_active` | Ubah status dari list | Pola ubah status |
|---|---|---|---|---|---|
| **Kontak** (acuan) | ✅ | ✅ | ✅ | ✅ | `bulkActions` DataTable |
| Akun (COA) | ✅ | ✅ | ✅ | ✅ | tombol toolbar custom |
| Produk | ✅ | ✅ | ✅ | ❌ | **tidak ada** |
| Satuan | ❌ | ❌ | ❌ | ✅ | aksi per baris |
| Gudang | ❌ | ✅ | ❌ | ✅ | aksi per baris |
| Departemen | ❌ | ✅ | ❌ | ✅ | aksi per baris |
| Proyek | ❌ | ❌ | ❌ | ✅ | aksi per baris |
| Syarat Bayar | ❌ | ✅ | ❌ | ✅ | aksi per baris |
| Kategori Produk | ❌ | ✅ | ❌ | ✅ | aksi per baris |

Tiga masalah yang terlihat pengguna:

1. **Produk tidak bisa diaktifkan/dinonaktifkan dari daftar sama sekali.**
   `useProdukMutations()` sudah menyediakan `activate`/`deactivate`, endpoint
   backend-nya ada, tapi halamannya tidak pernah memanggilnya. Satu-satunya
   entitas dengan celah ini.
2. **Enam halaman tidak punya filter Aktif/Nonaktif/Semua** dan tidak mengirim
   `is_active`, jadi baris nonaktif tercampur tanpa bisa disaring.
3. **Satuan dan Proyek bahkan tidak menampilkan status** — pengguna tidak bisa
   tahu suatu baris aktif atau tidak sampai membuka formulirnya.

## Format acuan (`KontakListPage`)

Empat unsur. Semua halaman harus punya keempatnya.

### 1. Konstanta opsi filter

```tsx
const ACTIVE_OPTIONS = [
  { value: true, label: 'Aktif' },
  { value: false, label: 'Nonaktif' },
  { value: undefined, label: 'Semua' },
]
```

### 2. State default "hanya aktif"

```tsx
// Default: hanya tampilkan kontak aktif. Pilih "Semua" di filter Status untuk menampilkan semuanya.
const [filterActive, setFilterActive] = useState<boolean | undefined>(true)
```

### 3. Dikirim ke server, bukan disaring di browser

```tsx
const { data } = useKontakList({ page, per_page: perPage, is_active: filterActive, ... })
```

Backend kesembilan entitas **sudah menerima `is_active`** — diverifikasi saat
Fase 6 `list-query-pushdown`. Tidak ada pekerjaan backend.

### 4. Ubah status lewat `bulkActions` DataTable

```tsx
{
  id: 'bulk-deactivate',
  label: 'Nonaktifkan Terpilih',
  permission: 'contacts.deactivate',
  onClick: (ids) => runBulkStatusChange(ids, false, (id) => deactivate.mutateAsync(id)),
}
```

`runBulkStatusChange` di Kontak melakukan dua hal yang **wajib ditiru**:

- **menyaring baris yang sudah dalam status tujuan** (`k.is_active !== targetActive`)
  sehingga tidak mengirim request sia-sia;
- **konfirmasi sebelum menonaktifkan** (`confirm('Nonaktifkan N kontak terpilih?')`),
  tapi tidak sebelum mengaktifkan — menonaktifkan yang berisiko.

## Tugas

### 4.1 — `ProdukListPage`: tambahkan ubah status

Paling kecil dan paling terasa. Halamannya sudah punya filter, badge, dan
paginasi; tinggal `bulkActions` seperti Kontak. Ambil `activate`/`deactivate`
dari `useProdukMutations()` yang sudah ada.

### 4.2 — `CoaListPage`: pindah ke `bulkActions`

Sekarang memakai dua `<Button>` custom di toolbar (baris ~278–281) yang
memanggil `handleBulkActivate`/`handleBulkDeactivate`. Perilakunya benar,
bentuknya yang berbeda.

⚠️ **COA dirender sebagai pohon** (`node.is_active`), bukan tabel datar seperti
Kontak. Periksa dulu apakah `DataTable` di halaman ini benar-benar mendukung
`bulkActions` dengan struktur pohonnya. **Kalau tidak**, jangan dipaksakan —
pertahankan tombol toolbar, samakan saja label, ikon, konfirmasi, dan
pengecekan permission-nya dengan Kontak. Catat keputusannya di file ini.

⚠️ Halaman ini juga kena Fase 3.1 (terkunci 100 baris tanpa paginasi).
Kerjakan **setelah** Fase 3, atau sekalian bersamaan — jangan dua kali sentuh.

### 4.3 — Enam halaman sederhana: tambahkan filter + badge

`SatuanPage`, `GudangPage`, `DepartemenPage`, `ProyekPage`,
`PaymentTermsPage`, `KategoriProdukPage`.

Per halaman:

1. Tambah `ACTIVE_OPTIONS` + state `filterActive` (default `true`).
2. Kirim `is_active: filterActive` ke hook.
3. Tambah `<SingleCheckboxFilter title="Status">` di sidebar.
4. Tambah kolom badge `<ActiveStatusBadge isActive={...} />` — **Satuan dan
   Proyek belum punya sama sekali**.
5. Ganti aksi per baris jadi `bulkActions`, atau pertahankan keduanya bila
   aksi per baris memang berguna di sana — **konfirmasi ke pemilik produk**.

⚠️ **Lima dari enam halaman ini belum punya `FilterSidebar`** (hanya
`ProyekPage` yang punya). Filter Aktif/Nonaktif format Kontak tinggal di
sidebar, jadi kelimanya perlu sidebar dulu. **Ini pendorong biaya terbesar
fase ini** — bukan filternya, melainkan kerangka yang menampungnya.

Kalau ingin lebih murah, alternatifnya menaruh filter di toolbar atas halaman.
Tapi itu berarti format-nya **tidak** sama dengan Kontak, yang bertentangan
dengan permintaan. **Putuskan dulu sebelum mulai**, jangan setengah jalan.

## ⚠️ Perubahan perilaku yang terlihat pengguna

Keenam halaman itu sekarang menampilkan **semua** baris, termasuk yang
nonaktif. Setelah fase ini, default-nya berubah jadi **hanya aktif**.

Artinya: pengguna yang terbiasa melihat satuan/gudang/departemen nonaktif di
daftar akan merasa datanya "hilang". Padahal cuma tersaring, dan bisa
dikembalikan lewat opsi "Semua".

Ini konsisten dengan Kontak/COA/Produk dan memang tujuan penyeragaman — tapi
**beri tahu pemilik produk sebelum rilis**, jangan sampai dilaporkan sebagai
data hilang.

## Perhatian khusus

**Nama permission berbeda per entitas.** Kontak memakai
`contacts.deactivate`. Jangan menyalinnya mentah-mentah — cek nama yang benar
tiap entitas:

```bash
cd /workspace/laravel_backend
rtk grep -rn "deactivate" app/Modules/MasterData/Routes/
```

Kalau ada entitas yang belum punya permission aktivasi terpisah, **jangan
mengarang** — naikkan sebagai temuan.

**Jangan pakai `filterActive` untuk menyaring di browser.** Seluruh rencana ini
tentang memindahkan penyaringan ke server; jangan menambah pola lama di fase
terakhirnya.

## Checklist Verifikasi

- [ ] Kesembilan halaman punya filter Aktif/Nonaktif/Semua
- [ ] Kesembilan mengirim `is_active` ke server (bukan menyaring di browser)
- [ ] Kesembilan menampilkan badge status di kolom
- [ ] Kesembilan bisa mengubah status dari daftar — termasuk **Produk**
- [ ] Konfirmasi muncul sebelum menonaktifkan, tidak sebelum mengaktifkan
- [ ] Baris yang sudah dalam status tujuan tidak ikut dikirim
- [ ] Permission dicek per entitas dengan nama yang benar
- [ ] `activeFilterCount` dan tombol Reset menghitung filter status
- [ ] `npm run build` hijau, `npx tsc --noEmit` bersih
- [ ] Backend tidak diubah; `php artisan test` hijau
- [ ] Uji di browser: nonaktifkan satu baris di **tiap** halaman, pastikan ia
      hilang dari default dan muncul lagi saat memilih "Semua"

## Git Checkpoint

```
feat(master-data): seragamkan fitur aktif/nonaktif di 9 halaman daftar

Kesembilan halaman punya fitur ini dengan sembilan bentuk berbeda. Diseragamkan
mengikuti KontakListPage: filter Aktif/Nonaktif/Semua di sidebar, is_active
dikirim ke server, badge status di kolom, dan perubahan status lewat
bulkActions dengan konfirmasi sebelum menonaktifkan.

Produk sebelumnya tidak bisa diaktifkan/dinonaktifkan dari daftar sama sekali
walau hook dan endpoint-nya sudah ada. Satuan dan Proyek tidak menampilkan
status. Enam halaman tidak punya filter status sehingga baris nonaktif
tercampur tanpa bisa disaring.

PERUBAHAN PERILAKU: enam halaman itu kini default hanya menampilkan baris
aktif, sebelumnya semua. Pilih "Semua" di filter Status untuk kembali.
```

## Setelah selesai

Update ledger `README.md`: Fase 4 → `✅ Selesai` + hash commit.
