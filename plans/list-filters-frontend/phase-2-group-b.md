# Fase 2 — Kelompok B: tambah filter tanggal (8 halaman)

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

## Setelah selesai

Update ledger `README.md`: Fase 2 → `✅ Selesai` + hash commit.
