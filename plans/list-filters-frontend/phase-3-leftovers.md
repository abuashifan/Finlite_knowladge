# Fase 3 — Paginasi COA + sisa temuan

Kumpulan temuan kecil dari audit 2026-08-07 yang berhubungan dengan halaman
daftar tapi bukan soal filter. Ditaruh di sini supaya tidak hilang.

## 3.1 — `CoaListPage` membatasi diri ke 100 baris

**Ini bug, dan diam.**

```tsx
// src/modules/master-data/pages/CoaListPage.tsx
const { data, isLoading } = useCoaList({
  page: 1,          // ← di-hardcode
  per_page: 100,    // ← di-hardcode
  account_type: filterType,
  is_active: filterActive,
  search: search || undefined,
})
```

Tidak ada state halaman, tidak ada `onPaginationChange`. Perusahaan dengan
lebih dari 100 akun **kehilangan sisanya tanpa pemberitahuan** — tidak ada
pesan, tidak ada tombol halaman berikutnya. Daftar akun perusahaan menengah
mudah melewati 100.

Satu-satunya halaman daftar dengan masalah ini; `KontakListPage` dan
`ProdukListPage` sudah berpaginasi normal (diverifikasi lewat grep
`onPaginationChange`/`setPage`).

**Perbaikan:** ikuti pola `ProdukListPage` — state `page`/`perPage`, kirim ke
hook, dan `onPaginationChange` di `DataTable`.

⚠️ **Periksa dulu apakah ada yang bergantung pada "semua akun termuat".** COA
kadang dipakai untuk membangun tampilan pohon (parent/child) yang butuh seluruh
daftar sekaligus. Kalau iya, paginasi biasa akan merusaknya, dan solusinya
berbeda — mungkin endpoint terpisah tanpa paginasi khusus untuk pohon:

```bash
cd /workspace/frontend
rtk grep -rn "parent_id\|tree\|hierarch" src/modules/master-data/pages/CoaListPage.tsx
```

Backend sudah mendukung "kirim semua tanpa paginasi" bila `page`/`per_page`
tidak dikirim sama sekali — lihat kontrak di
`app/Shared/Api/AppliesListQuery::applyListQuery()`. Jadi kalau memang butuh
seluruh pohon, **hilangkan** `page`/`per_page`, jangan naikkan `per_page` jadi
angka besar.

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

## Setelah selesai

1. Update ledger `README.md`: Fase 3 → `✅ Selesai` + hash commit.
2. Tandai rencana ini **SELESAI** di `Finlite_knowladge/README.md` §Plans.
