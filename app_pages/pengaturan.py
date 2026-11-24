# Studio Konten · dibuat oleh BagusAdam & Claude · penggunaan mengikuti LISENSI.md
"""Dashboard pengaturan laporan email otomatis (hanya untuk dijalankan di komputer sendiri)."""

from __future__ import annotations

__build__ = "2026.11.24-eac7c33b"
import os
from datetime import datetime, timedelta, timezone

import streamlit as st

from fetchers import REGIONS, TIME_RANGES
from github_api import GitHub, GitHubError, delete_connection, load_connection, save_connection
from konfigurasi import EMAIL_RE, HARI, VARIABLE_NAME, WORKFLOW_FILE, dari_json, ke_json

WIB = timezone(timedelta(hours=7))
TOKEN_URL = "https://github.com/settings/personal-access-tokens/new"

if os.environ.get("ISU_POPULER_LOKAL") != "1":
    st.error("Halaman ini hanya tersedia saat aplikasi dijalankan di komputer Anda.")
    st.stop()

st.title("Pengaturan laporan email")
st.caption("Atur tema, jadwal, dan penerima laporan isu populer yang dikirim otomatis oleh GitHub.")


def gh_error(e: GitHubError) -> str:
    if e.status == 401:
        return "Token GitHub tidak valid atau sudah kedaluwarsa. Buat token baru lalu hubungkan ulang."
    if e.status in (403, 404):
        return (
            "Token tidak punya izin yang cukup untuk repo ini. Pastikan token mengizinkan repo "
            "tersebut dengan izin **Actions: Read and write** dan **Variables: Read and write**. "
            f"(GitHub: {e.message})"
        )
    return f"GitHub mengembalikan error {e.status}: {e.message}"


# ---------------------------------------------------------------- koneksi
conn = load_connection()

if not conn:
    st.info(
        "Hubungkan dashboard ini ke repo GitHub Anda satu kali saja. "
        "Token disimpan hanya di komputer ini, tidak pernah diunggah ke GitHub.",
        icon=":material/link:",
    )
    with st.form("hubungkan"):
        repo = st.text_input("Repo GitHub", value="rosdew1206-star/PosyanduPP", help="Format: nama-akun/nama-repo")
        token = st.text_input(
            "Token GitHub",
            type="password",
            help=f"Buat di {TOKEN_URL} (lihat PANDUAN-DASHBOARD.md).",
        )
        st.markdown(f"Belum punya token? [Buat token di GitHub]({TOKEN_URL}) — ikuti PANDUAN-DASHBOARD.md.")
        if st.form_submit_button("Hubungkan", icon=":material/link:", type="primary"):
            if not repo.strip() or not token.strip():
                st.error("Isi repo dan token terlebih dahulu.")
            else:
                gh = GitHub(repo, token)
                try:
                    gh.check_repo()
                    gh.get_variable(VARIABLE_NAME)  # uji izin Variables
                    save_connection(gh.repo, gh.token)
                    st.success("Terhubung!")
                    st.rerun()
                except GitHubError as e:
                    st.error(gh_error(e))
                except OSError as e:
                    st.error(f"Tidak bisa menghubungi GitHub: {e}")
    st.stop()

gh = GitHub(conn["repo"], conn["token"])

# Muat pengaturan sekali per sesi (tombol "Muat ulang" untuk mengambil lagi)
if "cfg" not in st.session_state:
    try:
        raw = gh.get_variable(VARIABLE_NAME)
        st.session_state.cfg = dari_json(raw)
        st.session_state.cfg_baru = raw is None
    except GitHubError as e:
        st.error(gh_error(e))
        if st.button("Putuskan koneksi & masukkan token baru", icon=":material/link_off:"):
            delete_connection()
            st.rerun()
        st.stop()
    except OSError as e:
        st.error(f"Tidak bisa menghubungi GitHub: {e}")
        st.stop()

cfg = st.session_state.cfg

with st.container(horizontal=True, vertical_alignment="center"):
    st.markdown(f":material/check_circle: Terhubung ke **{gh.repo}**")
    if st.button("Muat ulang", icon=":material/refresh:"):
        del st.session_state["cfg"]
        st.rerun()

if st.session_state.get("cfg_baru"):
    st.warning(
        "Pengaturan belum pernah disimpan. Nilai di bawah adalah bawaan; klik **Simpan pengaturan** "
        "agar dipakai oleh laporan otomatis.",
    )

# ---------------------------------------------------------------- form
with st.form("pengaturan"):
    aktif = st.toggle("Kirim laporan otomatis", value=cfg["aktif"])

    st.subheader("Tema", divider="gray")
    tema_text = st.text_area(
        "Tema yang dipantau (satu per baris)",
        value="\n".join(cfg["tema"]),
        height=140,
        help='Contoh: harga beras, "mobil listrik", timnas Indonesia. Maksimal 20 tema.',
    )

    st.subheader("Jadwal kirim", divider="gray")
    hari = st.pills(
        "Hari",
        options=list(range(7)),
        format_func=lambda i: HARI[i],
        selection_mode="multi",
        default=cfg["hari"],
    )
    jam = st.multiselect(
        "Jam (WIB)",
        options=list(range(24)),
        default=cfg["jam"],
        format_func=lambda j: f"{j:02d}:00",
        help="Boleh lebih dari satu. Email biasanya tiba 5–20 menit setelah jam yang dipilih.",
    )

    st.subheader("Penerima", divider="gray")
    email_text = st.text_area(
        "Alamat email tujuan (satu per baris)",
        value="\n".join(cfg["email_tujuan"]),
        height=100,
        help="Kosongkan untuk mengirim ke akun Gmail pengirim (secret GMAIL_USER).",
    )

    st.subheader("Isi laporan", divider="gray")
    c1, c2, c3 = st.columns(3)
    wilayah = c1.selectbox("Wilayah & bahasa", list(REGIONS), index=list(REGIONS).index(cfg["wilayah"]))
    rentang = c2.selectbox("Rentang berita", list(TIME_RANGES), index=list(TIME_RANGES).index(cfg["rentang"]))
    jumlah = c3.slider("Isu per tema", 1, 10, cfg["jumlah_isu"])

    simpan = st.form_submit_button("Simpan pengaturan", icon=":material/save:", type="primary")

