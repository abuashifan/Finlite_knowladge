# Fase 8 — Cleanup + Architecture Tests

**Goal**: Hapus alias bridge, ganti semua referензi namespace lama → baru, hapus folder kosong, tambah architecture test penegak batas modul.

Prasyarat baca: `00-conventions.md` §3, §7, §9.

## Prasyarat
```bash
cd laravel_backend
test -d app/Modules/Sales/Models && echo "Fase 7 OK" || echo "STOP: selesaikan Fase 7"
php artisan test 2>&1 | tail -3
```

---

## A. Ganti semua referensi namespace lama → baru
Alias akan dihapus, jadi tiap referensi lama harus diganti nyata. Untuk tiap prefix lama, grep lalu ganti (di `app/ tests/ database/ routes/ bootstrap/ config/`):

```bash
grep -rn "App\\\\Support\\\\"              app/ tests/ database/ routes/ bootstrap/ config/
grep -rn "App\\\\Traits\\\\"               app/ tests/ database/
grep -rn "App\\\\Contracts\\\\"            app/ tests/ database/
grep -rn "App\\\\Enums\\\\"                app/ tests/ database/
grep -rn "App\\\\Exceptions\\\\ApiException" app/ tests/ database/ bootstrap/
grep -rn "App\\\\Data\\\\Reports\\\\"      app/ tests/ database/
grep -rn "App\\\\Http\\\\Middleware\\\\"   app/ tests/ bootstrap/
grep -rn "App\\\\Http\\\\Controllers\\\\Api\\\\" app/ tests/ routes/
grep -rn "App\\\\Http\\\\Requests\\\\"     app/ tests/
grep -rn "App\\\\Services\\\\"             app/ tests/ database/
grep -rn "App\\\\Models\\\\"               app/ tests/ database/ config/
```
Peta target: gunakan tabel di `00-conventions.md` §4 (Shared) + §1 (modul) + Fase 7 (model). Ganti persis (case-sensitive). **Termasuk factory files** di `database/factories/` (mereka referensi model).

> Tip: kerjakan satu prefix, jalankan `php artisan test`, commit. Lebih mudah rollback daripada mengganti semua sekaligus.

## B. Hapus AliasServiceProvider
1. Hapus `App\Providers\AliasServiceProvider::class` dari `bootstrap/providers.php`.
2. `rm app/Providers/AliasServiceProvider.php`.
3. `php artisan test` — jika ada `Class not found`, berarti ada referensi lama yang terlewat di langkah A. Perbaiki.

> **morphMap tetap dipertahankan** di `SharedServiceProvider::boot()` — kolom `*_type` di DB tenant lama masih menyimpan FQCN lama, morphMap yang menerjemahkannya. Jangan hapus. (Opsional lanjutan: data migration untuk menormalkan `*_type` ke alias pendek — di luar scope fase ini.)

## C. Hapus folder kosong / stub
Setelah dipastikan kosong:
```bash
rm -rf app/Support app/Traits app/Contracts app/Enums app/Data
rm -rf app/Http/Requests app/Http/Middleware
rm -rf app/Http/Controllers/Api          # base app/Http/Controllers/Controller.php TETAP
rm -rf app/Services
rm -rf app/Models/Tenant                 # jika kosong
rmdir app/Models 2>/dev/null || true     # hanya jika kosong (central sudah ke Shared)
find app/Shared -name README.md -delete  # stub lama
find app/Modules -name .gitkeep -delete  # Providers/.gitkeep jika folder sudah berisi/atau tak dipakai
```
Sisakan `app/Exceptions/` hanya jika Laravel butuh (cek `bootstrap/app.php` — di Laravel 11+ handler ada di bootstrap; `ApiException` sudah pindah ke Shared, folder boleh dihapus jika kosong).

## D. Optimasi & lint
```bash
composer dump-autoload -o
php artisan config:clear && php artisan route:clear
./vendor/bin/pint            # WAJIB per AGENTS.md backend (Pint check)
```

## E. Architecture tests (penegak batas modul)
Tambah `tests/Feature/Architecture/ModuleBoundariesTest.php` (PHPUnit/Pest sesuai konvensi repo; sudah ada `ModuleRoutesTest.php` sebagai contoh). Aturan yang diuji:
1. **Tidak ada namespace lama tersisa** — assert `app/` tidak mengandung `App\Http\Controllers\Api\`, `App\Services\`, `App\Support\`, `App\Models\Tenant\`, `App\Traits\`, `App\Data\`, `App\Contracts\`, `App\Enums\` (via file scan / `Finder`).
2. **Modul tidak meng-import internal modul lain** — file di `App\Modules\A` tidak boleh `use App\Modules\B\{Services|Controllers|Requests}` (Models & kontrak boleh, atau lewat integration service). Sesuaikan allowlist dengan integrasi nyata (Sales↔Inventory integration service).
3. **Shared tidak bergantung ke Modules** — `App\Shared\*` tidak boleh `use App\Modules\*`. **Pengecualian**: `App\Shared\TransactionLifecycle\Checkers\*` (mereferensi model domain — lihat `00-conventions.md` §4). Beri allowlist eksplisit.
4. **Route isolation** — tetap gunakan `ModuleRoutesTest` yang ada; pastikan jumlah route & middleware tak berubah.

Jika arsitektur test #2/#3 gagal karena coupling nyata yang belum bisa dilepas, catat sebagai `->group('known-coupling')` / TODO, jangan paksa refactor besar di fase ini.

## Checklist Verifikasi
- [ ] `grep` di langkah A → semua bersih (tak ada namespace lama di `app/ tests/ database/ routes/ bootstrap/ config/`).
- [ ] `AliasServiceProvider` terhapus; `bootstrap/providers.php` bersih.
- [ ] `composer dump-autoload -o` tanpa error.
- [ ] `php artisan test` hijau (baseline).
- [ ] `./vendor/bin/pint --test` bersih.
- [ ] `php artisan route:list --path=api | wc -l` = baseline; middleware kritis utuh.
- [ ] Architecture test baru lulus.
- [ ] Folder lama (`app/Support`, `app/Services`, `app/Http/Controllers/Api`, dst) hilang.

## Git Checkpoint
```
refactor(cleanup): Fase 8 — remove alias bridge, purge legacy namespaces, add architecture tests
```
Update ledger (Fase 8 → ✅). **Modularisasi selesai.**

## Definition of Done
Tidak ada namespace lama, tidak ada alias bridge, folder lama terhapus, architecture test menjaga batas modul, seluruh test + Pint hijau. `config/` & `database/migrations/` sengaja tetap (lihat `00-conventions.md` §6). morphMap dipertahankan permanen.
