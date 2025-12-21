# =====================================================
#  APP.PY FINAL – MUSHOLLA AT-TAQWA
#  HIJAU NU | LOGIN | INPUT TERPISAH | PDF RESMI
# =====================================================

import streamlit as st
import pandas as pd
import os
from datetime import datetime
from pathlib import Path
from io import BytesIO

# =====================================================
#  KONFIGURASI DIREKTORI
# =====================================================
BASE_DIR = Path(".")
DATA_DIR = BASE_DIR / "data"
os.makedirs(DATA_DIR, exist_ok=True)

FILE_KEUANGAN = DATA_DIR / "keuangan.csv"
FILE_BARANG   = DATA_DIR / "barang.csv"
FILE_LOG      = DATA_DIR / "log.csv"

# =====================================================
#  INISIAL FILE
# =====================================================
if not FILE_KEUANGAN.exists():
    pd.DataFrame(columns=[
        "Tanggal","Keterangan","Kategori","Masuk","Keluar","Saldo"
    ]).to_csv(FILE_KEUANGAN, index=False)

if not FILE_BARANG.exists():
    pd.DataFrame(columns=[
        "Tanggal","Jenis","Keterangan","Jumlah","Satuan"
    ]).to_csv(FILE_BARANG, index=False)

if not FILE_LOG.exists():
    pd.DataFrame(columns=["Waktu","User","Aktivitas"]).to_csv(FILE_LOG, index=False)

# =====================================================
#  AKUN PANITIA
# =====================================================
PANITIA = {
    "ketua":"kelas3ku",
    "sekretaris":"fatik3762",
    "bendahara 1":"hadi5028",
    "bendahara 2":"riki6522",
    "koor donasi 1":"bayu0255",
    "koor donasi 2":"roni9044"
}

# =====================================================
#  STREAMLIT & TEMA
# =====================================================
st.set_page_config("Manajemen Musholla At-Taqwa", layout="wide")

