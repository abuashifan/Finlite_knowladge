# Skema Tier Langganan — Index & Progress Ledger

> **Agent: baca file ini PERTAMA setiap sesi.** Ia menentukan fase mana yang sedang berjalan.
>
> Rencana ini menerapkan skema tier berlangganan yang diberikan pemilik produk
> 2026-08-11 ke dalam aplikasi. **Halaman harga / landing page tidak termasuk** —
> pemilik produk menyatakan itu urusan situs terpisah yang belum dibuat.

## Konteks — kenapa rencana ini ada

Pemilik produk menyerahkan skema tier lengkap (JSON, 4 tier + add-on) dan
bertanya "bagaimana menurutmu". Diskusi 2026-08-11 menghasilkan tiga keputusan
yang mengubah rancangannya, lalu Fase 0 langsung dikerjakan.

Skema aslinya:

| Tier | Perusahaan | User (included) | Add-on user | Catatan |
|---|---|---|---|---|
| Basic | 1 | 3 | ✅ berbayar | UMKM |
| Pro | 3 | 5 | ✅ berbayar | ditandai `popular` |
| Enterprise | 5 | 10 | ✅ berbayar | `customization: limited` |
| Custom | manual | manual | ✅ berbayar | `support: dedicated` |

Plus ~28 flag fitur per tier (`data_import`, `multi_warehouse`,
`transaction_approval`, `budgeting`, `advanced_reports`, `api`,
`marketplace_integration`, `pos_integration`, `user_permission`,
`audit_trail`, …) dan harga yang semuanya masih `null`.

## Keputusan yang sudah diambil

