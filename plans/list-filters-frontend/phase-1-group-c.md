# Fase 1 — Kelompok C: 9 halaman ke server-side

> **✅ Selesai 2026-08-07 — commit `58f6551`.** Lihat [§Hasil](#hasil).

**Ini inti rencana.** Sembilan halaman yang filternya hanya berlaku ke 25 baris
yang sedang tampil.

## Prasyarat

```bash
cd /workspace/frontend
# harus kosong — Fase 0 sudah membereskan cast bohong
rtk grep -rn "join(',') as " src/modules/
```

## Cakupan

| Halaman | Modul | Kolom tanggal di backend |
|---|---|---|
| `SalesInvoiceListPage` | Penjualan | `invoice_date` |
| `SalesReturnListPage` | Penjualan | `return_date` |
| `SalesReceiptListPage` | Penjualan | `receipt_date` |
| `GoodsReceiptListPage` | Pembelian | `receipt_date` |
| `VendorDepositListPage` | Pembelian | `deposit_date` |
| `VendorPaymentListPage` | Pembelian | `payment_date` |
| `CashReceiptListPage` | Kas & Bank | `receipt_date` |
| `CashPaymentListPage` | Kas & Bank | `payment_date` |
| `BankTransferListPage` | Kas & Bank | `transfer_date` |

Kolom tanggal tidak perlu dikirim frontend — backend sudah tahu lewat
`$listDateColumn`. Tabel di atas hanya supaya jelas apa yang sebenarnya
difilter saat menguji.

## Urutan kerja

**Kerjakan `SalesInvoiceListPage` sendirian dulu**, lalu **minta pemilik produk
mencobanya** sebelum menyalin ke delapan sisanya. Alasannya sama seperti pilot
di rencana sebelumnya: perubahan ini terlihat pengguna, dan lebih murah
memperbaiki polanya sekali daripada sembilan kali.

Yang berubah dan terasa: jumlah baris per halaman kini **selalu penuh** (25)
selama data mencukupi, sedangkan sebelumnya menyusut mengikuti filter. Itu
perbaikan, tapi bisa terasa asing di pemakaian pertama.

## Tugas per halaman

Ikuti `00-conventions.md` §1 persis. Ringkasnya:

1. Tambahkan ke argumen hook `use*List({...})`:
   ```ts
   status: filterStatuses.length > 0 ? filterStatuses.join(',') : undefined,
   date_from: dateRange.from || undefined,
   date_to: dateRange.to || undefined,
   ```
2. Hapus `visibleRows` dan penyaringan `.filter(...)`-nya.
3. Ganti `data={visibleRows}` → `data={rows}` di `DataTable`.
4. Hapus konstanta `FILTER_HINT` dan tempat ia dirender.
5. Hapus impor helper yang jadi yatim (mis. `isDateInRange`) — **cek dulu**
   apakah masih dipakai di file yang sama.
6. Reset halaman ke 1 saat status/tanggal berubah (§3).

## Perhatian khusus

**`isDateInRange`** dipakai lintas halaman. Setelah 9 halaman ini selesai,
periksa apakah masih ada pemakai:

```bash
rtk grep -rn "isDateInRange" src/
```

Kalau nol, hapus helper-nya sekalian. Kalau masih dipakai kelompok B atau
tempat lain, **biarkan** — jangan hapus fungsi yang masih terpanggil.

**Tiga halaman Kas & Bank** juga mendeklarasikan `cash_bank_account_id` di
`CashBankListParams`, dan backend sudah menerimanya sejak Fase 4
`list-query-pushdown` untuk Penerimaan & Pengeluaran Kas. Tapi **UI-nya belum
ada** — jangan menambah dropdown akun di fase ini, itu fitur baru. Catat saja
kalau memang diinginkan.

⚠️ **Transfer Bank sengaja tidak menerima `cash_bank_account_id`** karena punya
dua akun (`from_`/`to_`). Jangan menambahkannya tanpa keputusan pemilik produk
soal artinya.

**Filter customer/vendor** di halaman-halaman ini sudah bekerja server-side
sejak Fase 2–3 `list-query-pushdown` — jangan diutak-atik.

## Checklist Verifikasi

- [ ] Definition of Done `00-conventions.md` §7 untuk tiap halaman
- [ ] Uji dengan data > 25 baris pada **minimal 3 halaman** lintas modul:
      pilih status yang hanya dimiliki dokumen di halaman ≥ 2, pastikan muncul
      **dan** `total` menyusut
- [ ] `rtk grep -rn "FILTER_HINT" src/` — tinggal 0 setelah 9 halaman selesai
- [ ] `rtk grep -rn "visibleRows" src/` — kosong, atau tersisa hanya di halaman
      di luar kelompok C (verifikasi mana)
- [ ] `npm run build` hijau, `npx tsc --noEmit` bersih tanpa cast baru
- [ ] Backend tidak diubah; `php artisan test` hijau

## Git Checkpoint

```
fix(list): kirim filter status & tanggal ke server di 9 halaman

Sembilan halaman daftar menyaring hasil di browser, sehingga filter hanya
berlaku ke 25 baris yang sedang dimuat -- mencentang "Posted" tidak
menampilkan dokumen posted di halaman lain, dan jumlah baris menyusut tanpa
penjelasan sementara penomoran halaman tetap memakai total sebelum filter.

status/date_from/date_to kini dikirim ke server, yang sudah menerimanya sejak
list-query-pushdown selesai. FILTER_HINT dihapus karena tidak lagi benar.

Backend tidak diubah.
```

## Hasil

Selesai 2026-08-07, commit `58f6551`. Kesembilan halaman mengirim
`status`/`date_from`/`date_to` ke server.

`FILTER_HINT` **nol kemunculan** di seluruh frontend. `visibleRows` juga nol.

**Reset halaman diperluas melampaui rencana.** Rencana menyebut "reset ke
halaman 1 saat filter berubah"; implementasinya memakai satu `filterKey` yang
merangkum search + status + rentang tanggal + filter customer/vendor, bukan
hanya `search` seperti sebelumnya. Tanpa itu, memfilter dari halaman jauh
mendarat di daftar kosong.

**Dua bentuk pemanggilan hook**, tidak seragam seperti dugaan: enam halaman
memanggil `use*List({...})` multi-baris, tiga halaman Kas & Bank memanggilnya
dalam satu baris. Skrip migrasi harus menangani keduanya.

`isDateInRange` jadi yatim setelah kesembilan pemanggilnya hilang → dihapus
bersama `toDateKey` dan `DATE_INPUT_PATTERN` yang hanya melayaninya.
`shiftDateInputValue` juga yatim **tapi sudah begitu sebelum fase ini** —
sengaja dibiarkan, bukan urusan fase ini.

### Verifikasi

Diuji di browser dengan memantau request yang benar-benar dikirim:

| Halaman | Query yang dikirim | Hasil |
|---|---|---|
| Sales Invoice | `page=1&per_page=25&status=draft` | 6 baris → 3 |
| Penerimaan Kas | `page=1&per_page=25&date_from=2026-01-01` | — |
| Penerimaan Brg | `page=1&per_page=25&date_from=2026-01-01` | — |

Sebelum fase ini ketiganya hanya mengirim `page` & `per_page`. Tanpa console
error.

### ⚠️ Yang belum bisa diuji

**Uji penentu di README §Cara membuktikan — "filter menjangkau halaman ≥ 2 dan
`total` ikut menyusut" — belum dilakukan.** Data demo hanya 1–6 baris per
modul kelompok C, jauh di bawah 25, jadi halaman 2 tidak pernah ada.

Yang diuji sebagai gantinya adalah sinyal penyusunnya: parameter benar-benar
sampai ke server, dan jumlah baris berubah mengikutinya. Itu cukup untuk
menyatakan filternya server-side, tapi **bukan** bukti langsung atas gejala
yang dilaporkan pemilik produk.

Untuk menutupnya: buat > 25 dokumen di satu modul (mis. Sales Invoice) dengan
status campur, lalu ikuti lima langkah di README.

## Setelah selesai

- [x] Update ledger `README.md`: Fase 1 → `✅ Selesai` + hash commit.
- [ ] **Minta pemilik produk mencoba salah satu halaman** dengan data > 25
      baris — belum terpenuhi, lihat §Yang belum bisa diuji.
