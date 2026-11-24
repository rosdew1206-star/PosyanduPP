<!-- Studio Konten · dibuat oleh BagusAdam & Claude · penggunaan mengikuti LISENSI.md -->
# Panduan: Dashboard pengaturan laporan email

Dashboard ini ada di halaman **Pengaturan laporan** saat aplikasi dibuka lewat ikon **Isu Populer** di Desktop.
Di sana Anda bisa mengatur **tema**, **hari & jam kirim**, **alamat email tujuan**, dan menekan **Kirim laporan sekarang**.
Versi online (streamlit.app) tidak menampilkan halaman ini, jadi orang lain tidak bisa mengubah pengaturan Anda.

Pemasangan dilakukan sekali saja, kira-kira 10 menit.

---

## Langkah 1 — Perbarui file di GitHub

### a. Unggah file
1. Buka https://github.com/rosdew1206-star/PosyanduPP → **Add file → Upload files**.
2. Dari folder `upload-ke-github`, tarik **file dan folder** berikut sekaligus:
   - `app.py`, `laporan.py`, `konfigurasi.py`, `github_api.py`
   - folder **`app_pages`** (tarik foldernya; GitHub ikut membuat foldernya)
3. Klik **Commit changes**.

### b. Ganti isi file jadwal
1. Buka https://github.com/rosdew1206-star/PosyanduPP/edit/main/.github/workflows/laporan-harian.yml
2. Klik di kotak editor, tekan **Ctrl+A** lalu **Delete** untuk mengosongkannya.
3. Buka `upload-ke-github\.github\workflows\laporan-harian.yml` dengan Notepad, **Ctrl+A**, **Ctrl+C**,
   lalu tempel (**Ctrl+V**) ke editor GitHub.
4. Klik **Commit changes...** → **Commit changes**.

Sekarang GitHub memeriksa setiap jam, dan mengirim email hanya pada hari & jam yang Anda pilih di dashboard.

## Langkah 2 — Buat token GitHub untuk dashboard

Token ini adalah "kunci" agar dashboard di komputer Anda boleh menyimpan pengaturan ke repo.

1. Buka https://github.com/settings/personal-access-tokens/new
2. Isi:
   - **Token name:** `Dashboard Isu Populer`
   - **Expiration:** pilih masa berlaku (misalnya 1 tahun). Setelah kedaluwarsa, buat token baru.
   - **Repository access:** pilih **Only select repositories**, lalu pilih **isu-populer**.
3. Di bagian **Permissions → Repository permissions**, klik **Add permissions** dan atur:
   - **Actions:** `Read and write`
   - **Variables:** `Read and write`
   (Metadata: Read-only akan ikut otomatis.)
4. Klik **Generate token**, lalu salin token yang muncul (diawali `github_pat_...`). Token hanya ditampilkan sekali.

> Jangan bagikan token ini ke siapa pun dan jangan menaruhnya di file yang diunggah.

## Langkah 3 — Hubungkan dashboard

1. Klik dua kali ikon **Isu Populer** di Desktop.
2. Di menu atas, klik **Pengaturan laporan**.
3. Repo sudah terisi `rosdew1206-star/PosyanduPP`. Tempel token di kolom **Token GitHub**, lalu klik **Hubungkan**.
   Token disimpan di komputer ini saja (`%APPDATA%\IsuPopuler\github.json`).
4. Atur tema, hari, jam, dan email tujuan, lalu klik **Simpan pengaturan**.
5. Klik **Kirim laporan sekarang** untuk mencoba; email tiba dalam ±1–2 menit.

---

## Pertanyaan umum

- **Apakah alamat email tujuan terlihat orang lain?** Tidak. Pengaturan disimpan sebagai *Actions variable*
  yang hanya bisa dilihat pemilik repo, dan log GitHub hanya menulis jumlah penerima.
  Penerima dikirimi sebagai BCC, jadi tidak saling melihat alamat.
- **Kenapa riwayat penuh dengan jalan "Terjadwal"?** GitHub memeriksa setiap jam. Di luar jam kirim,
  laporan otomatis langsung berhenti tanpa mengirim email (statusnya tetap ✅).
- **Email terlambat?** Jadwal GitHub bisa terlambat 5–20 menit. Jika terlambat lebih dari satu jam
  (jarang), pengiriman jam itu terlewat.
- **Menghentikan sementara:** matikan tombol **Kirim laporan otomatis** di dashboard, lalu Simpan.
- **tema.txt masih dipakai?** Hanya sebagai cadangan jika pengaturan di dashboard belum pernah disimpan.
- **Token kedaluwarsa:** dashboard akan memberi tahu. Klik **Putuskan koneksi**, buat token baru (Langkah 2),
  lalu hubungkan lagi.