| Topik | Keputusan | Alasan |
|---|---|---|
| Tier Free | **Dipertahankan**, tidak dihapus dan tidak disembunyikan | Pemilik produk akan mempertimbangkannya sebagai media promosi. Juga jaring pengaman: `CompanyQuotaService::DEFAULT_PLAN_CODE = 'free'` memakainya untuk client tanpa paket. |
| Cakupan add-on user | **Per client**, berlaku di **semua** perusahaannya | Keputusan eksplisit pemilik produk. Konsekuensi yang disadari: client Pro (3 perusahaan) yang membeli add-on 5 mendapat 15 slot tambahan secara total, padahal label harganya `per_user`. Alternatif "per perusahaan" ditawarkan dan ditolak. |
| Halaman harga | **Di luar cakupan** | Akan dibuat di landing page terpisah yang belum ada. |
| Siklus penagihan | **Bulanan atau tahunan saja** — enum tertutup dua nilai, tidak ada kuartalan atau seumur hidup. Kolom `plans.monthly_price` dan `yearly_price` sudah ada. |
| Langganan menempel di client | **`subscriptions.company_id` → `user_id`**, satu baris per periode; perpanjangan membuat baris baru sehingga riwayat penagihan terbentuk sendiri. Tabelnya efektif kosong (dua baris demo dari Juni), jadi ini waktu termurah mengubahnya. Rincian di [Fase 3](phase-3-siklus-langganan.md#2a-langganan-pindah-dari-perusahaan-ke-client). |
| Kedaluwarsa | **Kunci penuh** setelah tenggang **7 hari**, pengingat **H-14**, perpanjangan **manual**. Diperlunak dua peredam: tombol buka kunci di area admin, dan akses penuh selama tenggang. |
| Harga tier | **Belum ditentukan** | Skema mengirim `price: null`. Angka lama di seeder dibiarkan; Enterprise diberi 0 sebagai penampung. Kolomnya tidak nullable dan tidak dibaca kode mana pun. |
| Isi tiap tier | **Peta baru, menggantikan daftar fitur di skema asli.** Basic: pembukuan penuh termasuk persediaan satu gudang dan aktiva tetap. Pro: + multi-gudang, jejak audit, laporan tersimpan, banding multi-periode. Enterprise: + anggaran, dimensi departemen & proyek, role kustom. **Terhalang:** impor berkas diminta masuk Pro tapi fiturnya belum ada sama sekali. Rinciannya di [Fase 2](phase-2-peta-tier-dan-peluncuran.md#peta-tier-yang-disetujui). | Skema asli membuat Pro dan Enterprise **identik secara fitur**, sementara aplikasi ternyata sudah memuat kemampuan kelas atas yang tidak disebut sama sekali (dimensi departemen/proyek dengan laporan tersegmentasi). Aktiva tetap sempat diusulkan sebagai gerbang Pro lalu dibatalkan: tanpanya penyusutan tidak tercatat dan laporan keuangan Basic jadi salah. |
| Paket vs permission | **Dua sumbu terpisah, satu pipa.** Paket menentukan perusahaan ini punya fitur apa (mengikat semua orang, owner termasuk); permission menentukan user tambahan boleh menyentuh apa (owner & admin dikecualikan). Keduanya memakai jalur penyaluran yang sama, tapi alasan penolakannya tidak pernah dilebur. | Ditegaskan pemilik produk: *"Budget itu fitur dari tipe client, dan permission user itu tentang peran user tambahan di data perusahaan, bukan user pemilik atau administrator."* Melebur keduanya membuat pesan error salah alamat dan editor role berbohong. |
| Owner memakan slot | **Ya**, seperti sebelumnya | `max_users = 1` pada Free berarti pemilik bekerja sendirian. Kalau owner dikecualikan, angka di paket menyesatkan. Perlu ditulis eksplisit di materi jualan ("termasuk pemilik"). |

## Keadaan terverifikasi 2026-08-11

| Lapis | Keadaan |
|---|---|
| Kuota perusahaan | ✅ Ditegakkan. `CompanyQuotaService` + gerbang di `CompanyController::store()` (`COMPANY_QUOTA_EXCEEDED`, 422). |
| Kuota user | ✅ Ditegakkan. `UserQuotaService`, titik penegakan tunggal di `CompanyUserAssignmentService::assign()`. |
| Add-on user | ✅ Fase 0 (di bawah). |
| Flag fitur | ✅ **Ditegakkan sejak Fase 2 (2026-08-12).** `plans.features` diisi peta tier yang disetujui, `config('plan_features.enforce')` bawaannya `true`. Client Basic/Pro/Enterprise/Custom sekarang benar-benar berbeda kemampuannya. Keempat boolean `plans.can_use_*` tetap **tidak dibaca siapa pun**; peta fitur memakai `plans.features`, bukan mereka. |
| Permission | ✅ **Sudah menjaga hampir semuanya.** 421 dari 441 rute API memakai `permission:` (95,5%); 20 sisanya memang tidak boleh dijaga (health, auth, admin, pemilih perusahaan). Role kustom per perusahaan, override allow/deny per orang, dan 240 izin sudah berjalan. **Inilah tulang yang dipakai Fase 1–2**, bukan gerbang baru. |
| `max_transactions_per_month` | ⚠️ Kolomnya tetap ada, tetap tidak dibaca siapa pun (sengaja tidak dihapus — lihat "Yang sengaja TIDAK dikerjakan"). **Diganti fungsinya** oleh kuota penyimpanan sejak Fase 4 (2026-08-12): `StorageQuotaService` + `storage:measure` harian, ditegakkan sebelum unggahan impor. |
| Siklus langganan | ✅ **Ditegakkan sejak Fase 3 (2026-08-12).** `subscriptions` sekarang ber-scope **client** (`user_id`), satu baris per periode. Kedaluwarsa mengunci penuh di titik login setelah tenggang 7 hari; `SubscriptionService` satu-satunya penulis. **Client lama yang belum di-backfill berstatus `none`, bukan `expired` — tidak terkunci.** Lihat Fase 3 §8.1. |

## Fase

| Fase | Isi | Status |
|---|---|---|
| [0](phase-0-kuota-addon.md) | Angka tier + tier Enterprise + add-on user per client | ✅ **SELESAI 2026-08-11** |
| [1](phase-1-lapis-paket.md) | Lapis paket disisipkan ke jalur permission yang sudah ada — **tanpa menyentuh satu rute pun**, dimatikan saklar | ✅ **SELESAI 2026-08-11** |
| [2](phase-2-peta-tier-dan-peluncuran.md) | Mengisi peta fitur per tier, editor role menyaring, lalu menyalakannya | ✅ **SELESAI 2026-08-12** |
| [3](phase-3-siklus-langganan.md) | Siklus bulanan/tahunan, kedaluwarsa, kunci penuh, tenggang 7 hari | ✅ **SELESAI 2026-08-12** |
| [4](phase-4-kuota-penyimpanan.md) | Kuota penyimpanan per tier, menggantikan batas jumlah transaksi | ✅ **SELESAI 2026-08-12** |
| [5](phase-5-kebersihan-tenant.md) | ⚠️ **Bug aktif** — 53 GB berkas tenant uji bocor di `database/tenants/` | ✅ **SELESAI 2026-08-12** |

**Semua lima fase dari rencana skema tier sudah selesai dikerjakan.** Saklar
paket menyala (`plan_features.enforce` bawaan `true`), siklus langganan
berjalan (`subscriptions` per-client, kunci penuh di login setelah tenggang
7 hari), kuota penyimpanan ditegakkan sebelum unggahan impor, dan kebocoran
berkas tenant test (14 GB saat ditutup) sudah berhenti dengan guard
anti-regresi terpasang. Suite penuh: **1271 test, 0 gagal.**

Satu hal penting dari Fase 3 yang perlu diketahui sebelum menyentuh fase
mana pun lebih lanjut: kunci login hanya benar-benar menahan client yang
**sudah pernah** di-subscribe lewat area admin — client lama yang belum
di-backfill berstatus `none` (belum berlangganan), bukan `expired`, dan
TIDAK terkunci. Backfill massal ke seluruh client lama belum dikerjakan dan
bukan bagian dari janji fase mana pun; itu keputusan operasional pemilik
produk. Detail di
[Fase 3 §8.1](phase-3-siklus-langganan.md#81-keputusan-yang-diambil-saat-eksekusi-none--expired).

Fase 5 dikerjakan **sebelum** Fase 4 (persis urutan yang diminta rancangan
sendiri — Fase 4 punya prasyarat eksplisit ke Fase 5). Deviasi terbesarnya:
mekanisme "redirect ke direktori sementara" yang disarankan rancangan diganti
perbaikan langsung di sumber kebocoran (lima base class test menjangkau
~110 dari ~117 titik) plus guard PHPUnit yang menggagalkan build kalau ada
regresi baru — detail di
[Fase 5 §Hasil eksekusi](phase-5-kebersihan-tenant.md#hasil-eksekusi-2026-08-12).

### Perubahan rancangan 2026-08-11 (sore)

Fase 1–2 versi pertama merancang `FeatureGateService` + middleware `feature:`
yang dipasang di ~19 grup rute, plus hook & guard baru di frontend. **Dibatalkan**
setelah audit rute menunjukkan 95,5% rute sudah dijaga `permission:`. Rancangan
penggantinya menyisipkan lapis paket ke corong permission yang sudah ada:

| | Rancangan lama | Rancangan sekarang |
|---|---|---|
| Middleware baru | `EnsureFeature` | tidak ada |
| Rute disentuh | ~19 grup modul | **0** |
| Kerja frontend | hook + guard + saring `moduleConfig` | hanya editor role |
| Titik perubahan inti | tersebar | satu service |

Dua koreksi fakta ikut dibawa: **role kustom sudah ada** (bukan fitur yang belum
dibangun, seperti ditulis versi pertama), dan **ekspor/impor sama sekali tidak
ada** — kebalikan dari dugaan awal. Rinciannya di
[Fase 2](phase-2-peta-tier-dan-peluncuran.md).

## Yang sengaja TIDAK dikerjakan

- **Halaman harga / landing page** — di luar aplikasi.
- **Gerbang untuk fitur yang belum dibangun** (`api`, `marketplace_integration`,
  `pos_integration`). Menandainya `false` di Basic sah sebagai materi jualan,
  tapi membangun gerbang untuk fitur yang tidak ada hanya menambah kode mati.
- **Membangun ekspor Excel/PDF dan impor data.** Terverifikasi tidak ada di
  backend maupun frontend, padahal skema menandainya `true` di semua tier. Kalau
  mau dibangun, itu rencana tersendiri — menyentuh hampir setiap halaman daftar
  dan laporan. Sampai itu terjadi, keduanya tidak dipetakan ke tier mana pun.
- **Menghapus lalu menulis ulang test suite.** Ditimbang dan ditolak; alasannya
  di [Fase 2](phase-2-peta-tier-dan-peluncuran.md#nasib-test-suite-lama).
- **Add-on perusahaan.** Skema hanya menyediakan `additional_user`. Client Pro
  yang butuh perusahaan ke-4 harus naik ke Enterprise. Kalau nanti berubah,
  bentuknya mengikuti `users.extra_users` dari Fase 0.
- **Menghapus `max_transactions_per_month`.** Tidak dipakai, tapi menghapus
  kolom tidak mendesak dan bukan bagian dari skema ini.

## Catatan yang terbawa dari pekerjaan sebelumnya

Alur undangan (`POST /access/invitations`) masih **stub**: tidak ada endpoint
terima dan tidak ada email. Kalau nanti dibangun, endpoint terimanya **wajib**
lewat `CompanyUserAssignmentService` — itu satu-satunya tempat batas user
ditegakkan, dan melewatinya berarti melubangi kuota.
