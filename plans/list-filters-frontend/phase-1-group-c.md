# Fase 1 — Kelompok C: 9 halaman ke server-side

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

## Setelah selesai

1. Update ledger `README.md`: Fase 1 → `✅ Selesai` + hash commit.
2. **Minta pemilik produk mencoba salah satu halaman** dengan data > 25 baris
   sebelum lanjut ke Fase 2.
