# 00 — Conventions (Baca Sekali per Sesi)

Referensi bersama untuk semua fase. Ditulis sekali di sini supaya file fase tidak mengulang.

---

## 1. Aturan namespace & PSR-4

`composer.json` sudah memetakan `"App\\": "app/"` secara rekursif. Artinya **folder apa pun di bawah `app/` otomatis ter-autoload** selama namespace-nya mengikuti path. `App\Shared\...` dan `App\Modules\...` langsung resolve **tanpa perlu mengubah `composer.json`**. Jangan tambah entri PSR-4 baru.

> Satu-satunya saat menyentuh autoload: `composer dump-autoload -o` di Fase 8 (opsional, untuk optimasi). Tidak wajib di fase lain — file baru langsung terbaca.

### Transform namespace modul (Fase 1–6)

Regular, tiga baris ini berlaku untuk **setiap** modul `{X}`:

| Lama (path & namespace) | Baru (path & namespace) |
|---|---|
| `app/Http/Controllers/Api/{X}/*` — `App\Http\Controllers\Api\{X}` | `app/Modules/{X}/Controllers/*` — `App\Modules\{X}\Controllers` |
| `app/Http/Requests/{X}/*` — `App\Http\Requests\{X}` | `app/Modules/{X}/Requests/*` — `App\Modules\{X}\Requests` |
| `app/Services/{X}/*` — `App\Services\{X}` | `app/Modules/{X}/Services/*` — `App\Modules\{X}\Services` |

Subfolder di dalamnya dipertahankan (mis. `Services/Sales/Concerns/` → `Modules/Sales/Services/Concerns/`, namespace `App\Modules\Sales\Services\Concerns`).

### Transform namespace Shared (Fase 0)

Capability-first (lihat tabel §4). Pola: `App\Support\{Cap}\X` / `App\Services\{Cap}\X` → `App\Shared\{Cap}\X`.

---

## 2. Langkah baku memindahkan satu file

Untuk tiap file yang dipindah:

1. `git mv <src> <dest>` (pakai `git mv`, bukan copy — menjaga history).
2. Edit baris `namespace ...;` di file itu sesuai tujuan.
3. **Jangan** langsung memburu semua referensi ke class ini di seluruh codebase — itulah gunanya alias (lihat §3). Cukup update referensi **di dalam file yang ikut dipindah pada fase yang sama** (mis. controller yang me-`use` request yang juga pindah).
4. Referensi lintas-modul yang belum dimigrasi dibiarkan; alias yang menjembatani.

> Pengecualian yang **wajib** diedit walau pakai alias (karena bukan class resolution biasa):
> - `bootstrap/app.php` (import & middleware alias — lihat Fase 0)
> - `bootstrap/providers.php` (daftar provider)
> - File `Routes/api.php` modul (baris `use ...Controller` — `class_alias` tetap bekerja, tapi route file sebaiknya rapi; update saat modulnya dimigrasi)

---

## 3. Mekanisme alias bridge

Dibuat di Fase 0: `app/Providers/AliasServiceProvider.php`, didaftarkan di `bootstrap/providers.php`.

```php
namespace App\Providers;

use Illuminate\Support\ServiceProvider;

class AliasServiceProvider extends ServiceProvider
{
    /** Alias nama-lama → implementasi-baru. Bertambah tiap fase, DIHAPUS di Fase 8. */
    public const ALIASES = [
        // 'App\\Support\\Api\\ApiResponseBuilder' => \App\Shared\Api\ApiResponseBuilder::class,
    ];

    public function register(): void
    {
        foreach (self::ALIASES as $legacy => $current) {
            if (! class_exists($legacy, false) && ! interface_exists($legacy, false)) {
                class_alias($current, $legacy);
            }
        }
    }
}
```

Aturan penting:
- **Arah alias**: `class_alias(CLASS_BARU, 'Nama\\Lama')`. Argumen pertama harus class yang **sudah ada** (yang baru). Argumen kedua string nama lama.
- Didaftarkan di `register()` (bukan `boot()`) supaya alias siap sebelum class lain di-autoload.
- Cek `class_exists(..., false)` mencegah bentrok bila autoloader sempat menemukan file lama.
- Tiap fase menambahkan entri ke `ALIASES`. File fase mencantumkan daftar persisnya.
- `AliasServiceProvider` **harus terdaftar setelah** `SharedServiceProvider` di `bootstrap/providers.php`.

> **Trait tidak bisa di-`class_alias`.** Jika sebuah trait dipindah (mis. `App\Traits\ApiResponse`), file yang `use` trait itu harus diupdate langsung di fase yang sama (grep + ganti). File fase menandai trait dengan ⚠️.

---

## 4. Peta Shared (tujuan Fase 0)

Struktur akhir `app/Shared/`. Config **tidak** ikut (tetap di `config/`, lihat §6) — kolom Config hanya menandai kepemilikan.

