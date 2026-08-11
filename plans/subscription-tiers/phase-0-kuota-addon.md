# Fase 0 — Angka Tier & Add-on User

**Status: ✅ SELESAI 2026-08-11**

Menyelaraskan angka tier dengan skema pemilik produk, menambahkan tier
Enterprise yang belum ada, dan membangun add-on "user tambahan".

## Yang berubah

### Angka tier

`database/seeders/PlanSeeder.php`:

| Tier | Sebelum | Sesudah |
|---|---|---|
| Free | 1 perusahaan / 1 user | *(tidak berubah)* |
| Basic | 1 / 3, `can_use_inventory = false` | 1 / 3, `can_use_inventory = **true**` |
| Pro | 3 / **10** | 3 / **5** |
| Enterprise | *(tidak ada)* | **5 / 10** — tier baru |
| Custom | 1 / 10 (cadangan) | *(tidak berubah)* |

`can_use_inventory` pada Basic dibalik ke `true` mengikuti skema
(`inventory: true` di Basic). Aman tanpa efek perilaku: keempat boolean
`can_use_*` tidak dibaca kode mana pun (lihat README, "Keadaan terverifikasi").

Harga Enterprise diisi 0 — pemilik produk belum menentukan harga, kolomnya tidak
nullable, dan tidak ada kode yang membacanya.

### Add-on user

Kolom baru `users.extra_users` (`unsignedInteger`, default 0, non-nullable) —
`database/migrations/2026_08_11_000005_add_extra_users_to_users_table.php`.

Non-nullable dan default 0 dengan sengaja: berbeda dari `company_quota` /
`user_quota`, add-on **tidak punya keadaan "ikut paket"**. Yang ada hanya
"belum beli".

Batas efektif per perusahaan menjadi:

```
batas = (angka manual tier Custom ATAU max_users paket) + users.extra_users
```

Add-on **berlaku penuh di setiap perusahaan**, bukan satu jatah yang dibagi.
Client Pro (5 user) dengan add-on 5 mendapat 10 user di masing-masing dari 3
perusahaannya.

## File yang disentuh

### Backend

| File | Perubahan |
|---|---|
| `database/migrations/2026_08_11_000005_add_extra_users_to_users_table.php` | **Baru.** Kolom `extra_users`. |
| `app/Shared/Models/User.php` | `extra_users` di `$fillable` + cast `integer`. |
| `app/Shared/Subscription/UserQuotaService.php` | `limitFor(Company)` dipecah jadi `limitForOwner(User)` (publik, baru) + `baseLimitFor()` + `addOnFor()` privat. `summaryFor()` menambah kunci `extra_users`. |
| `app/Modules/Companies/Services/CompanyUserAssignmentService.php` | Pesan error menyebut add-on terpisah dari paket. Tanpa itu, angka batasnya tidak cocok dengan `max_users` paket dan terbaca seperti bug. |
| `app/Modules/Admin/Controllers/ClientUserController.php` | Aturan validasi `extra_users` (`0..999`); disimpan di `extraAttributes()` **di luar** blok pembersih tier Custom; `plans()` mengurutkan Custom paling bawah. |
| `app/Modules/Admin/Services/ClientUserService.php` | `usersLimitFor()` privat **dihapus**, diganti `UserQuotaService::limitForOwner()`. Payload menambah `extra_users`. |
| `database/seeders/PlanSeeder.php` | Angka tier + tier Enterprise. |

Dua hal yang perlu diingat saat menyentuh ulang berkas-berkas ini:

1. **Add-on tidak dibersihkan saat paket berubah.** Blok di `extraAttributes()`
   yang menge-null-kan `company_quota` / `user_quota` untuk tier non-Custom
   **tidak boleh** mencakup `extra_users` — add-on dibeli terpisah dan tetap
   berlaku lintas tier.
2. **Duplikasi hitungan sudah dihapus.** Sebelumnya `ClientUserService` punya
   salinan sendiri logika batas user, sehingga angka di layar admin bisa
   berbeda dari yang ditegakkan. Sekarang keduanya memanggil service yang sama.
   Jangan hidupkan lagi salinan itu.

### Frontend

| File | Perubahan |
|---|---|
| `src/types/admin.types.ts` | `extra_users: number` di `ClientUser`; `extra_users?: number \| null` di `ClientProfileFields`. |
| `src/modules/admin/schemas/clientSchema.ts` | `extra_users: quota(0)`. |
| `src/modules/admin/pages/AdminClientFormPage.tsx` | Tab **Add-ons** berisi input beneran + ringkasan hitungan. `TAB_FIELDS` menambah `addons: ['extra_users']`, sehingga `TabKey` tidak perlu lagi mendaftarkan `addons` terpisah dan tab itu ikut mendapat titik-merah error. Tombol Simpan kini muncul di tab Add-ons juga. |
| `src/modules/admin/pages/AdminClientsPage.tsx` | Kolom "Maks User" diberi penanda `⁺` + tooltip pemecahan paket vs add-on. |

Catatan UI: nol ditampilkan sebagai kolom kosong, bukan angka `0` — "belum beli
add-on" lebih jelas terbaca begitu. Ringkasan di tab Add-ons juga menghitung
dampak totalnya (`add-on × jumlah perusahaan`) supaya keputusan "per client"
terlihat angkanya sebelum disimpan.

## Test

`tests/Feature/Companies/UserQuotaTest.php` — 2 test baru:

- `test_add_on_adds_slots_to_every_company_of_the_client` — paket 2 user +
  add-on 2, dua perusahaan; membuktikan batasnya 4 di **masing-masing**, bukan
  2 slot tambahan yang dibagi berdua.
- `test_add_on_stacks_on_top_of_custom_tier_quota` — angka manual tier Custom
  pun ditambah add-on, tidak digantikan.

`tests/Feature/Admin/AdminClientManagementTest.php` — 1 test baru:

- `test_add_on_survives_plan_change_and_raises_users_limit` — mengunci perbedaan
  perilaku dari kuota khusus: add-on **tidak** ikut terhapus saat paket diganti.

## Verifikasi yang dijalankan

```
php artisan test                    → 1174 test, 1169 lulus, 5 skip, 0 gagal
./vendor/bin/pint --dirty           → lulus
npm run build (tsc -b && vite)      → 0 error
npx eslint                          → bersih
```

Pada database dev, setelah `migrate` + `db:seed --class=PlanSeeder`:

```
free        Free        perusahaan=1  user=1    active
basic       Basic       perusahaan=1  user=3    active
pro         Pro         perusahaan=3  user=5    active
custom      Custom      perusahaan=1  user=10   active
enterprise  Enterprise  perusahaan=5  user=10   active
```

Penurunan Pro dari 10 → 5 user diperiksa dampaknya ke data dev: tidak ada
perusahaan yang jadi melebihi batas (`#1 PT Maju Jaya` 1/5, `#2 PT Nusantara
Dagang Sejahtera` 2/5).

## Yang belum dikerjakan di fase ini

Tab Add-ons hanya memuat **satu** add-on, sesuai skema (`additional_user`).
Kalau nanti ada add-on kedua, bentuk tabnya perlu berubah dari sepasang field
menjadi daftar — dan `ClientProfileFields` ikut melebar.
