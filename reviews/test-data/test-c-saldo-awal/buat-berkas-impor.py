"""Membuat berkas impor Test C (saldo awal + aset tetap awal), template Perdagangan Umum.

Pakai:  python3 buat-berkas-impor.py <folder-keluaran> [tanggal-saldo-awal YYYY-MM-DD]
Contoh: python3 buat-berkas-impor.py . 2026-01-01

Butuh openpyxl. Akumulasi penyusutan dihitung garis lurus sampai tanggal saldo
awal dengan rumus yang sama dengan peringatan di pratinjau impor Finlite
(laravel_backend: OpeningAccumulatedDepreciation), jadi tidak muncul peringatan
"menyimpang dari perkiraan". Jumlah per akun di berkas saldo awal sama dengan
total kartu di berkas aset tetap.
"""
import sys, datetime as dt
from openpyxl import Workbook
out = sys.argv[1]
OPEN = dt.date.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 else dt.date(2025, 12, 31)

def months_elapsed(start):
    y, m = start.year, start.month + 1
    if m > 12: y, m = y + 1, 1
    first = dt.date(y, m, 1); om = dt.date(OPEN.year, OPEN.month, 1)
    if om <= first: return 0
    return (om.year - first.year) * 12 + om.month - first.month

def accum(cost, life, start):
    if not life: return 0
    return float(round(min(cost / (life * 12) * months_elapsed(start), cost)))

# name, category, acq date, cost, life, qty, desc, GL account (cost), GL account (accum)
A = [
 ("Tanah Gudang Jl. Industri No. 12", "LAND", dt.date(2019,5,10), 400_000_000, None, "Tanah dan hak atas tanah", "1500", None),
 ("Gedung Gudang dan Kantor", "BUILDING", dt.date(2020,8,20), 600_000_000, 20, "Bangunan permanen 2 lantai", "1520", "1521"),
 ("Mitsubishi L300 Pickup B 9123 KJ", "VEHICLE", dt.date(2022,2,12), 220_000_000, 8, "Kendaraan angkut barang", "1510", "1511"),
 ("Honda Vario Motor Operasional B 3456 TX", "VEHICLE", dt.date(2023,9,5), 25_000_000, 8, "Motor antar barang", "1510", "1511"),
 ("Mesin Kasir dan Printer Struk", "OFFICE_EQUIP", dt.date(2024,1,3), 15_000_000, 4, "Kasir toko", "1530", "1531"),
 ("Laptop Lenovo ThinkPad", "IT_EQUIP", dt.date(2024,6,15), 14_000_000, 4, "Laptop pemilik", "1530", "1531"),
 ("Komputer Admin Gudang", "IT_EQUIP", dt.date(2023,3,2), 9_000_000, 4, "PC admin", "1530", "1531"),
 ("Rak Besi Gudang (set 20 unit)", "FURNITURE", dt.date(2022,10,10), 36_000_000, 4, "Rak penyimpanan barang", "1530", "1531"),
 ("Hand Pallet dan Troli Angkut", "MACHINE", dt.date(2023,7,18), 12_000_000, 8, "Alat angkut gudang", "1530", "1531"),
 ("Lisensi Software Kasir dan Stok", "SOFTWARE", dt.date(2024,4,1), 24_000_000, 4, "Lisensi 4 tahun", "1540", "1541"),
]
fmt = lambda d: d.strftime("%d/%m/%Y")
fa_rows, cost_by, acc_by = [], {}, {}
for n, cat, d, cost, life, desc, ca, aa in A:
    ac = accum(cost, life, d)
    fa_rows.append([n, cat, fmt(d), cost, ac, 0, life or "", 1, fmt(d), "", "", desc])
    cost_by[ca] = cost_by.get(ca, 0) + cost
    if aa: acc_by[aa] = acc_by.get(aa, 0) + ac

debit = [
 ("1100","Saldo awal kas toko",15_000_000),
 ("1110","Saldo awal rekening bank",185_000_000),
 ("1120","Saldo awal piutang usaha",62_500_000),
 ("1131","Saldo awal persediaan barang dagang A",96_000_000),
 ("1132","Saldo awal persediaan barang dagang B",54_000_000),
 ("1140","Saldo awal uang muka pembelian",10_000_000),
]
names = {"1500":"Tanah","1510":"Kendaraan","1520":"Gedung","1530":"Peralatan","1540":"Perangkat lunak"}
accn = {"1511":"Akumulasi penyusutan kendaraan","1521":"Akumulasi penyusutan gedung","1531":"Akumulasi penyusutan peralatan","1541":"Akumulasi amortisasi perangkat lunak"}
for k in sorted(cost_by): debit.append((k, f"Saldo awal harga perolehan {names[k].lower()}", cost_by[k]))
credit = [(k, f"Saldo awal {accn[k].lower()}", round(v,2)) for k,v in sorted(acc_by.items())]
credit += [("2100","Saldo awal hutang usaha",78_000_000),("2130","Saldo awal uang muka penjualan",5_000_000),("3100","Saldo awal modal pemilik",500_000_000)]
td = sum(x[2] for x in debit); tc = sum(x[2] for x in credit)
credit.append(("3200","Saldo awal laba ditahan", round(td - tc)))
assert abs(sum(x[2] for x in credit) - td) < 0.01 and credit[-1][2] > 0

ob_rows = [[c, d, v, 0] for c, d, v in debit] + [[c, d, 0, v] for c, d, v in credit]
ob_rows.sort(key=lambda r: r[0])

def save(path, headers, rows, widths):
    wb = Workbook(); ws = wb.active
    ws.append(headers)
    for r in rows: ws.append(r)
    for i, w in enumerate(widths): ws.column_dimensions[chr(65+i)].width = w
    wb.save(path)
save(f"{out}/saldo-awal-perdagangan-umum.xlsx", ["Account Code","Description","Debit","Credit"], ob_rows, [14,48,18,18])
save(f"{out}/aset-tetap-awal-perdagangan-umum.xlsx",
     ["Name","Category","Acquisition Date","Acquisition Cost","Accumulated Depreciation","Salvage Value","Useful Life Years","Quantity","Service Start Date","Department","Project","Description"],
     fa_rows, [40,14,16,18,22,14,16,10,18,12,10,32])
print("Total debit/kredit:", td)
print("Laba ditahan:", credit[-1][2])
for k in sorted(cost_by): print("GL", k, cost_by[k])
for k in sorted(acc_by): print("GL", k, acc_by[k])
