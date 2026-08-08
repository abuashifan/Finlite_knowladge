# List Filters Frontend — Index & Progress Ledger

> **Agent: baca file ini PERTAMA setiap sesi.** Ia menentukan fase mana yang sedang berjalan.
>
> Rencana ini membuat filter di halaman daftar **berlaku ke seluruh data**, bukan
> hanya ke 25 baris yang kebetulan sedang tampil. Backend sudah siap menerima
> parameternya sejak `list-query-pushdown` selesai; yang kurang tinggal frontend
> mengirimkannya.

## Hubungan dengan rencana sebelumnya

`plans/list-query-pushdown/` (✅ selesai 2026-08-07) memperbaiki **beban**:
server tidak lagi menghidrasi seluruh tabel untuk mengirim satu halaman.

Rencana ini memperbaiki **cakupan**: filter yang dipilih pengguna sekarang
diterapkan database ke seluruh tabel, bukan disaring browser dari halaman yang
sudah terlanjur dimuat.

Dua masalah berbeda, dua perbaikan berbeda. Urutannya sengaja begini — backend
harus bisa menerima `status`/`date_from`/`date_to` dulu, dan sekarang bisa.

## Masalah yang diselesaikan

Sembilan halaman daftar menyaring hasil **di browser**:

```ts
// SalesInvoiceListPage.tsx — pola yang sama di 9 halaman
const { data } = useSalesInvoiceList({ page, per_page: 25, search, customer_id })
const visibleRows = rows.filter((invoice) => {
  const matchesStatus = filterStatuses.length === 0 || filterStatuses.includes(invoice.status)
  const matchesDate = isDateInRange(invoice.date, dateRange.from, dateRange.to)
  return matchesStatus && matchesDate
})
```

`status`, `date_from`, dan `date_to` tidak pernah dikirim ke server.

**Akibatnya:** mencentang "Posted" hanya menampilkan dokumen posted **yang ada
di halaman 1**. Dokumen posted di halaman 2 tidak muncul. Lebih buruk lagi,
jumlah baris yang tampil jadi lebih sedikit dari 25 tanpa penjelasan, dan
penomoran halaman tetap menghitung baris yang sudah disaring keluar.

Ini tercatat jujur di UI sebagai `FILTER_HINT`:

> *"Filter multi-select dan tanggal berlaku pada data halaman yang sedang dimuat."*

Setelah rencana ini, konstanta itu dihapus — bukan karena disembunyikan,
melainkan karena tidak lagi benar.

## Peta keadaan — audit 2026-08-07

22 halaman daftar, tiga kelompok. **Jangan pakai angka "9 halaman" dari
`list-query-pushdown/00-conventions.md` §8 sebagai satu-satunya acuan** —
angka itu hanya menghitung kelompok C.

### Kelompok A — sudah benar (5 halaman)

Mengirim `status` + `date_from` + `date_to` ke server. **Jangan disentuh**;
pakai sebagai contoh acuan.

`JournalListPage`, `StockMovementListPage`, `StockAdjustmentListPage`,
`StockOpnameListPage`, `VendorBillListPage`

### Kelompok B — status benar, belum punya filter tanggal (8 halaman)

Mengirim `status` ke server dengan benar. Tidak menyaring di browser. Yang
kurang: **UI filter tanggal belum ada sama sekali** — jadi ini penambahan
fitur, bukan perbaikan bug.

`QuotationListPage`, `SalesOrderListPage`, `DeliveryOrderListPage`,
`ProformaListPage`, `CustomerDepositListPage`, `PurchaseRequestListPage`,
`PurchaseOrderListPage`, `PurchaseReturnListPage`

### Kelompok C — rusak, menyaring di browser (9 halaman)

Punya UI filter status **dan** tanggal, tapi tidak mengirim satu pun ke server.

`SalesInvoiceListPage`, `SalesReturnListPage`, `SalesReceiptListPage`,
`GoodsReceiptListPage`, `VendorDepositListPage`, `VendorPaymentListPage`,
`CashReceiptListPage`, `CashPaymentListPage`, `BankTransferListPage`

### Terpisah — 9 halaman master data dengan Aktif/Nonaktif

Ketiga kelompok di atas soal **status dokumen** (draft/posted/void) dan rentang
tanggal. Master data punya sumbu yang berbeda: `is_active`, tanpa siklus
dokumen. Fiturnya ada di 9 halaman dengan 9 bentuk berbeda, diseragamkan ke
format `KontakListPage` di [Fase 4](phase-4-active-status.md).

Tiga di antaranya (COA, Kontak, Produk) juga masuk hitungan 22 halaman di atas;
enam sisanya (Satuan, Gudang, Departemen, Proyek, Syarat Bayar, Kategori
Produk) halaman sederhana tanpa filter status dokumen, jadi tidak masuk
kelompok A/B/C.

## Kabar baik dari audit