| Folder Shared (`App\Shared\...`) | Sumber | Config terkait |
|---|---|---|
| `Api/` | `Support/Api/*` (2), `Traits/ApiResponse.php` ⚠️ | `api_errors.php` |
| `Audit/` | `Services/Audit/*` (1), `Support/Audit/*` (3) | — |
| `DocumentNumbering/` | `Services/DocumentNumbering/*` (1), `Support/DocumentNumbering/*` (2) | `document_numbers.php` |
| `TransactionLifecycle/` | `Services/Transactions/*` (14, kecuali SourceDocumentPickerService), `Support/Transaction/*` (6), `Support/Revision/*` (2), `Traits/HasTransactionLifecycle.php` ⚠️, `Traits/HasRevisionTracking.php` ⚠️ | `transaction_lifecycle.php` |
| `TransactionLifecycle/Contracts/` | `Contracts/Transactions/*` (2) | — |
| `TransactionLifecycle/Checkers/` | `Services/Transactions/Checkers/*` (6) | — |
| `SourceDocument/` | `Http/Controllers/Api/Transactions/SourceDocumentPickerController.php`, `Services/Transactions/SourceDocumentPickerService.php`, `Support/SourceLink/*` (4), `Traits/HasSourceLink.php` ⚠️ | `source_links.php` |
| `AccountMapping/` | `Services/AccountMapping/*` (2), `Support/AccountMapping/*` (3) | `account_mappings.php` |
| `Permission/` | `Services/Permissions/*` (3) | `permissions.php` |
| `Tenant/` | `Services/Tenant/*` (4) | `tenant.php` |
| `Validation/` | `Services/Validation/*` (1) | — |
| `DataRetention/` | `Services/DataRetention/*` (2), `Support/DataRetention/*` (3) | `data_retention.php` |
| `Reports/Data/` | `Data/Reports/*` (16) | — |
| `Reports/` | `Support/Reports/ReportVisibilityMode.php` (1), `Traits/HasReportVisibility.php` ⚠️ | `report_visibility.php` |
| `Enums/` | `Enums/SourceType.php` (1) | — |
| `Exceptions/` | `Exceptions/ApiException.php` (1) | — |
| `Http/Middleware/` | `Http/Middleware/*` (2) | — |
| `Http/Controllers/` | `Http/Controllers/Api/HealthController.php` (1) | — |
| `Models/` | *(Fase 7)* 18 central model | — |
| `Providers/` | *(baru)* `SharedServiceProvider.php` | — |

> Catatan clash nama: `Enums/SourceType.php` dan `Support/SourceLink/SourceType.php` sama-sama bernama `SourceType`. Tetap terpisah (`App\Shared\Enums\SourceType` vs `App\Shared\SourceDocument\SourceType`) — jangan digabung.
>
> Catatan coupling: `TransactionLifecycle/Checkers/*` mereferensikan model domain (Sales/Purchase/Inventory/Journal/CashBank). Ini diterima untuk sekarang (mereka mengimplementasi contract bersama). Fase 8 architecture-test memberi mereka pengecualian.

---

## 5. Yang TIDAK ikut ke Shared / modul

Tetap di lokasi sekarang di semua fase (Laravel memuatnya dari path default; alias menjembatani referensi):

- `app/Console/Commands/*` (9) — command tetap di sini. Referensi ke class yang pindah dijembatani alias.
- `app/Http/Controllers/Controller.php` — base controller, tetap.
- `database/migrations/**` — lihat §6.
- `config/**` — lihat §6.
- `routes/api.php` — tetap sebagai aggregator (`require` tiap `app/Modules/{X}/Routes/api.php`). Tidak diganti ke provider-based routing.

---

## 6. Kenapa Config & Migration TIDAK dipindah

- **Config**: memindah `config/foo.php` ke modul mengubah key `config('foo.*')` kecuali pakai `mergeConfigFrom` dengan hati-hati. Risiko tinggi, manfaat kecil. Semua file config **tetap di `config/`**. Kepemilikan didokumentasikan (tabel §4 & file fase) untuk navigasi saja.
- **Migration central**: tetap di `database/migrations/` + `database/migrations/central/`. Pemuatan dipindah dari `AppServiceProvider::boot()` ke `SharedServiceProvider::boot()` (`loadMigrationsFrom(database_path('migrations/central'))`). Laravel juga auto-load root `database/migrations/`.
- **Migration tenant**: `database/migrations/tenant/` adalah **source of truth** multi-tenant, dimuat per-tenant oleh `TenantMigrationService`. **Jangan dipindah/diubah** di fase mana pun.

---

## 7. Ranjau untuk Fase 7 (Model) — baca sebelum menyentuh model

Fase 0–6 tidak menyentuh model. Dua alasan model ditunda:

