# Studio Konten · dibuat oleh BagusAdam & Claude · penggunaan mengikuti LISENSI.md
"""Aplikasi web pencari & perangkum isu populer berdasarkan tema.

Jalankan:  streamlit run app.py

Halaman "Pengaturan laporan" hanya muncul jika aplikasi dijalankan di komputer sendiri
lewat "Jalankan Isu Populer.bat" (variabel lingkungan ISU_POPULER_LOKAL=1).
Versi online (Streamlit Cloud) hanya menampilkan halaman pencarian.
"""

from __future__ import annotations

__build__ = "2026.11.24-eac7c33b"
import os

import streamlit as st

st.set_page_config(page_title="Isu Populer", page_icon="📰", layout="wide")

pages = [
    st.Page(
        "app_pages/cari.py",
        title="Cari isu",
        icon=":material/search:",
        default=True,
        help="Ketik tema untuk mencari berita & diskusi terkini, lalu lihat ringkasan isu populernya.",
    )
]

if os.environ.get("ISU_POPULER_LOKAL") == "1":
    pages.append(
        st.Page(
            "app_pages/pengaturan.py",
            title="Pengaturan laporan",
            icon=":material/settings:",
            help="Atur tema, hari & jam kirim, dan penerima laporan email otomatis. Hanya di komputer Anda.",
        )
    )

page = st.navigation(pages, position="top" if len(pages) > 1 else "hidden")
page.run()
