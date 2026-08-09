# Fase 0 — Perbaiki kontrak service `budgetApi`

**Tujuan:** membuat data yang dikembalikan API benar-benar sampai ke layar.
**Wajib lebih dulu** — selama fase ini belum selesai, tidak ada perbaikan lain
yang bisa dilihat hasilnya.

## Masalah

`src/modules/budget/services/budgetApi.ts` menutup **16 dari 16 method** dengan
`.then((r) => r.data)`. Interceptor `src/services/http.ts:160` sudah
mengembalikan `response.data`, jadi itu unwrap kedua:

```
API            {success: true, data: [...], meta: []}
http.get()  →  {success: true, data: [...], meta: []}   ← sudah di-unwrap di sini
.then(r=>r.data) → [...]                                 ← unwrap kedua
halaman: data?.data → undefined                          ← array tidak punya .data
```

Budget adalah satu-satunya modul yang melakukan ini — 20+ service lain memanggil
`http.get<unknown, ApiResponse<T>>(...)` dan memakai hasilnya langsung.

## Perubahan

**`src/modules/budget/services/budgetApi.ts`** — tulis ulang mengikuti
`src/modules/master-data/services/produkApi.ts` sebagai acuan:

```ts
// SEBELUM
listPeriods: (): Promise<ApiResponse<BudgetPeriod[]>> =>
  http.get('/budget-periods').then((r) => r.data),

// SESUDAH
listPeriods: () =>
  http.get<unknown, ApiResponse<BudgetPeriod[]>>('/budget-periods'),
```

Berlaku untuk keempat belas method lainnya juga. Aturannya seragam:

- Buang **setiap** `.then((r) => r.data)`.
- Pindahkan tipe hasil ke generic kedua `http.get`/`post`/`put`, jangan sebagai
  anotasi return — inilah yang membuat type checker benar-benar memeriksa.
- Buang anotasi `: Promise<ApiResponse<...>>` yang eksplisit; biarkan
  disimpulkan dari generic.

**Jangan** ubah halaman yang membacanya. `data?.data` di kelima halaman sudah
benar begitu service-nya benar.

## Kenapa `npm run build` tidak menangkap ini

`http.get('/budget-periods')` tanpa generic → axios memberi `AxiosResponse<any>`
→ `r.data` bertipe `any` → `Promise<any>` bisa ditugaskan ke
`Promise<ApiResponse<...>>` tanpa keluhan. Memindahkan tipe ke generic
menghilangkan `any`-nya, jadi kesalahan serupa berikutnya akan gagal build.

## Verifikasi

```bash
# tidak boleh ada sisa
rtk grep -rn "then((r) => r.data)" src/modules/
rtk npm run build          # WAJIB — npx tsc --noEmit tidak memeriksa apa pun di project ini
```

Manual (butuh Fase 1 untuk menu, atau deep link `/budget` pada muat pertama):

1. Buat satu periode anggaran lewat halaman form.
2. **Daftar periode menampilkan baris itu.** Inilah uji yang menentukan —
   sebelum fase ini, daftarnya tetap berbunyi "Belum ada periode anggaran".
3. Hapus lagi baris ujinya.

Kalau ingin menguji tanpa UI, `curl` endpoint-nya dan bandingkan: yang dikirim
API dan yang dibaca halaman harus objek dengan kunci `data`, bukan array
telanjang.