Tiga hal membuat pekerjaan ini jauh lebih kecil dari dugaan awal:

1. **Tipe parameter sudah menerima semuanya.** `SalesInvoiceListParams`,
   `CashBankListParams`, dan kawan-kawan sudah punya `status`, `date_from`,
   `date_to`. Tidak perlu mengubah kontrak API client.
2. **Backend sudah menerima dan menghormatinya**, termasuk status
   comma-separated (`draft,posted`) — diperbaiki di Fase 1 `list-query-pushdown`.
3. **Filter Aktif/Nonaktif sudah server-side di tiga halaman utama** (COA,
   Kontak, Produk), lengkap dengan opsi "Semua". Diverifikasi 2026-08-07.

> ⚠️ **Koreksi.** Poin 3 semula berbunyi *"Pola D tidak ada lagi — sudah
> selesai"*. **Terlalu cepat disimpulkan.** Audit lanjutan atas permintaan
> pemilik produk menemukan bahwa fitur aktif/nonaktif ada di **9 halaman**,
> bukan 3, dan tidak ada dua yang bentuknya sama: Produk bahkan tidak bisa
> mengubah status sama sekali dari daftar, sementara enam halaman lain tidak
> punya filter statusnya. Yang benar: tiga halaman utama sudah **memfilter**
> server-side; penyeragaman fiturnya belum dikerjakan. Lihat
> [Fase 4](phase-4-active-status.md).
>
> Pelajarannya sama dengan rencana sebelumnya: memeriksa satu aspek (di sini
> "apakah `is_active` dikirim?") lalu menyimpulkan seluruh fitur beres.

## Progress Ledger

| Fase | Judul | File | Halaman | Status | Commit |
|------|-------|------|---------|--------|--------|
| 0 | Fondasi: tipe status multi-nilai | `phase-0-types.md` | — | ✅ Selesai | 2cdee59 |
| 1 | Kelompok C → server-side | `phase-1-group-c.md` | 9 | ✅ Selesai | 58f6551 |
| 2 | Kelompok B → tambah filter tanggal | `phase-2-group-b.md` | 8 | ⬜ Belum | — |
| 3 | Paginasi COA + sisa temuan | `phase-3-leftovers.md` | 1 | ⬜ Belum | — |
| 4 | Seragamkan Aktif/Nonaktif ke format Kontak | `phase-4-active-status.md` | 9 | ✅ Selesai | 36712f6 |

> Status yang boleh: `⬜ Belum`, `🔄 Berjalan`, `✅ Selesai`.

**Fase 0 wajib lebih dulu** — Fase 1 mengirim status multi-pilih sebagai
`"draft,posted"`, dan tipe saat ini (`status?: SalesInvoiceStatus`) tidak
mengizinkannya tanpa `as` yang berbohong ke type checker.

## Prinsip desain

- **Backend tidak diubah.** Kalau ternyata butuh perubahan backend, berhenti
  dan catat — berarti ada asumsi rencana ini yang salah.
- **Satu pola, disalin apa adanya.** Kelompok C seragam; setelah satu halaman
  selesai dan dinilai, delapan sisanya mengikuti persis.
- **Hapus `FILTER_HINT` hanya bersamaan dengan perbaikannya**, jangan lebih
  cepat. Selama filter masih client-side, peringatan itu jujur dan berguna.
- **Reset ke halaman 1 saat filter berubah.** Kalau pengguna di halaman 5 lalu
  memfilter sampai tersisa 2 halaman, ia akan melihat daftar kosong. Halaman
  kelompok A sudah menangani ini untuk `search`; pola yang sama berlaku ke
  status dan tanggal.
- **Jangan menambah `LIMIT` diam-diam** — sama seperti rencana sebelumnya,
  paginasi harus jujur.

## Cara membuktikan perbaikannya bekerja

Bukan "filternya jalan" (itu sudah tampak jalan sejak dulu, di satu halaman),
melainkan **filternya menjangkau halaman lain**:

1. Cari modul yang datanya > 25 baris. Kalau tidak ada, buat dulu.
2. Catat `total` tanpa filter.
3. Pilih status yang hanya dimiliki dokumen di halaman ≥ 2.
4. **Sebelum perbaikan:** hasil 0 baris, `total` tetap angka penuh.
5. **Sesudah perbaikan:** dokumen itu muncul, dan `total` ikut menyusut.

Poin ke-5 yang menentukan. Kalau `total` tidak berubah, berarti filternya masih
tidak sampai ke server.

## Referensi

- Rencana pendahulu: `plans/list-query-pushdown/README.md` (✅ selesai)
- Trait backend yang menerima parameternya: `app/Shared/Api/AppliesListQuery.php`
- Contoh halaman yang sudah benar: `src/modules/accounting/pages/JournalListPage.tsx`
- Aturan frontend: `/workspace/frontend/AGENTS.md`
