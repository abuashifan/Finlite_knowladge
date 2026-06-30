# Rencana Modularisasi Laravel Backend Finlite

## Context

**Masalah**: Aplikasi Laravel 13.x saat ini memiliki 18 module di `app/Modules/{Nama}/` yang hanya berisi `Routes/api.php` dan folder `Providers/` kosong. Kode sesungguhnya (controllers, services, models, requests) masih tersebar di struktur Laravel tradisional (`app/Http/`, `app/Services/`, `app/Models/`), sehingga:

- Navigasi kode sulit — untuk 1 fitur harus buka 4-5 folder berbeda
- Tidak jelas batasan antar modul — dependensi silang tersembunyi
- Module providers kosong — tidak bisa isolated testing per modul
- `app/Shared/` cuma berisi README stub — cross-cutting code tidak terpusat

**Tujuan**: Setiap modul menjadi self-contained (Controllers, Services, Models, Requests, Routes, Providers, Config, Migrations, Tests dalam satu folder), dengan kode cross-cutting di `app/Core/`.

**Pendekatan**: Full DDD Modules, 18 modul dipertahankan, migrasi bertahap per modul (non-blocking).

---

## Target Architecture

```
app/
  Core/                              ← Shared cross-cutting code
    Traits/                          ← 5 traits (dari app/Traits/)
    Support/                         ← 31 value objects (dari app/Support/)
      AccountMapping/ Api/ Audit/ DataRetention/ DocumentNumbering/
      Inventory/ OpeningBalance/ Reports/ Revision/ SourceLink/ Transaction/
    Contracts/Transactions/          ← 2 interfaces
    Enums/                           ← SourceType
    Exceptions/                      ← ApiException
    Data/Reports/                    ← 16 report DTOs
    Middleware/                      ← EnsureCompanyAccess, EnsurePermission
    Services/
      Tenant/                        ← TenantContext, ConnectionManager, Provisioning, Migration
      Transactions/                  ← Policy, Dependency, DateGuard, Revision, VoidEffect + checkers
      AccountMapping/                ← Service + Validator
      DocumentNumbering/             ← DocumentNumberService
      Validation/                    ← BusinessReferenceValidator
    Models/                          ← 18 central models (User, Company, Role, Permission, Plan, dll)
    Http/Controllers/
      SourceDocumentPickerController.php
      HealthController.php
    Providers/CoreServiceProvider.php
    Config/                          ← config files yg cross-module

  Modules/
    Auth/                            ← Controllers, Requests, Services, Models, Routes, Providers
    Companies/                       ← sda
    Tenant/                          ← sda
    Access/                          ← sda
    Settings/                        ← sda
    Setup/                           ← sda
    MasterData/                      ← sda + Models tenant + Migrations tenant
    Accounting/                      ← sda
    Journal/                         ← sda
    CashBank/                        ← sda
    OpeningBalance/                  ← sda
    Budget/                          ← sda
    Inventory/                       ← sda + Config
    Sales/                           ← sda + Config
    Purchase/                        ← sda + Config
    FixedAssets/                     ← sda
    Reports/                         ← sda
    Dashboard/                       ← sda

  Http/
    Controllers/Controller.php       ← base controller (tetap)
  Console/Commands/                  ← 9 artisan commands
  Providers/
    AppServiceProvider.php           ← stripped down
    AliasServiceProvider.php         ← backward compatibility (sementara)

tests/                               ← tetap di sini, ikuti struktur module
  Feature/{Module}/
  Unit/{Module}/
```

Setiap module berisi:
```
app/Modules/{Nama}/
  Controllers/         ← dari app/Http/Controllers/Api/{Nama}/
  Requests/            ← dari app/Http/Requests/{Nama}/
  Services/            ← dari app/Services/{Nama}/
  Models/              ← tenant models dari app/Models/Tenant/ + central models jika relevan
  Routes/api.php       ← sudah ada, update namespace controller references
  Providers/{Nama}ServiceProvider.php  ← register bindings, load routes, load migrations
  Config/              ← module-specific config (opsional)
  Migrations/          ← tenant migrations (opsional, fase akhir)
  Tests/               ← (opsional, bisa tetap di tests/)
```

