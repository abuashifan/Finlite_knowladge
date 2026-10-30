# Finlite Workspace — Portal Organisasi, Anggaran, dan Proyek

> **KONSEP PENGEMBANGAN BARU. BELUM ADA KOMITMEN IMPLEMENTASI.**

## Aktor

Pegawai/pengaju, kepala departemen, kepala unit, bagian keuangan, pimpinan, auditor; delegasi dan batas kewenangan harus didefinisikan.

## MVP yang diusulkan

1. Struktur organisasi: unit, departemen, jabatan, keanggotaan pegawai, atasan/approver.
2. Portal: dashboard personal, daftar pengajuan, notifikasi, tugas persetujuan.
3. Pengajuan kegiatan/proyek: proposal, RAB per item, cost center, lampiran, revisi, komentar.
4. Workflow approval berjenjang yang configurable menurut nominal, unit, dan jenis pengajuan.
5. Validasi ketersediaan anggaran dan reservasi sesuai kebijakan.
6. Pencairan/pengadaan: referensi ke transaksi resmi Finlite (bukan jurnal manual paralel).
7. LPJ: bukti pengeluaran, pengembalian dana, pemeriksaan, penutupan.
8. Monitoring: pagu, dana yang dicadangkan, komitmen, realisasi aktual, outstanding uang muka, progres kegiatan, audit trail.

## Contoh alur sekolah

Guru mengajukan kegiatan ujian → kepala kurikulum memeriksa → kepala sekolah menyetujui → keuangan mengecek anggaran → dana muka/pembelian diproses di Accounting → guru unggah kuitansi/LPJ → keuangan verifikasi → laporan realisasi dan sisa anggaran diperbarui.

## Definisi angka (wajib dipisahkan)

- **Allocated:** pagu/anggaran yang ditetapkan.
- **Reserved:** anggaran yang dicadangkan untuk pengajuan yang belum menjadi komitmen final.
- **Committed:** kewajiban/pesanan yang sudah disetujui namun belum sepenuhnya menjadi biaya aktual.
- **Actual:** realisasi yang diakui berdasarkan transaksi sah di Finlite.
- **Disbursed:** uang yang telah keluar; belum tentu sama dengan biaya aktual.
- **Outstanding advance:** uang muka yang belum dipertanggungjawabkan.

Contoh: RAB Rp10 juta, pencairan uang muka Rp7 juta, bukti biaya sah Rp5,5 juta; outstanding advance Rp1,5 juta. Jangan menghitung seluruh pencairan sebagai realisasi biaya.

**Perlu keputusan:** rumus available budget, aturan pembatalan/revisi, carry-over, pembebanan lintas departemen, sumber actual, status posting, dan apakah komitmen mencakup purchase order.

## Status workflow usulan

Draft → Submitted → In Review → Approved/Rejected/Revision Requested → Funding/Execution → LPJ Submitted → LPJ Verified → Closed. Cabang Cancelled/Void harus mengikuti kontrol dan audit.

## Proyek/kegiatan

Setiap proyek dapat memiliki owner, unit, jadwal, milestone, anggaran per kategori, aktivitas, dokumen, dan pengeluaran terkait. Progres pekerjaan tidak boleh otomatis disamakan dengan serapan anggaran.

## Kriteria penerimaan MVP

- Pegawai hanya melihat pengajuan yang diizinkan.
- Approver tidak dapat melompati batas kewenangan.
- Satu aksi persetujuan tidak memicu reservasi ganda (idempotency).
- Perubahan anggaran/pencairan/LPJ terlacak.
- Angka actual direkonsiliasi ke Finlite; perbedaan disajikan sebagai exception.
- Tenant isolation dan kontrol company diuji.
