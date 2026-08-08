# Fase 2 — Kelompok B: tambah filter tanggal (8 halaman)

> **✅ Selesai 2026-08-08 — commit `cf4ec72`.** Lihat [§Hasil](#hasil).

**Ini penambahan fitur, bukan perbaikan bug.** Kedelapan halaman sudah mengirim
`status` ke server dengan benar dan tidak menyaring apa pun di browser. Yang
belum ada: UI filter rentang tanggal.

⚠️ **Konfirmasi ke pemilik produk dulu.** Fase 0 dan 1 memperbaiki yang rusak;
fase ini menambah yang belum ada. Bisa jadi tidak semua modul membutuhkannya.

## Prasyarat

Fase 1 selesai **dan sudah dinilai pemilik produk**.

## Cakupan

| Halaman | Kolom tanggal di backend |
|---|---|
| `QuotationListPage` | `quotation_date` |
| `SalesOrderListPage` | `order_date` |
| `DeliveryOrderListPage` | `delivery_date` |
| `ProformaListPage` | `proforma_date` |
| `CustomerDepositListPage` | `deposit_date` |
| `PurchaseRequestListPage` | `request_date` |
| `PurchaseOrderListPage` | `order_date` |
| `PurchaseReturnListPage` | `return_date` |

Backend **sudah siap** menerima `date_from`/`date_to` untuk kedelapannya —
`$listDateColumn` sudah diset dan kolomnya ber-index sejak Fase 0
`list-query-pushdown`. Tidak ada pekerjaan backend.

## Tugas

Tiru bentuk filter tanggal yang sudah ada, jangan merancang yang baru. Dua
contoh yang sudah jalan:

- `JournalListPage` — dua `<Input type="date">` di dalam
  `<FilterSection title="Tanggal">`
- `StockMovementListPage` — pola `dateRange` dengan state `{from, to}`

Pilih **satu** dari keduanya dan pakai konsisten di kedelapan halaman. Catat
mana yang dipilih di commit message.

Per halaman:

1. Tambah state rentang tanggal.
2. Tambah `<FilterSection title="Tanggal">` di sidebar — **di bawah** kotak
   pencarian yang sekarang ada di atas (lihat commit `a1249ee`).
3. Kirim `date_from`/`date_to` ke hook.
4. Ikutkan ke `activeFilterCount` dan ke `onReset` `FilterSidebar`.
5. Reset halaman ke 1 saat tanggal berubah (`00-conventions.md` §3).

## Perhatian khusus

**`activeFilterCount` mudah terlupa.** Kalau tanggal tidak dihitung, badge
jumlah filter aktif akan berbohong dan tombol "Reset" tidak membersihkannya.
Periksa keduanya di tiap halaman.

**`PurchaseRequestListPage`** juga punya filter `department_id`/`project_id`
yang sudah bekerja server-side — jangan diubah.

## Checklist Verifikasi

- [ ] Definition of Done `00-conventions.md` §7 untuk tiap halaman
- [ ] Badge jumlah filter aktif ikut menghitung rentang tanggal
- [ ] Tombol Reset membersihkan rentang tanggal juga
- [ ] Uji minimal 2 halaman dengan data lintas beberapa bulan
- [ ] `npm run build` hijau
- [ ] Backend tidak diubah

## Git Checkpoint

```
feat(list): tambah filter rentang tanggal di 8 halaman daftar

Kedelapan halaman sudah memfilter status server-side tapi belum punya UI
rentang tanggal sama sekali. Backend sudah menerima date_from/date_to sejak
list-query-pushdown; ini melengkapi sisi UI-nya.
```

## Hasil

Selesai 2026-08-08, commit `cf4ec72`. Kedelapan halaman punya filter rentang
tanggal.

**Komponen yang dipilih: `DateRangeFilterSection`**, bukan pola `<Input
type="date">` mentah ala `JournalListPage`. Alasannya ia sudah dipakai 13
halaman lain termasuk seluruh kelompok C, jadi ini yang mayoritas — memilih
pola Journal justru akan menambah varian ketiga.

**Nol perubahan backend**, sesuai prinsip rencana. `$listDateColumn` sudah
diset per modul dan kolomnya ber-index sejak `list-query-pushdown` Fase 0.

**Reset halaman ikut diperluas** ke seluruh kombinasi filter lewat `filterKey`,
sama seperti yang Fase 1 lakukan untuk kelompok C. Rencana tidak memintanya
eksplisit di fase ini, tapi tanpa itu halaman baru saja mewarisi masalah yang
sama.

### Verifikasi

Request yang benar-benar dikirim, 4 halaman lintas dua modul:

| Halaman | Query |
|---|---|
| Penawaran | `sales/quotations?page=1&per_page=25&date_from=2026-01-01` |
| Sales Order | `sales/orders?…&date_from=2026-01-01` |
| Permintaan | `purchase/requests?…&date_from=2026-01-01` |
| Purchase Order | `purchase/orders?…&date_from=2026-01-01` |

**`activeCount` dan Reset diuji khusus** — ini yang ditandai "paling mudah
terlupa" di §Perhatian khusus. Hasilnya: badge `0 → 2` saat dua tanggal diisi,
kembali kosong setelah Reset, dan kedua input benar-benar dikosongkan.

### Catatan desain yang sengaja dibiarkan

Badge menghitung `from` dan `to` sebagai **dua** filter terpisah, bukan satu
rentang. Secara semantik satu rentang tanggal lebih tepat dihitung 1. Tapi 9
halaman kelompok C sudah berperilaku begitu sejak lama, jadi konsistensi
didahulukan — mengubahnya berarti menyentuh 17 halaman untuk perkara kosmetik.
Kalau mau diseragamkan jadi 1, kerjakan sekaligus di semuanya, jangan sebagian.

## Setelah selesai

- [x] Update ledger `README.md`: Fase 2 → `✅ Selesai` + hash commit.