---

## Strategi Backward Compatibility

Setiap fase, class yang dipindahkan tetap bisa diakses via nama lama menggunakan `class_alias()` di `AliasServiceProvider`:

```php
class_alias(\App\Core\Support\Api\ApiResponseBuilder::class, \App\Support\Api\ApiResponseBuilder::class);
class_alias(\App\Core\Traits\ApiResponse::class, \App\Traits\ApiResponse::class);
// ... bertambah tiap fase, dihapus di fase cleanup
```

Ini memungkinkan migrasi inkremental tanpa merusak kode yang belum dimigrasi.

---

## Fase Migrasi

### Fase 0: Core Foundation (2-3 hari)
**Goal**: Pindahkan semua kode shared ke `app/Core/`, buat alias bridge, verifikasi 120+ test tetap pass.

**Yang dipindah**:
- `app/Support/` → `app/Core/Support/` (31 file)
- `app/Traits/` → `app/Core/Traits/` (5 file)
- `app/Contracts/` → `app/Core/Contracts/` (2 file)
- `app/Enums/` → `app/Core/Enums/` (1 file)
- `app/Exceptions/` → `app/Core/Exceptions/` (1 file)
- `app/Data/Reports/` → `app/Core/Data/Reports/` (16 file)
- `app/Http/Middleware/` → `app/Core/Middleware/` (2 file)
- `app/Http/Requests/Concerns/` → `app/Core/Support/Reports/` (2 file)
- `app/Services/Tenant/` → `app/Core/Services/Tenant/` (4 file)
- `app/Services/Transactions/` → `app/Core/Services/Transactions/` (15 file)
- `app/Services/AccountMapping/` → `app/Core/Services/AccountMapping/` (2 file)
- `app/Services/DocumentNumbering/` → `app/Core/Services/DocumentNumbering/` (1 file)
- `app/Services/Validation/` → `app/Core/Services/Validation/` (1 file)
- `app/Models/` (central) → `app/Core/Models/` (18 file)
- `app/Http/Controllers/Api/HealthController.php` → `app/Core/Http/Controllers/`
- `app/Http/Controllers/Api/Transactions/SourceDocumentPickerController.php` → `app/Core/Http/Controllers/`

**Yang dibuat**:
- `app/Core/Providers/CoreServiceProvider.php` — register TenantContext singleton, bind contracts, load central migrations
- `app/Providers/AliasServiceProvider.php` — backward compatibility aliases
- Update `bootstrap/providers.php` — tambahkan CoreServiceProvider + AliasServiceProvider
- Update `app/Providers/AppServiceProvider.php` — hapus binding yang sudah pindah ke Core

**Verifikasi**: `php artisan test` — 120+ tests pass. `php artisan serve` — API endpoints respond.

---

### Fase 1: Auth + Companies + Tenant (2-3 hari)
**Goal**: Migrasi 3 modul self-contained pertama, establish pola yang akan diulangi.

**Auth module** (`app/Modules/Auth/`):
- Controllers: AuthController, PermissionController
- Requests: LoginRequest, RegisterRequest
- Services: PermissionService, PermissionCatalogService, EffectivePermissionService (dari `app/Services/Permissions/`)
- Models: (User tetap di Core, di-refer via DI)
- Buat `AuthServiceProvider.php`

**Companies module** (`app/Modules/Companies/`):
- Controllers: CompanyController, MyCompaniesController
- Services: CompanyUserAssignmentService
- Models: Company, CompanyUser, CompanyInvitation, CompanyAccountingSetting, CompanyModuleSetting, CompanySetupState
- Buat `CompaniesServiceProvider.php`

