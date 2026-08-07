# Fase 0 — Fondasi: tipe status multi-nilai

**Halaman diubah: 0.** Fase ini hanya membuka jalan supaya Fase 1 tidak perlu
berbohong ke type checker.

## Kenapa perlu

UI filter status adalah **multi-select** (`filterStatuses: string[]`), dan
backend menerima `?status=draft,posted`. Tapi tipenya enum tunggal:

```ts
export interface SalesInvoiceListParams {
  status?: SalesInvoiceStatus   // ← 'draft' | 'posted' | ...
}
```

`filterStatuses.join(',')` menghasilkan `string`, bukan salah satu anggota enum.
Tiga halaman Persediaan sudah menyiasatinya:

```ts
status: filterStatuses.length > 0 ? filterStatuses.join(',') as StockMovementStatus : undefined
```

Cast itu **berbohong**: `'draft,posted'` bukan `StockMovementStatus`. Kalau
dibiarkan, Fase 1 akan menyalin kebohongan yang sama ke 9 halaman lagi.

## Tugas

### 0.1 — Longgarkan tipe `status` di params daftar

Untuk **params daftar saja** (bukan tipe dokumen atau payload), ubah:

```ts
status?: SalesInvoiceStatus
```

menjadi:

```ts
/** Satu status, atau beberapa dipisah koma (mis. "draft,posted"). */
status?: string
```

File yang terdampak — verifikasi ulang dengan grep, jangan percaya daftar ini
mentah-mentah:

```bash
cd /workspace/frontend
rtk grep -rn "  status?:" src/modules/*/types/*.ts
```

Per audit 2026-08-07, yang berupa **params daftar**:

| File | Interface |
|---|---|
| `sales/types/salesInvoice.types.ts` | `SalesInvoiceListParams` |
| `cash-bank/types/cashBank.types.ts` | `CashBankListParams` |
| `inventory/types/stockMovement.types.ts` | params mutasi stok |
| `inventory/types/stockAdjustment.types.ts` | params penyesuaian stok |
| `inventory/types/stockOpname.types.ts` | params opname |
| `purchase/types/goodsReceipt.types.ts` | params penerimaan barang |
| `purchase/types/purchaseOrder.types.ts` | params PO |
| `purchase/types/purchaseRequest.types.ts` | params PR |
| `accounting/types/journalEntry.types.ts` | params jurnal |

⚠️ **Jangan** mengubah `status` pada tipe **dokumen** (mis. `SalesInvoice.status`)
— di sana enum sempit justru benar dan menjaga `DocumentStatusBadge`.

⚠️ `master-data/types/proyek.types.ts` dan `fixed-assets/types/*` muncul di
grep tapi **di luar cakupan**: proyek difilter server-side lewat kolom `status`
miliknya sendiri, dan Aktiva Tetap tidak termasuk 22 halaman daftar rencana ini.

### 0.2 — Buang cast bohong yang sudah ada

Setelah 0.1, tiga halaman Persediaan bisa dibersihkan:

```bash
rtk grep -rn "join(',') as " src/modules/
```

Harus jadi kosong. Ini satu-satunya perubahan halaman di fase ini, dan sifatnya
menghapus kebohongan, bukan mengubah perilaku.

### 0.3 — Putuskan nasib `due_from` / `due_to`

`SalesInvoiceListParams` menjanjikan keduanya; backend tidak pernah
menerimanya (`00-conventions.md` §6). **Rekomendasi: hapus dari tipe** — grep
dulu untuk memastikan tidak ada pemakai:

```bash
rtk grep -rn "due_from\|due_to" src/
```

Kalau ada pemakainya, berarti ada UI yang mengirim filter yang diabaikan
diam-diam — catat sebagai temuan dan naikkan ke pemilik produk sebelum
menghapus.

## Checklist Verifikasi

- [ ] `npx tsc --noEmit` bersih
- [ ] `rtk grep -rn "join(',') as " src/modules/` kosong
- [ ] `npm run build` hijau
- [ ] Backend tidak diubah
- [ ] Uji cepat di browser: filter status multi-pilih di **Mutasi Stok** (sudah
      server-side sejak dulu) masih bekerja — ini regresi paling mungkin dari
      fase ini

## Git Checkpoint

```
refactor(types): izinkan status multi-nilai di params daftar

Tipe params daftar memakai enum status tunggal padahal UI-nya multi-select dan
backend menerima comma-separated. Tiga halaman Persediaan menyiasatinya dengan
`as StockMovementStatus` yang berbohong ke type checker; cast itu dihapus.

Tipe status pada dokumen tidak diubah -- di sana enum sempit memang benar.
```

## Setelah selesai

Update ledger `README.md`: Fase 0 → `✅ Selesai` + hash commit.
