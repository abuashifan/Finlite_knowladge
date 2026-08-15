# Phase 4 — Dimensi Revenue di Jurnal Penjualan

> **Fase ini tidak bergantung pada fase mana pun** dan boleh dikerjakan lebih dulu.
> Hasilnya baru terpakai di fase 6.
>
> ⚠️ **Cakupan diperluas — lihat [project-dimension-budgeting-readiness-plan.md](project-dimension-budgeting-readiness-plan.md).**
> Audit lanjutan menemukan kebocoran dimensi yang sama tidak hanya di Sales Invoice (dokumen
> ini), tapi juga Sales Return, Purchase Bill, Purchase Return, hampir seluruh jalur
> `StockMovementJournalService` (COGS, purchase_in, adjustment, opening_stock), dan seluruh
> journal Fixed Asset (capitalization, disposal, depreciation). Diagnosis Sales Invoice di
> dokumen ini tetap akurat dan jadi bagian dari perbaikan P0 di dokumen baru — tapi jangan
> anggap fase 4 ini cukup untuk menutup G11 secara penuh.

## Objective

Membuat baris **pendapatan** di jurnal membawa `department_id` dan `project_id`.

Tanpa ini `Actual Revenue` per proyek selalu 0, dan Project Profitability, Project Margin,
serta Project Cash Flow mustahil dihitung.

Menutup **G11**.

---

## Diagnosa

Audit menemukan bahwa dimensi **sudah** mengalir ke jurnal dari hampir semua sumber. Sales
Invoice adalah satu-satunya pengecualian.

| Sumber jurnal | Meneruskan dimensi? | Bukti |
|---|---|---|
| Cash Payment | ✅ | `CashPaymentService.php:200-201` |
| Cash Receipt | ✅ | `CashReceiptService.php:222-223` |
| Inventory / COGS | ✅ mengelompokkan **per** dimensi | `StockMovementJournalService.php:234-258` |
| Fixed Asset | ✅ | `FixedAssetService.php:471-472` |
| Jurnal manual | ✅ | `JournalLineNormalizer.php:38-39` |
| **Sales Invoice** | ❌ **dibuang** | `SalesInvoiceService.php:451-467` |
| Vendor Bill | ⚠️ dibuang, tapi tidak masalah — lihat di bawah |

`sales_invoice_lines` **sudah punya** kolom `department_id` dan `project_id`
(`2026_05_20_090011_create_sales_invoice_lines_table.php:36-37`), dan dimensi itu diteruskan
rapi dari quotation → order → delivery order → invoice. Datanya ada; yang hilang hanya di
langkah terakhir saat baris jurnal dibentuk.

---

## Existing files affected

### `app/Modules/Sales/Services/SalesInvoiceService.php`

Method `invoiceRevenueJournalLines()` (sekitar baris 451–490). Sekarang:

```php
$revenueGrouped[$revenueAccountId] = ($revenueGrouped[$revenueAccountId] ?? 0.0) + (float) $line->gross_amount;
if ($discountAccountId !== null) {
    $discountGrouped[$discountAccountId] = ($discountGrouped[$discountAccountId] ?? 0.0) + (float) $line->discount_amount;
}
```

Kunci grouping diubah menjadi komposit:

```php
$key = $revenueAccountId.'|'.($line->department_id ?? '').'|'.($line->project_id ?? '');
```

lalu saat membentuk baris jurnal, `department_id` dan `project_id` dipecah kembali dari kunci
dan ikut disertakan. Sama untuk `$discountGrouped`.

`JournalEntryLine` sudah punya kedua kolom di `$fillable`, dan
`$journal->lines()->createMany($lines)` akan menyimpannya tanpa perubahan lain.

Perubahan bedah: **±20 baris di satu method, satu file.**

---

## Modul lain: sengaja tidak diubah

### `VendorBillService::billDebitJournalLines()`

Mengelompokkan per `accountId` saja, membuang dimensi. **Tidak diubah**, karena method itu
hanya menghasilkan baris **Inventory** dan **Fixed Asset Clearing** — keduanya akun neraca yang
tidak pernah masuk anggaran beban.

Beban operasional tidak bisa lewat vendor bill sama sekali: `VendorBillService.php:499`
melempar `PURCHASE_BILL_LINE_CLASSIFICATION_REQUIRED` dengan pesan *"Record other expenses
through Cash/Bank payments"* — dan jalur Cash/Bank sudah meneruskan dimensi dengan benar.
Beban pokok penjualan datang dari `StockMovementJournalService` yang juga sudah benar.

Menyentuhnya berarti melanggar guardrail "jangan refactor modul yang tidak diminta" untuk nol
manfaat.

---

## Database changes

Tidak ada. Kolomnya sudah ada di `sales_invoice_lines` dan `journal_entry_lines`.

## API / service changes