**Tenant module** (`app/Modules/Tenant/`):
- Controllers: TenantContextTestController
- Models: TenantDatabase
- Buat `TenantServiceProvider.php`

**Pola yang diulang tiap fase**:
1. Buat struktur folder module
2. Pindahkan file + update namespace
3. Buat ServiceProvider (register routes, bindings)
4. Register provider di `bootstrap/providers.php`
5. Tambahkan alias di `AliasServiceProvider`
6. Update cross-module `use` statements
7. Run tests

---

### Fase 2: Access + Settings + Setup (2-3 hari)
Module yang depend ke Companies dan Auth.

### Fase 3: MasterData + Accounting + Journal (3-4 hari)
Module foundational yang menyediakan data ke downstream modules. Pindahkan tenant models (ChartOfAccount, Contact, Product, dll) dan tenant migrations.

### Fase 4: CashBank + OpeningBalance + Budget (2-3 hari)
Module dengan dependensi moderat.

### Fase 5: Inventory + Sales + Purchase (4-5 hari)
**Fase paling kompleks** — ketiga modul ini saling terintegrasi:
- Inventory menyediakan `InventorySalesIntegrationService` dan `InventoryPurchaseIntegrationService`
- Sales consume InventorySalesIntegrationService
- Purchase consume InventoryPurchaseIntegrationService
- Tidak ada circular dependency (Inventory tidak depend ke Sales/Purchase)

### Fase 6: FixedAssets + Reports + Dashboard (2-3 hari)
Module tersisa.

### Fase 7: Cleanup (2-3 hari)
- Hapus `AliasServiceProvider`
- Hapus directory kosong (`app/Http/Controllers/Api/`, `app/Http/Requests/`, `app/Services/`, `app/Support/`, `app/Traits/`, dll)
- Update `phpunit.xml` jika struktur test berubah
- `composer dump-autoload -o`
- Full test suite

---

## Estimasi Total: 19-27 hari kerja

| Fase | File dipindah | Estimasi |
|------|-------------|----------|
| 0: Core | ~90 | 2-3 hari |
| 1: Auth/Companies/Tenant | ~25 | 2-3 hari |
| 2: Access/Settings/Setup | ~25 | 2-3 hari |
| 3: MasterData/Accounting/Journal | ~60 | 3-4 hari |
| 4: CashBank/OpeningBalance/Budget | ~45 | 2-3 hari |
| 5: Inventory/Sales/Purchase | ~110 | 4-5 hari |
| 6: FixedAssets/Reports/Dashboard | ~45 | 2-3 hari |
| 7: Cleanup | ~30 file dihapus | 2-3 hari |

---

## Risiko & Mitigasi

| Risiko | Dampak | Mitigasi |
|--------|--------|----------|
| Missed import references | Test gagal | Run full test suite tiap fase; grep-based scan namespace lama |
| Cross-module integration break | Fitur rusak | Fase 5 (Inventory/Sales/Purchase) paling kritis — test integration ketat |
| Tenant migration break | Multi-tenant rusak | Jaga `database/migrations/tenant/` sebagai source of truth; jangan pindah sebelum Fase 7 |
| `class_alias()` performance | Autoloading lambat | Temporary only; dihapus di Fase 7 |

---

## Verifikasi

Setiap fase berakhir dengan:
1. `php artisan test` — semua 120+ tests pass
2. `php artisan serve` — API endpoints respond dengan benar
3. Test manual: register → login → select company → akses modul (sales, purchase, inventory, reports)
4. `X-Company-ID` header + tenant database switching tetap berfungsi

Fase 5 (Inventory/Sales/Purchase) ada verifikasi tambahan:
- Buat Sales Quotation → Sales Order → Delivery Order → Proforma Invoice → Sales Invoice
- Verifikasi stock movement terbuat otomatis (Inventory-Sales integration)
- Buat Purchase Request → Purchase Order → Goods Receipt → Vendor Bill
- Verifikasi stock terupdate (Inventory-Purchase integration)