st.markdown("""
<style>
.stApp {background:#f1f6f2;}
h1,h2,h3,h4 {color:#D4AF37;font-weight:800;}
.header-box{
    background:linear-gradient(90deg,#064635,#0b6e4f);
    padding:22px;border-radius:14px;color:#D4AF37;margin-bottom:18px;
}
section[data-testid="stSidebar"]{background:#0b6e4f;}
section[data-testid="stSidebar"] *{color:white!important;}
.stButton>button{
    background:linear-gradient(90deg,#0b6e4f,#18a36d);
    color:white;font-weight:700;border-radius:10px;
}
.infocard{
    background:white;border-radius:14px;padding:18px;
    border:1px solid #d9e9dd;text-align:center;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
#  UTIL
# =====================================================
def read_csv(path):
    try: return pd.read_csv(path)
    except: return pd.DataFrame()

def log(user, aksi):
    df = read_csv(FILE_LOG)
    df.loc[len(df)] = [datetime.now(), user, aksi]
    df.to_csv(FILE_LOG, index=False)

# =====================================================
#  LOAD DATA
# =====================================================
df_keu = read_csv(FILE_KEUANGAN)
df_barang = read_csv(FILE_BARANG)

if not df_keu.empty:
    df_keu["Masuk"]  = pd.to_numeric(df_keu["Masuk"], errors="coerce").fillna(0)
    df_keu["Keluar"] = pd.to_numeric(df_keu["Keluar"], errors="coerce").fillna(0)
    df_keu["Saldo"]  = (df_keu["Masuk"] - df_keu["Keluar"]).cumsum()

# =====================================================
#  PDF
# =====================================================
def generate_pdf(df_keu, df_barang):
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors

    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4)
    s = getSampleStyleSheet()
    el = []

    el.append(Paragraph("<b>MUSHOLLA AT-TAQWA</b>", s["Title"]))
    el.append(Paragraph("LAPORAN RESMI KEUANGAN & BARANG", s["Heading2"]))
    el.append(Paragraph(f"Tanggal Cetak: {datetime.now().strftime('%d %B %Y')}", s["Normal"]))
    el.append(Spacer(1,12))

    el.append(Paragraph("<b>Laporan Keuangan</b>", s["Heading3"]))
    data = [["Tanggal","Keterangan","Masuk","Keluar","Saldo"]]
    for _,r in df_keu.iterrows():
        data.append([r["Tanggal"],r["Keterangan"],
                     f"{r['Masuk']:,.0f}",f"{r['Keluar']:,.0f}",f"{r['Saldo']:,.0f}"])
    t = Table(data, repeatRows=1)
    t.setStyle(TableStyle([
        ("GRID",(0,0),(-1,-1),0.5,colors.grey),
        ("BACKGROUND",(0,0),(-1,0),colors.lightgrey),
        ("ALIGN",(2,1),(-1,-1),"RIGHT")
    ]))
    el.append(t); el.append(Spacer(1,14))

    if not df_barang.empty:
        el.append(Paragraph("<b>Laporan Barang Masuk</b>", s["Heading3"]))
        data2 = [["Tanggal","Jenis","Keterangan","Jumlah","Satuan"]]
        for _,r in df_barang.iterrows():
            data2.append([
    r.get("Tanggal", r.get("tanggal","")),
    r.get("Jenis", r.get("jenis","")),
    r.get("Keterangan", r.get("keterangan","")),
    r.get("Jumlah", r.get("jumlah","")),
    r.get("Satuan", r.get("satuan",""))
])
        tb = Table(data2, repeatRows=1)
        tb.setStyle(TableStyle([
            ("GRID",(0,0),(-1,-1),0.5,colors.grey),
            ("BACKGROUND",(0,0),(-1,0),colors.lightgrey)
        ]))
        el.append(tb)

    el.append(Spacer(1,20))
    el.append(Paragraph(
        "Ketua: Ferri Kusuma<br/>"
        "Sekretaris: Alfan Fatichul Ichsan<br/>"
        "Bendahara: Sunhadi Prayitno", s["Normal"]
    ))

    doc.build(el)
    buf.seek(0)
    return buf

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
level = st.sidebar.radio("",["Publik","Ketua","Sekretaris","Bendahara 1","Bendahara 2","Koor Donasi 1","Koor Donasi 2"])

user = "Publik"
if level!="Publik":
    pw = st.sidebar.text_input("Password",type="password")
    if PANITIA.get(level.lower())!=pw:
        st.stop()
    user = level

menu = st.sidebar.radio("📂 Menu",[
    "💰 Keuangan","➕ Input Keuangan",
    "📦 Barang Masuk","➕ Input Barang",
    "📄 Laporan","🧾 Log"
])

# =====================================================
#  💰 KEUANGAN
# =====================================================
if menu=="💰 Keuangan":
    c1,c2,c3 = st.columns(3)
    c1.markdown(f"<div class='infocard'><h4>Total Masuk</h4><h3>Rp {df_keu['Masuk'].sum():,.0f}</h3></div>",unsafe_allow_html=True)
    c2.markdown(f"<div class='infocard'><h4>Total Keluar</h4><h3>Rp {df_keu['Keluar'].sum():,.0f}</h3></div>",unsafe_allow_html=True)
    c3.markdown(f"<div class='infocard'><h4>Saldo Akhir</h4><h3>Rp {df_keu['Saldo'].iloc[-1] if not df_keu.empty else 0:,.0f}</h3></div>",unsafe_allow_html=True)
    st.dataframe(df_keu, use_container_width=True)

# =====================================================
#  ➕ INPUT KEUANGAN
# =====================================================
elif menu=="➕ Input Keuangan" and user!="Publik":
    with st.form("keu"):
        tgl = st.date_input("Tanggal")
        ket = st.text_input("Keterangan")
        jenis = st.selectbox("Jenis",["Kas Masuk","Kas Keluar"])
        nom = st.number_input("Nominal",min_value=0)
        if st.form_submit_button("💾 Simpan"):
            df_keu.loc[len(df_keu)] = [
                tgl,ket,jenis,
                nom if jenis=="Kas Masuk" else 0,
                nom if jenis=="Kas Keluar" else 0,
                0
            ]
            df_keu.to_csv(FILE_KEUANGAN,index=False)
            log(user,"Input Keuangan")
            st.success("Tersimpan"); st.rerun()

# =====================================================
#  📦 BARANG
# =====================================================
elif menu=="📦 Barang Masuk":
    st.dataframe(df_barang,use_container_width=True)

elif menu=="➕ Input Barang" and user!="Publik":
    with st.form("barang"):
        tgl = st.date_input("Tanggal")
        jns = st.text_input("Jenis")
        ket = st.text_input("Keterangan")
        jml = st.number_input("Jumlah",min_value=0)
        sat = st.text_input("Satuan")
        if st.form_submit_button("💾 Simpan"):
            df_barang.loc[len(df_barang)] = [tgl,jns,ket,jml,sat]
            df_barang.to_csv(FILE_BARANG,index=False)
            log(user,"Input Barang")
            st.success("Tersimpan"); st.rerun()

# =====================================================
#  📄 LAPORAN
# =====================================================
elif menu=="📄 Laporan":
    st.dataframe(df_keu,use_container_width=True)
    st.dataframe(df_barang,use_container_width=True)
    st.download_button(
        "📥 Download Laporan PDF Resmi",
        generate_pdf(df_keu,df_barang),
        "Laporan_Musholla_At-Taqwa.pdf",
        "application/pdf"
    )

# =====================================================
#  🧾 LOG
# =====================================================
elif menu=="🧾 Log":
    st.dataframe(read_csv(FILE_LOG),use_container_width=True)
