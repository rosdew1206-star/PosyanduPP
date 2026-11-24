<!-- Studio Konten · dibuat oleh BagusAdam & Claude · penggunaan mengikuti LISENSI.md -->
# Panduan: Laporan isu populer otomatis ke email

Setiap hari sekitar **jam 07.00 WIB**, GitHub menjalankan `laporan.py`. Skrip ini mencari isu populer
24 jam terakhir untuk setiap tema di `tema.txt`, lalu mengirim ringkasannya ke Gmail Anda.
Gratis dan tetap berjalan walaupun komputer Anda mati.

---

## Langkah 1 — Buat App Password Gmail (±3 menit)

App Password adalah kata sandi khusus 16 huruf agar aplikasi bisa mengirim email dari Gmail Anda,
tanpa memakai kata sandi utama.

1. Pastikan **Verifikasi 2 Langkah** aktif: https://myaccount.google.com/signinoptions/twosv
2. Buka https://myaccount.google.com/apppasswords
3. Di kolom nama aplikasi, ketik `Isu Populer`, lalu klik **Create**.
4. Salin 16 huruf yang muncul (misalnya `abcd efgh ijkl mnop`). Simpan sementara; kode ini hanya ditampilkan sekali.

> Jangan bagikan App Password ke siapa pun dan jangan menulisnya di file kode.
> Jika bocor, hapus di halaman yang sama lalu buat yang baru.

## Langkah 2 — Simpan data rahasia di GitHub ("Secrets")

1. Buka https://github.com/rosdew1206-star/PosyanduPP/settings/secrets/actions
2. Klik **New repository secret**, lalu buat dua secret berikut (satu per satu):

| Name | Secret (isi) |
|---|---|
| `GMAIL_USER` | alamat Gmail Anda |
| `GMAIL_APP_PASSWORD` | 16 huruf dari Langkah 1 |

Opsional: buat secret `EMAIL_TO` jika laporan ingin dikirim ke alamat lain atau ke beberapa orang
(pisahkan dengan koma). Jika tidak dibuat, laporan dikirim ke `GMAIL_USER`.

Secrets disimpan terenkripsi, tidak terlihat oleh pengunjung repo walaupun repo-nya publik.

## Langkah 3 — Unggah file baru ke GitHub

File baru ada di folder `upload-ke-github`: `laporan.py`, `tema.txt`, `app.py` (diperbarui),
dan file jadwal di `.github/workflows/laporan-harian.yml`.

**a. File biasa:** di halaman repo klik **Add file → Upload files**, tarik `laporan.py`, `tema.txt`,
dan `app.py`, lalu klik **Commit changes**.

**b. File jadwal** (karena foldernya tersembunyi, cara paling mudah adalah membuatnya langsung):
1. Klik **Add file → Create new file**.
2. Di kolom nama file, ketik persis: `.github/workflows/laporan-harian.yml`
   (setiap tanda `/` otomatis membuat folder).
3. Buka file `upload-ke-github\.github\workflows\laporan-harian.yml` dengan Notepad,
   salin seluruh isinya, lalu tempel ke kotak editor GitHub.
4. Klik **Commit changes**.

## Langkah 4 — Uji sekarang (tanpa menunggu besok pagi)

1. Buka tab **Actions** di repo.
2. Klik **Laporan isu populer harian** di sebelah kiri.
3. Klik **Run workflow → Run workflow**.
4. Tunggu ±1 menit. Tanda ✅ hijau berarti email terkirim; periksa Gmail Anda (juga folder Spam).
   Tanda ❌ merah: klik untuk melihat pesan error-nya.

---

## Mengubah pengaturan

- **Tema:** buka `tema.txt` di GitHub, klik ikon pensil, ubah daftar (satu tema per baris), lalu **Commit changes**.
- **Jam kirim:** ubah baris `cron` di `laporan-harian.yml`. Jam ditulis dalam UTC (WIB dikurangi 7 jam).
  Contoh: `"0 23 * * *"` = 06.00 WIB, `"0 0,10 * * *"` = 07.00 dan 17.00 WIB.
- **Menghentikan:** tab **Actions → Laporan isu populer harian → ⋯ → Disable workflow**.

## Catatan

- Jadwal GitHub kadang terlambat 5–30 menit pada jam sibuk.
- Pada repo publik, GitHub otomatis menonaktifkan jadwal jika repo **tidak ada perubahan selama 60 hari**.
  GitHub akan mengirim email peringatan; cukup klik **Enable workflow** di tab Actions,
  atau ubah `tema.txt` sesekali.
- Reddit biasanya memblokir server GitHub, jadi laporan berisi berita dari Google News.
