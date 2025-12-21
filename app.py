# =====================================================
#  APP.PY FINAL – SISTEM KEUANGAN MUSHOLLA AT-TAQWA
# =====================================================

import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
from io import BytesIO
import os

# =====================================================
#  KONFIGURASI
# =====================================================
BASE_DIR = Path(".")
DATA_DIR = BASE_DIR / "data"
os.makedirs(DATA_DIR, exist_ok=True)

FILE_KEU = DATA_DIR / "keuangan.csv"
FILE_BAR = DATA_DIR / "barang.csv"
FILE_LOG = DATA_DIR / "log_aktivitas.csv"

for f, cols in {
    FILE_KEU: ["Tanggal","Keterangan","Kategori","Masuk","Keluar","Saldo"],
    FILE_BAR: ["tanggal","jenis","keterangan","jumlah","satuan"],
    FILE_LOG: ["Waktu","User","Aktivitas"]
}.items():
    if not f.exists():
        pd.DataFrame(columns=cols).to_csv(f, index=False)

PANITIA = {
    "ketua": "kelas3ku",
    "sekretaris": "fatik3762",
    "bendahara 1": "hadi5028",
    "bendahara 2": "riki6522",
    "koor donasi 1": "bayu0255",
    "koor donasi 2": "roni9044"
}

# =====================================================
#  TEMA
# =====================================================
st.set_page_config(page_title="Musholla At-Taqwa", layout="wide")

st.markdown("""
<style>
.stApp { background:#f1f6f2; }
h1,h2,h3,h4 { color:#1b9e77; font-weight:800; }
.header-box {
    background:linear-gradient(90deg,#064635,#0b6e4f);
    padding:22px;border-radius:14px;
    color:white;margin-bottom:18px;
}
section[data-testid="stSidebar"] { background:#0b6e4f; }
section[data-testid="stSidebar"] * { color:white !important; }
.infocard {
    background:white;border-radius:14px;
    padding:18px;border:1px solid #d9e9dd;
    text-align:center;
}
.stButton>button {
    background:linear-gradient(90deg,#0b6e4f,#18a36d);
    color:white;font-weight:700;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
#  UTIL
# =====================================================
def load_csv(path):
    return pd.read_csv(path)

def save_csv(df, path):
    df.to_csv(path, index=False)

def log_activity(user, act):
    df = load_csv(FILE_LOG)
    df.loc[len(df)] = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        user,
        act
    ]
    save_csv(df, FILE_LOG)

# =====================================================
#  LOAD DATA
# =====================================================
df_keu = load_csv(FILE_KEU)
df_bar = load_csv(FILE_BAR)

if not df_keu.empty:
    df_keu["Masuk"] = pd.to_numeric(df_keu["Masuk"], errors="coerce").fillna(0)
    df_keu["Keluar"] = pd.to_numeric(df_keu["Keluar"], errors="coerce").fillna(0)
    df_keu["Saldo"] = (df_keu["Masuk"] - df_keu["Keluar"]).cumsum()

# =====================================================
#  HEADER
# =====================================================
st.markdown("""
<div class="header-box">
<h2>📊 Sistem Keuangan Musholla At-Taqwa</h2>
Transparansi • Amanah • Profesional
</div>
""", unsafe_allow_html=True)

# =====================================================
#  LOGIN
# =====================================================
st.sidebar.header("🔐 Login")
level = st.sidebar.radio("", ["Publik","Ketua","Sekretaris","Bendahara 1","Bendahara 2","Koor Donasi 1","Koor Donasi 2"])

if level != "Publik":
    pw = st.sidebar.text_input("Password", type="password")
    if PANITIA.get(level.lower()) != pw:
        st.stop()

menu = st.sidebar.radio("📂 Menu", ["💰 Keuangan","📦 Barang Masuk","📄 Laporan","🧾 Log"])

# =====================================================
#  MENU KEUANGAN
# =====================================================
if menu == "💰 Keuangan":

    st.subheader("💰 Ringkasan Keuangan")

    if not df_keu.empty:
        c1,c2,c3 = st.columns(3)
        c1.markdown(f"<div class='infocard'><h4>Total Masuk</h4><h3>Rp {df_keu['Masuk'].sum():,.0f}</h3></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='infocard'><h4>Total Keluar</h4><h3>Rp {df_keu['Keluar'].sum():,.0f}</h3></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='infocard'><h4>Saldo Akhir</h4><h3>Rp {df_keu['Saldo'].iloc[-1]:,.0f}</h3></div>", unsafe_allow_html=True)

    st.markdown("### 📄 Detail Transaksi")
    st.dataframe(df_keu, use_container_width=True)

    # ---------- DOWNLOAD ----------
    st.download_button(
        "📥 Download Keuangan (CSV)",
        df_keu.to_csv(index=False),
        "keuangan.csv",
        "text/csv"
    )

    # ---------- INPUT / EDIT / HAPUS ----------
    if level != "Publik":

        st.markdown("### ➕ Tambah Data Keuangan")
        with st.form("add_keu"):
            tgl = st.date_input("Tanggal")
            ket = st.text_input("Keterangan")
            masuk = st.number_input("Masuk", min_value=0)
            keluar = st.number_input("Keluar", min_value=0)
            submit = st.form_submit_button("Simpan")

            if submit:
                df_keu.loc[len(df_keu)] = [tgl, ket, "", masuk, keluar, 0]
                save_csv(df_keu, FILE_KEU)
                log_activity(level, "Tambah data keuangan")
                st.success("Data tersimpan")
                st.rerun()

        st.markdown("### ✏️ Edit / 🗑️ Hapus Data")
        idx = st.number_input("Index data", min_value=0, max_value=len(df_keu)-1 if len(df_keu)>0 else 0)
        if st.button("🗑️ Hapus"):
            df_keu = df_keu.drop(idx).reset_index(drop=True)
            save_csv(df_keu, FILE_KEU)
            log_activity(level, f"Hapus data keuangan index {idx}")
            st.success("Data dihapus")
            st.rerun()

# =====================================================
#  MENU BARANG (STRUKTUR SAMA)
# =====================================================
elif menu == "📦 Barang Masuk":

    st.dataframe(df_bar, use_container_width=True)

    st.download_button(
        "📥 Download Barang (CSV)",
        df_bar.to_csv(index=False),
        "barang.csv",
        "text/csv"
    )

    if level != "Publik":
        with st.form("add_bar"):
            tgl = st.date_input("Tanggal")
            jenis = st.text_input("Jenis")
            ket = st.text_input("Keterangan")
            jml = st.number_input("Jumlah", min_value=0)
            sat = st.text_input("Satuan")
            if st.form_submit_button("Simpan"):
                df_bar.loc[len(df_bar)] = [tgl, jenis, ket, jml, sat]
                save_csv(df_bar, FILE_BAR)
                log_activity(level, "Tambah data barang")
                st.success("Data tersimpan")
                st.rerun()

# =====================================================
#  MENU LOG
# =====================================================
elif menu == "🧾 Log":

    if level == "Publik":
        st.stop()

    df_log = load_csv(FILE_LOG)
    st.dataframe(df_log, use_container_width=True)

    st.download_button(
        "📥 Download Log (CSV)",
        df_log.to_csv(index=False),
        "log_aktivitas.csv",
        "text/csv"
    )
