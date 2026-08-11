# Fase 5 — Gerbang Tier

**Status: ⬜ Belum dikerjakan. Bergantung pada Fase 1–4 dan pada
[subscription-tiers Fase 1](../subscription-tiers/phase-1-lapis-paket.md).**

Menyambungkan importer ke lapis paket. Fase terkecil di rencana ini — hampir
seluruh mekanismenya sudah dibangun di rencana subscription-tiers.

## Dua kunci izin baru

Ditambahkan di `config/permissions.php`:

| Izin | Menjaga | Tier |
|---|---|---|
| `masterdata.import` | Profil kontak, produk, COA (Fase 1) | Basic ke atas |
| `transactions.import` | Profil faktur penjualan, pembelian, jurnal umum (Fase 3–4) | Pro ke atas |

Dipisahkan begini karena tier-nya berbeda. Satu kunci `import` saja tidak cukup —
ia memaksa memilih antara memberi Basic akses ke impor transaksi, atau menahan
impor master data yang justru dibutuhkan client baru.

## Pemasangan

**Rute** — grup impor dari
[Fase 0](phase-0-mesin-impor.md#endpoint) tidak bisa memakai satu izin untuk
semuanya, karena profilnya berbeda tier. Dua pilihan:

1. **Pisahkan rutenya** per kelompok profil (`/imports/master/*` dan
   `/imports/transactions/*`)
2. **Periksa di controller** berdasarkan `profile` yang diminta

Rekomendasi: **yang pertama.** Izin di rute bisa diaudit dengan `grep`;
pemeriksaan di controller tidak. Konsistensi dengan 421 rute lain yang sudah
memakai `permission:` lebih berharga daripada menghemat satu grup rute.

**Peta paket** — dua baris di `config/plan_features.php`:

```php
'data_import'         => ['masterdata.import'],    // sebenarnya terbuka di semua tier
'transaction_import'  => ['transactions.import'],  // Pro ke atas
```

Catatan: karena impor master data terbuka mulai Basic, ia sebenarnya **tidak
perlu dipetakan sama sekali** — prefix yang tidak disebut di peta selalu terbuka.
Mendaftarkannya hanya berguna kalau nanti ada tier yang tidak mendapatkannya.
Lebih bersih: **hanya petakan `transactions.import`.**

**Role preset** — `masterdata.import` masuk ke role yang mengelola master data
(`finance`, `accountant`, `purchasing`, `sales` sesuai cakupannya);
`transactions.import` ke role yang boleh membuat dokumen terkait.
`owner`/`admin` otomatis lewat `*`.

## Memperbarui rencana subscription-tiers

Dua baris ⏳ di
[peta tier](../subscription-tiers/phase-2-peta-tier-dan-peluncuran.md#1-peta-tier-yang-disetujui)
diganti dengan izin sebenarnya:

| Kemampuan | Basic | Pro | Enterprise | Izin |
|---|:---:|:---:|:---:|---|
| Impor master data | ✅ | ✅ | ✅ | *tidak dipetakan* |
| Impor transaksi | — | ✅ | ✅ | `transactions.import` |

Matriks di `PlanFeatureMatrixTest` ikut bertambah dua baris.

## Test

- `masterdata.import` terbuka di ketiga tier
- `transactions.import`: Basic → 403 `FEATURE_NOT_IN_PLAN`; Pro & Enterprise → 200
- **Owner client Basic tetap ditolak** untuk impor transaksi
- Client Basic tetap bisa mengimpor kontak dan produk
- Kolom dimensi di berkas jurnal ditolak untuk client Pro (dari
  [Fase 4](phase-4-pembelian-dan-jurnal.md#dimensi--bersinggungan-dengan-tier))

## Risiko

- **Menyalakan gerbang impor sebelum importernya matang** membuat client Pro
  membayar untuk fitur yang belum stabil. Fase ini dikerjakan **terakhir**,
  setelah Fase 3–4 terbukti jalan dengan data nyata.