if simpan:
    tema = [t.strip() for t in tema_text.splitlines() if t.strip()]
    emails = [e.strip() for e in email_text.replace(",", "\n").splitlines() if e.strip()]
    salah = [e for e in emails if not EMAIL_RE.match(e)]
    errors = []
    if not tema:
        errors.append("Isi minimal satu tema.")
    if len(tema) > 20:
        errors.append("Maksimal 20 tema.")
    if aktif and not hari:
        errors.append("Pilih minimal satu hari kirim.")
    if aktif and not jam:
        errors.append("Pilih minimal satu jam kirim.")
    if salah:
        errors.append("Alamat email tidak valid: " + ", ".join(salah))
    if errors:
        for err in errors:
            st.error(err)
    else:
        baru = {
            "aktif": aktif,
            "tema": tema,
            "hari": sorted(hari),
            "jam": sorted(jam),
            "email_tujuan": emails,
            "wilayah": wilayah,
            "rentang": rentang,
            "jumlah_isu": jumlah,
        }
        try:
            gh.set_variable(VARIABLE_NAME, ke_json(baru))
            st.session_state.cfg = dari_json(ke_json(baru))
            st.session_state.cfg_baru = False
            st.toast("Pengaturan tersimpan di GitHub.", icon=":material/check:")
            st.rerun()
        except GitHubError as e:
            st.error(gh_error(e))
        except OSError as e:
            st.error(f"Tidak bisa menghubungi GitHub: {e}")

# ---------------------------------------------------------------- ringkasan jadwal
if cfg["aktif"] and cfg["hari"] and cfg["jam"]:
    hari_txt = "setiap hari" if len(cfg["hari"]) == 7 else ", ".join(HARI[h] for h in cfg["hari"])
    jam_txt = ", ".join(f"{j:02d}:00" for j in cfg["jam"])
    penerima = f"{len(cfg['email_tujuan'])} alamat" if cfg["email_tujuan"] else "akun Gmail pengirim"
    st.success(
        f"Laporan **{len(cfg['tema'])} tema** dikirim **{hari_txt}** pukul **{jam_txt} WIB** ke {penerima}.",
        icon=":material/schedule:",
    )
else:
    st.warning("Laporan otomatis sedang nonaktif.", icon=":material/pause_circle:")

# ---------------------------------------------------------------- kirim sekarang & riwayat
st.subheader("Kirim & riwayat", divider="gray")
with st.container(horizontal=True, vertical_alignment="center"):
    if st.button("Kirim laporan sekarang", icon=":material/send:"):
        try:
            gh.dispatch(WORKFLOW_FILE)
            st.toast("Permintaan dikirim. Email tiba dalam ±1–2 menit.", icon=":material/send:")
        except GitHubError as e:
            st.error(gh_error(e))
    st.link_button("Buka di GitHub Actions", f"https://github.com/{gh.repo}/actions", icon=":material/open_in_new:")
    st.button("Segarkan riwayat", icon=":material/refresh:")

STATUS = {
    "success": "✅ Berhasil",
    "failure": "❌ Gagal",
    "cancelled": "⏹️ Dibatalkan",
    "skipped": "⏭️ Dilewati",
}
try:
    runs = gh.recent_runs(WORKFLOW_FILE, n=10)
    rows = []
    for r in runs:
        t = datetime.fromisoformat(r["created_at"].replace("Z", "+00:00")).astimezone(WIB)
        status = STATUS.get(r.get("conclusion") or "", "⏳ Berjalan" if r["status"] != "completed" else r["status"])
        rows.append(
            {
                "Waktu (WIB)": t.strftime("%a %d %b %H:%M"),
                "Pemicu": "Manual" if r["event"] == "workflow_dispatch" else "Terjadwal (cek tiap jam)",
                "Status": status,
                "Detail": r["html_url"],
            }
        )
    if rows:
        st.dataframe(
            rows,
            hide_index=True,
            column_config={"Detail": st.column_config.LinkColumn("Detail", display_text="Lihat")},
            alt="Riwayat menjalankan laporan otomatis",
        )
        st.caption(
            "Jalan terjadwal terjadi setiap jam; di luar jam kirim, laporan otomatis tidak mengirim email "
            "(tetap berstatus berhasil)."
        )
    else:
        st.caption("Belum ada riwayat.")
except GitHubError as e:
    st.caption(f"Riwayat tidak bisa dimuat: {gh_error(e)}")
except OSError:
    st.caption("Riwayat tidak bisa dimuat (tidak ada koneksi internet).")

with st.expander("Koneksi GitHub"):
    st.write(f"Repo: `{gh.repo}`. Token tersimpan di komputer ini (folder AppData\\IsuPopuler).")
    if st.button("Putuskan koneksi", icon=":material/link_off:"):
        delete_connection()
        st.session_state.pop("cfg", None)
        st.rerun()
