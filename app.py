# app.py
import streamlit as st
import pandas as pd
import os
from datetime import datetime
from pathlib import Path

# =====================================================
# KONFIGURASI AWAL
# =====================================================
BASE_DIR = Path(".")
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_KEU = UPLOADS_DIR / "keuangan"
UPLOADS_BAR = UPLOADS_DIR / "barang"

for d in [DATA_DIR, UPLOADS_DIR, UPLOADS_KEU, UPLOADS_BAR]:
    os.makedirs(d, exist_ok=True)

FILE_KEUANGAN = DATA_DIR / "keuangan.csv"
FILE_BARANG = DATA_DIR / "barang.csv"
FILE_LOG = DATA_DIR / "log_aktivitas.csv"

if not FILE_KEUANGAN.exists():
    pd.DataFrame(columns=["Tanggal","Keterangan","Kategori","Masuk","Keluar","Saldo","bukti_url"]).to_csv(FILE_KEUANGAN, index=False)

if not FILE_BARANG.exists():
    pd.DataFrame(columns=["tanggal","jenis","keterangan","jumlah","satuan","bukti"]).to_csv(FILE_BARANG, index=False)

if not FILE_LOG.exists():
    pd.DataFrame(columns=["Waktu","User","Aktivitas"]).to_csv(FILE_LOG, index=False)

# =====================================================
# AKUN PANITIA
# =====================================================
PANITIA = {
    "ketua": "kelas3ku",
    "sekretaris": "fatik3762",
    "bendahara 1": "hadi5028",
    "bendahara 2": "riki6522",
    "koor donasi 1": "bayu0255",
    "koor donasi 2": "roni9044"
}

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(page_title="Manajemen Musholla At-Taqwa", layout="wide")

