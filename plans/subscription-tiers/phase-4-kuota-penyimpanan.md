# Fase 4 — Kuota Penyimpanan

**Status: ⬜ Belum dikerjakan.**

Diminta pemilik produk 2026-08-11: *"buat skema untuk besarnya kapasitas hardisk
atau alokasi cloud-nya."*

Fase ini menggantikan `max_transactions_per_month` yang dibuang (keputusan
2026-08-11: **tidak ada batas jumlah transaksi**). Membatasi jumlah transaksi
menghukum client yang paling aktif — justru yang paling bernilai. Kalau biaya
perlu dikendalikan, batasnya lebih tepat di penyimpanan.

## Pengukuran nyata, bukan taksiran

Diukur langsung dari dua tenant di mesin dev, 2026-08-11:

| | Ukuran | Tabel | Baris jurnal |
|---|---|---|---|
| `company_000001.sqlite` | 1,7 MB | 78 | 66 |
| `company_000002.sqlite` | 1,9 MB | 78 | 361 |

Dua angka penting yang bisa ditarik:

- **Dasar per perusahaan ≈ 1,7 MB.** Itu biaya skema 87 migrasi sebelum satu
  transaksi pun dicatat. Setiap perusahaan baru langsung memakan segitu.
- **Pertumbuhan ≈ 0,7 KB per baris jurnal.** Selisih 0,2 MB untuk ~300 baris
  jurnal.

## Proyeksi untuk kasus pemakaian yang diminta

Kasus yang mendorong rencana data-import: **500 faktur per hari**.

Satu faktur menghasilkan kira-kira: baris faktur + 3 baris barang + entri jurnal
+ 4 baris jurnal + mutasi piutang ≈ **3 KB**.

| | Per bulan (22 hari kerja) | Per tahun |
|---|---|---|
| 500 faktur/hari | 11.000 faktur ≈ **33 MB** | ≈ **400 MB** |
| 100 faktur/hari | 2.200 faktur ≈ 7 MB | ≈ 80 MB |
| 20 faktur/hari | 440 faktur ≈ 1,3 MB | ≈ 16 MB |

Ditambah berkas impor: satu berkas 1.000 baris ≈ 150 KB, satu per hari, masa
simpan 30 hari ≈ **5 MB tetap**.

**Kesimpulannya: penyimpanan bukan biaya yang menakutkan.** Client Pro paling
sibuk sekalipun tumbuh di bawah 500 MB setahun. Yang menjadikannya biaya adalah
**jumlah perusahaan × dasar 1,7 MB**, bukan volume transaksi.

## Skema yang diusulkan

| | Basic | Pro | Enterprise | Custom |
|---|---|---|---|---|
| Perusahaan | 1 | 3 | 5 | manual |
| **Kuota penyimpanan per perusahaan** | **1 GB** | **2 GB** | **5 GB** | manual |
| Total maksimum per client | 1 GB | 6 GB | 25 GB | manual |
| Masa simpan berkas impor | 30 hari | 30 hari | 90 hari | manual |

Angkanya sengaja **longgar** — sekitar dua kali lipat proyeksi paling sibuk.
Alasannya: kuota penyimpanan bukan alat jualan di sini, melainkan **pagar
terhadap pemakaian anomali** (client yang mengunggah berkas raksasa berulang
kali, atau kesalahan yang menulis jutaan baris). Kuota yang ketat akan lebih
sering menghukum pemakaian normal daripada menghemat biaya.

## Cara menegakkannya

**Yang diukur:** ukuran berkas SQLite tenant + total berkas impor yang tersimpan
untuk perusahaan itu.

**Kapan diperiksa:** bukan tiap request — itu pemborosan. Cukup:

1. **Sebelum menerima unggahan impor** — satu-satunya jalur yang bisa menambah
   penyimpanan secara melonjak.
2. **Sekali sehari** lewat command terjadwal, yang mencatat ukuran tiap tenant ke
   database pusat.

Kolom `tenant_databases` adalah tempat yang wajar untuk menyimpan hasil
pengukuran harian (`size_bytes`, `measured_at`).

**Saat terlampaui:** tahan penambahan data baru dengan pesan yang jelas, **jangan
kunci akses baca**. Sejalan dengan aturan yang sudah berlaku di seluruh rencana
ini — yang ditahan adalah pertumbuhan, bukan yang sudah ada.

## Area admin

Daftar client menampilkan pemakaian penyimpanan per perusahaan, dengan penanda
saat mendekati batas. Itu juga yang memberi kamu data nyata untuk menyesuaikan
angka di atas setelah beberapa bulan — angka sekarang adalah tebakan terdidik
dari dua tenant yang isinya masih sedikit.

## Prasyarat kebersihan ⚠️

Sebelum kuota apa pun ditegakkan, **kebocoran berkas test harus ditutup lebih
dulu**. Terukur 2026-08-11: `database/tenants/` memuat **33.790 berkas, 53 GB**,
di mana 4.471 di antaranya dibuat pada hari itu juga oleh test suite. Setiap
tenant uji menjalankan 87 migrasi lalu meninggalkan berkas 1,7 MB yang tidak
pernah dihapus.

Itu bukan masalah kuota client — itu masalah kebersihan mesin — tapi ia mengotori
setiap pengukuran penyimpanan dan harus beres sebelum fase ini bermakna. Rincian
dan perbaikannya ada di
[Fase 5](phase-5-kebersihan-tenant.md).

## Alokasi server — bahan hitung kasar

Dengan skema di atas, satu server dengan **100 GB** ruang tenant menampung
kira-kira:

| Bauran client | Perkiraan |
|---|---|
| 100% Basic (1 perusahaan) | ~1.000 client *(dibatasi kuota, bukan pemakaian nyata)* |
| Realistis (pemakaian nyata, bukan kuota) | **beberapa ribu client** |

Perbedaan besar antara keduanya menegaskan poin di atas: kuota adalah pagar, dan
pemakaian sebenarnya jauh di bawahnya. Untuk perencanaan kapasitas, pakai
pengukuran harian dari command terjadwal — bukan penjumlahan kuota.