Tidak ada perubahan kontrak. Jurnal yang dihasilkan berbeda isinya, bukan bentuknya.

## Frontend changes

Tidak ada.

---

## Dependencies

Tidak ada.

---

## Risks

| Risiko | Mitigasi |
|---|---|
| Menyentuh modul Sales melanggar semangat "jangan refactor modul tak diminta" | Ruang lingkup dikunci ke **satu method**. Tidak ada perubahan lain di modul Sales. |
| Nominal jurnal berubah | Yang berubah hanya **kunci grouping**, bukan aritmetikanya. Total per akun tetap identik; hanya jumlah barisnya bertambah saat satu akun dipakai beberapa proyek. |
| Jurnal jadi tidak balance | Sisi AR dan pajak tidak disentuh; total kredit pendapatan tetap sama. Test wajib menegaskan `Σdebit = Σkredit`. |
| Jumlah baris jurnal bertambah untuk invoice multi-proyek | Itu memang tujuannya. Pastikan `line_order` tetap berurutan dan `JournalValidationService::validateLines()` tetap lulus (min 2 baris, tidak ada baris nol). |
| Invoice lama yang sudah ter-post tidak ikut berubah | Benar dan disengaja — jurnal bersifat immutable. Project Profitability hanya akurat untuk invoice **setelah** perubahan ini. Catat di dokumen dan di UI Project Summary. |

---

## Testing

Test baru di `tests/Feature/Sales/SalesInvoiceDimensionTest.php`:

- Invoice dengan baris bertanda `project_id` → `journal_entry_lines` pendapatan membawa
  `project_id` yang sama
- Invoice dengan dua baris, proyek berbeda, akun pendapatan **sama** → menghasilkan **dua**
  baris jurnal pendapatan, masing-masing dengan proyeknya
- Invoice dengan diskon bertanda proyek → baris diskon juga membawa dimensi
- Invoice **tanpa** dimensi → jurnal **identik** dengan sebelum perubahan (jumlah baris, akun,
  nominal)
- `Σdebit = Σkredit` di semua kasus di atas
- `department_id` ikut terbawa, tidak hanya `project_id`

Regresi wajib penuh karena menyentuh modul transaksi:

```bash
cd /workspace/laravel_backend
vendor/bin/pint --test
php artisan test tests/Feature/Sales
php artisan test tests/Feature/Reports    # laporan penjualan & P&L tidak berubah angkanya
```

---

## Hasil implementasi — 2026-08-14

Status: **selesai** untuk cakupan dokumen ini (Sales Invoice).

Perubahan bedah persis seperti rencana: **satu method, satu file**
(`SalesInvoiceService::invoiceRevenueJournalLines()`). Kunci grouping berubah dari
`$revenueAccountId` menjadi komposit `akun|dept|proyek`, lalu dipecah kembali saat baris jurnal
dibentuk. Ditambah dua helper privat: `dimensionKey()` dan `parseDimensionKey()`.

`scaleGroupedAmounts()` tidak perlu diubah — ia tidak peduli bentuk kuncinya; docblock-nya saja
yang diperbarui dari `array<int,float>` jadi `array<array-key,float>`.

`VendorBillService` **tidak disentuh**, sesuai §"Modul lain: sengaja tidak diubah".

### Verifikasi

`tests/Feature/Sales/SalesInvoiceDimensionTest.php` — 5 test:
dimensi terbawa ke baris pendapatan · dua proyek pada akun pendapatan sama → **dua** baris ·
baris diskon ikut membawa dimensi · **invoice tanpa dimensi menghasilkan jurnal yang sama
persis seperti sebelumnya** (jaring pengaman utama) · departemen saja sudah cukup untuk memecah
baris. Semua kasus menegaskan `Σdebit = Σkredit`.

`php artisan test tests/Feature/Sales` lulus penuh; `tests/Feature/Reports` tidak berubah.

> ⚠️ `pint --test` pada `SalesInvoiceService.php` gagal — tapi **sudah gagal sebelum perubahan
> ini** (fixer file-wide: `braces_position`, `unary_operator_spaces`, dst.). Tidak dirapikan
> karena aturan "jangan refactor modul yang tidak diminta".

**Cakupan yang belum ditutup:** kebocoran dimensi di Sales Return, Purchase Bill/Return,
`StockMovementJournalService`, dan Fixed Asset — lihat peringatan di kepala dokumen ini dan
`project-dimension-budgeting-readiness-plan.md`. G11 **belum** tertutup penuh.

---

## Acceptance criteria

1. Sales invoice bertanda proyek menghasilkan `journal_entry_lines.project_id` terisi.
2. Invoice tanpa dimensi menghasilkan jurnal yang **byte-for-byte setara** dengan sebelumnya
   (jumlah baris, akun, nominal, urutan).
3. `tests/Feature/Sales` lulus penuh.
4. Laporan P&L dan Trial Balance tidak berubah angkanya.