# =====================================================
# STYLE HIJAU NU (DIPERTAHANKAN)
# =====================================================
st.markdown("""
<style>
.stApp { background-color: #f1f6f2 !important; }
h1,h2,h3,h4 { color:#0b6e4f !important; font-weight:800; }
.header-box {
    background: linear-gradient(90deg,#0b6e4f,#18a36d);
    padding:22px 26px; border-radius:14px;
    color:white !important; margin-bottom:16px;
}
.header-title { font-size:30px; font-weight:900; }
.header-sub { opacity:.85; margin-top:-6px; }
section[data-testid="stSidebar"] { background:#0b6e4f; padding:20px; }
section[data-testid="stSidebar"] * { color:white !important; }
.stButton>button {
    background: linear-gradient(90deg,#0b6e4f,#18a36d);
    color:white !important; font-weight:700;
    padding:8px 22px; border-radius:10px;
}
.stButton>button:hover { background: linear-gradient(90deg,#18a36d,#0b6e4f); }
input, textarea, select { border-radius:10px !important; border:1px solid #0b6e4f !important; }
.infocard { background:white; border-radius:14px; padding:18px; text-align:center; border:1px solid #d9e9dd; margin-bottom:15px; }
.dataframe th { background:#0b6e4f !important; color:white !important; }
a { color:#0b6e4f; font-weight:700; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# UTIL
# =====================================================
def read_csv(path):
    try:
        return pd.read_csv(path)
    except:
        return pd.DataFrame()

def save_csv(df, path):
    df.to_csv(path, index=False)

def save_uploaded(uploaded, folder):
    if uploaded is None:
        return ""
    dest = folder / uploaded.name
    if dest.exists():
        dest = folder / f"{dest.stem}_{datetime.now().strftime('%Y%m%d%H%M%S')}{dest.suffix}"
    with open(dest, "wb") as f:
        f.write(uploaded.getbuffer())
    return str(dest)

def preview_link(path):
    if not path or pd.isna(path):
        return "-"
    return f"<a href='{path}' target='_blank'>Lihat Bukti</a>"

def log_activity(user, act):
    t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df = read_csv(FILE_LOG)
    df = pd.concat([df, pd.DataFrame([[t, user, act]], columns=df.columns)], ignore_index=True)
    save_csv(df, FILE_LOG)

# =====================================================
# LOAD DATA
# =====================================================
df_keu = read_csv(FILE_KEUANGAN)
df_barang = read_csv(FILE_BARANG)
df_log = read_csv(FILE_LOG)

# =====================================================
# HEADER
# =====================================================
st.markdown("""
<div class="header-box">
  <div class="header-title">Laporan Keuangan Musholla At-Taqwa</div>
  <div class="header-sub">Transparansi • Amanah • Profesional</div>
</div>
""", unsafe_allow_html=True)

# =====================================================
# LOGIN
# =====================================================
st.sidebar.header("Login sebagai")
level = st.sidebar.radio("", [
    "Publik","Ketua","Sekretaris",
    "Bendahara 1","Bendahara 2",
    "Koor Donasi 1","Koor Donasi 2"
])

if level != "Publik":
    pw = st.sidebar.text_input("Password", type="password")
    if level.lower() not in PANITIA or pw != PANITIA[level.lower()]:
        st.warning("🔒 Password salah")
        st.stop()

menu = st.sidebar.radio("Menu", ["💰 Keuangan","📦 Barang Masuk","📄 Laporan","🧾 Log"])

# =====================================================
# SESSION
# =====================================================
if "edit_barang" not in st.session_state:
    st.session_state.edit_barang = None

# =====================================================
# MENU BARANG MASUK (FIX + HIJAU NU)
# =====================================================
if menu == "📦 Barang Masuk":
    st.header("📦 Barang Masuk")

    st.subheader("Input Barang")
    if level != "Publik":
        tgl = st.date_input("Tanggal Barang")
        jenis = st.text_input("Jenis Barang")
        ket = st.text_input("Keterangan")
        jumlah = st.number_input("Jumlah", min_value=0)
        satuan = st.text_input("Satuan")
        bukti = st.file_uploader("Upload Bukti (pdf/jpg/png)", type=["pdf","jpg","jpeg","png"])

        if st.button("💾 Simpan Barang"):
            path = save_uploaded(bukti, UPLOADS_BAR)
            df_barang = pd.concat([df_barang, pd.DataFrame([{
                "tanggal": str(tgl),
                "jenis": jenis,
                "keterangan": ket,
                "jumlah": jumlah,
                "satuan": satuan,
                "bukti": path
            }])], ignore_index=True)
            save_csv(df_barang, FILE_BARANG)
            log_activity(level, "Input barang")
            st.success("Barang berhasil disimpan")

    st.subheader("Data Barang Masuk")
    if len(df_barang) > 0:
        df_show = df_barang.copy()
        df_show["Bukti"] = df_show["bukti"].apply(preview_link)
        df_show = df_show.rename(columns={
            "tanggal": "Tanggal",
            "jenis": "Jenis Barang",
            "keterangan": "Keterangan",
            "jumlah": "Jumlah",
            "satuan": "Satuan"
        })

        st.markdown(
            df_show[["Tanggal","Jenis Barang","Keterangan","Jumlah","Satuan","Bukti"]]
            .to_html(escape=False, index=True),
            unsafe_allow_html=True
        )

        if level == "Ketua":
            idx = st.number_input("Pilih nomor baris untuk edit", 0, len(df_barang)-1)
            if st.button("✏️ Edit Barang"):
                st.session_state.edit_barang = idx
                st.rerun()

    if level == "Ketua" and st.session_state.edit_barang is not None:
        i = st.session_state.edit_barang
        row = df_barang.iloc[i]

        st.subheader("✏️ Edit Barang")
        tgl = st.date_input("Tanggal", pd.to_datetime(row["tanggal"]))
        jenis = st.text_input("Jenis Barang", row["jenis"])
        ket = st.text_input("Keterangan", row["keterangan"])
        jumlah = st.number_input("Jumlah", min_value=0, value=int(row["jumlah"]))
        satuan = st.text_input("Satuan", row["satuan"])
        bukti = st.file_uploader("Ganti Bukti", type=["pdf","jpg","jpeg","png"])

        if st.button("💾 Simpan Perubahan"):
            path = row["bukti"]
            if bukti:
                path = save_uploaded(bukti, UPLOADS_BAR)
            df_barang.loc[i] = [str(tgl), jenis, ket, jumlah, satuan, path]
            save_csv(df_barang, FILE_BARANG)
            log_activity(level, "Edit barang")
            st.session_state.edit_barang = None
            st.success("Perubahan tersimpan")
            st.rerun()

        if st.button("🗑️ Hapus Barang"):
            df_barang = df_barang.drop(i).reset_index(drop=True)
            save_csv(df_barang, FILE_BARANG)
            log_activity(level, "Hapus barang")
            st.session_state.edit_barang = None
            st.rerun()

# =====================================================
# MENU LAIN (TETAP AMAN)
# =====================================================
elif menu == "📄 Laporan":
    st.header("📄 Laporan")
    st.info("Menu laporan tetap stabil")

elif menu == "🧾 Log":
    st.header("🧾 Log Aktivitas")
    st.dataframe(df_log, use_container_width=True)

elif menu == "💰 Keuangan":
    st.header("💰 Keuangan")
    st.info("Menu keuangan tetap stabil")
