# =====================================================
#  APP.PY FINAL – SISTEM KEUANGAN MUSHOLLA AT-TAQWA
#  HIJAU NU | LOGIN | LOG | CSV | PDF LAPORAN
# =====================================================

import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
from io import BytesIO
import os

# =====================================================
#  KONFIGURASI DIREKTORI
# =====================================================
BASE_DIR = Path(".")
DATA_DIR = BASE_DIR / "data"
os.makedirs(DATA_DIR, exist_ok=True)

FILE_KEUANGAN = DATA_DIR / "keuangan.csv"
FILE_BARANG   = DATA_DIR / "barang.csv"
FILE_LOG      = DATA_DIR / "log_aktivitas.csv"

# =====================================================
#  INISIAL FILE
# =====================================================
if not FILE_KEUANGAN.exists():
    pd.DataFrame(columns=[
        "Tanggal","Keterangan","Kategori","Masuk","Keluar","Saldo"
    ]).to_csv(FILE_KEUANGAN, index=False)

if not FILE_BARANG.exists():
    pd.DataFrame(columns=[
        "tanggal","jenis","keterangan","jumlah","satuan"
    ]).to_csv(FILE_BARANG, index=False)

if not FILE_LOG.exists():
    pd.DataFrame(columns=[
        "Waktu","User","Aktivitas"
    ]).to_csv(FILE_LOG, index=False)

# =====================================================
#  AKUN PANITIA
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
#  STREAMLIT CONFIG & TEMA
# =====================================================
st.set_page_config(page_title="Musholla At-Taqwa", layout="wide")

st.markdown("""
<style>
.stApp { background:#f1f6f2; }
h1,h2,h3,h4 { color:#0b6e4f; font-weight:800; }
.header-box {
    background:linear-gradient(90deg,#064635,#0b6e4f);
    padding:22px; border-radius:14px;
    color:white; margin-bottom:18px;
}
section[data-testid="stSidebar"] { background:#0b6e4f; }
section[data-testid="stSidebar"] * { color:white !important; }
.stButton>button {
    background:linear-gradient(90deg,#0b6e4f,#18a36d);
    color:white; font-weight:700;
    border-radius:10px;
}
.infocard {
    background:white; border-radius:14px;
    padding:18px; border:1px solid #d9e9dd;
    text-align:center;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
#  UTIL
# =====================================================
def read_csv(path):
    try:
        return pd.read_csv(path)
    except:
        return pd.DataFrame()

def save_csv(df, path):
    df.to_csv(path, index=False)

def log_activity(user, aktivitas):
    df = read_csv(FILE_LOG)
    df.loc[len(df)] = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        user,
        aktivitas
    ]
    save_csv(df, FILE_LOG)

# =====================================================
#  LOAD DATA
# =====================================================
df_keu = read_csv(FILE_KEUANGAN)
df_bar = read_csv(FILE_BARANG)

if not df_keu.empty:
    df_keu["Masuk"]  = pd.to_numeric(df_keu["Masuk"], errors="coerce").fillna(0)
    df_keu["Keluar"] = pd.to_numeric(df_keu["Keluar"], errors="coerce").fillna(0)
    df_keu["Saldo"]  = (df_keu["Masuk"] - df_keu["Keluar"]).cumsum()

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
level = st.sidebar.radio(
    "", ["Publik","Ketua","Sekretaris","Bendahara 1","Bendahara 2","Koor Donasi 1","Koor Donasi 2"]
)

if level != "Publik":
    pw = st.sidebar.text_input("Password", type="password")
    if PANITIA.get(level.lower()) != pw:
        st.warning("❌ Password salah")
        st.stop()

menu = st.sidebar.radio("📂 Menu", [
    "💰 Keuangan",
    "📦 Barang Masuk",
    "📄 Laporan",
    "🧾 Log"
])

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

        st.download_button(
            "📥 Download Keuangan (CSV)",
            df_keu.to_csv(index=False),
            "keuangan.csv",
            "text/csv"
        )
    else:
        st.info("Belum ada data keuangan.")

# =====================================================
#  MENU BARANG
# =====================================================
elif menu == "📦 Barang Masuk":

    st.subheader("📦 Data Barang Masuk")

    if df_bar.empty:
        st.info("Belum ada data barang.")
    else:
        st.dataframe(df_bar, use_container_width=True)

        st.download_button(
            "📥 Download Barang Masuk (CSV)",
            df_bar.to_csv(index=False),
            "barang_masuk.csv",
            "text/csv"
        )

# =====================================================
#  MENU LAPORAN (PDF)
# =====================================================
elif menu == "📄 Laporan":

    st.subheader("📄 Laporan Resmi")

    st.markdown("### 💰 Keuangan")
    st.dataframe(df_keu, use_container_width=True)

    st.markdown("### 📦 Barang Masuk")
    st.dataframe(df_bar, use_container_width=True)

    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors

    def generate_pdf():
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        el = []

        el.append(Paragraph("<b>MUSHOLLA AT-TAQWA</b>", styles["Title"]))
        el.append(Paragraph("LAPORAN KEUANGAN & BARANG MASUK", styles["Heading2"]))
        el.append(Paragraph(f"Tanggal Cetak: {datetime.now().strftime('%d %B %Y')}", styles["Normal"]))
        el.append(Spacer(1,12))

        data = [["Tanggal","Keterangan","Masuk","Keluar","Saldo"]]
        for _, r in df_keu.iterrows():
            data.append([r["Tanggal"],r["Keterangan"],r["Masuk"],r["Keluar"],r["Saldo"]])

        tbl = Table(data, repeatRows=1)
        tbl.setStyle(TableStyle([
            ("GRID",(0,0),(-1,-1),0.5,colors.grey),
            ("BACKGROUND",(0,0),(-1,0),colors.lightgrey)
        ]))
        el.append(tbl)

        el.append(Spacer(1,20))
        el.append(Paragraph(
            "Ketua: Ferri Kusuma<br/>"
            "Sekretaris: Alfan Fatichul Ichsan<br/>"
            "Bendahara: Sunhadi Prayitno",
            styles["Normal"]
        ))

        doc.build(el)
        buffer.seek(0)
        return buffer

    st.download_button(
        "📥 Download Laporan PDF",
        generate_pdf(),
        "Laporan_Musholla_At-Taqwa.pdf",
        "application/pdf"
    )

# =====================================================
#  MENU LOG
# =====================================================
elif menu == "🧾 Log":

    if level == "Publik":
        st.warning("🔒 Log hanya untuk panitia")
        st.stop()

    df_log = read_csv(FILE_LOG)

    if df_log.empty:
        st.info("Belum ada log.")
    else:
        st.dataframe(df_log, use_container_width=True)

        st.download_button(
            "📥 Download Log (CSV)",
            df_log.to_csv(index=False),
            "log_aktivitas.csv",
            "text/csv"
        )