### 7a. Morph map
`ActivityLog` (central) dan `TenantAuditLog` (tenant) memakai `morphTo()`, dan **tidak ada `enforceMorphMap`** di codebase → kolom `*_type` menyimpan **nama class penuh** (mis. `App\Models\Tenant\JournalEntry`). Memindah namespace model **memutus data morph lama** kecuali dipasang morph map yang memetakan string lama → class baru:

```php
// SharedServiceProvider::boot() (ditambah di Fase 7)
use Illuminate\Database\Eloquent\Relations\Relation;

Relation::morphMap([
    'App\\Models\\Tenant\\JournalEntry' => \App\Modules\Journal\Models\JournalEntry::class,
    // ... satu baris per model yang jadi target morph
]);
```

Fase 7 mencantumkan grep untuk menemukan semua model yang jadi target morph.

### 7b. Factory resolution
Model yang pakai `HasFactory` di-resolve factory-nya oleh Laravel dengan mengupas prefix `App\Models\`. Setelah model pindah ke `App\Shared\Models\` / `App\Modules\{X}\Models\`, resolusi **putus**. Tiap model ber-factory butuh override:

```php
protected static function newFactory()
{
    return \Database\Factories\Tenant\JournalEntryFactory::new();
}
```

Factory saat ini: `database/factories/UserFactory.php` + `database/factories/Tenant/*`. Factory file **tidak dipindah**; hanya tambah `newFactory()` di model yang perlu.

---

## 8. Perintah verifikasi standar

Dipakai di Checklist Verifikasi tiap fase. Jalankan dari root `laravel_backend`.

```bash
# Baseline test — CATAT jumlah test SEBELUM mulai fase, bandingkan sesudah.
php artisan test

# Sanity autoload & config
composer dump-autoload            # pastikan tidak ada class map error
php artisan config:clear
php artisan route:clear
php artisan route:list --path=api # jumlah route harus SAMA sebelum & sesudah

# Cek tidak ada sisa referensi namespace lama yang tak ter-alias (harusnya kosong
# untuk class yang SUDAH dihapus alias-nya; sebelum Fase 8 boleh ada, dijembatani alias)
grep -rn "App\\\\Support\\\\" app/ routes/ bootstrap/    # contoh; sesuaikan per fase
```

Endpoint kritis yang harus tetap 2xx/terdaftar (dari `backend-modular-monolith-plan.md`):
`/api/health`, `/api/auth/login`, `/api/companies`, `/api/tenant-context-test`,
`/api/master-data/products`, `/api/journals`, `/api/reports/profit-loss`,
`/api/sales/invoices`, `/api/purchase/bills`, `/api/cash-bank/accounts`,
`/api/inventory/stock-balances`, `/api/access/users`.

Middleware tiap route terproteksi harus tetap: `auth:sanctum`, `company.access`, `permission:*`.

---

## 9. Git checkpoint

- Semua pekerjaan di branch **`claude/backend-modular-refactor-plan-o1fu69`** (repo `laravel_backend`).
- Satu commit per fase minimal; boleh commit per modul di dalam fase (memudahkan rollback parsial).
- Format pesan commit (sesuai CLAUDE.md backend):
  ```
  refactor(shared): Fase 0 — move cross-cutting code to app/Shared
  refactor(sales): Fase 5 — move Sales controllers/requests/services to module
  ```
- **Rollback**: karena tiap fase commit terpisah dan aplikasi hijau di tiap batas fase, `git revert <commit-fase>` mengembalikan satu fase tanpa merusak lainnya.
- Setelah fase selesai & hijau: update ledger di `README.md` (repo `Finlite_knowladge`) lalu commit README.

---

## 10. Dependency graph antar-modul (bukti urutan fase)

Panah = "bergantung pada". Urutan fase mengikuti arah ini (yang didepend duluan dimigrasi lebih awal / paralel-aman karena alias).

```
Shared (Fase 0)  ←  dipakai semua modul
Auth, Companies, Tenant (F1)  ←  Access, Settings, Setup (F2)
MasterData (F3)  ←  Journal, CashBank, Sales, Purchase, Inventory, FixedAssets, Budget, OpeningBalance
Accounting (F3, fiscal/period)  ←  Journal, Reports, semua modul transaksi (period guard)
Journal (F3)  ←  CashBank, Sales, Purchase, Inventory, FixedAssets, OpeningBalance (posting)
Inventory (F5)  ←  Sales, Purchase (integration service; TIDAK sebaliknya → tak ada siklus)
Sales, Purchase, Inventory, CashBank, Journal, FixedAssets  ←  Reports (F6), Dashboard (F6)
```

Karena **alias menjembatani semua referensi**, urutan sebenarnya fleksibel; urutan di atas meminimalkan jumlah referensi "maju" yang perlu diperhatikan saat verifikasi manual. Model (Fase 7) dilepas dari graph ini karena dipindah terpisah paling akhir.
