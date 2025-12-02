import streamlit as st
import pandas as pd
import os
from datetime import datetime

# =====================================================
#  KONFIGURASI AWAL
# =====================================================

DATA_DIR = "data"
UPLOADS_DIR = "uploads"
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)

FILE_KEUANGAN = f"{DATA_DIR}/keuangan.csv"
FILE_BARANG = f"{DATA_DIR}/barang.csv"

PANITIA = {
    "ketua": "kelas3ku",
    "sekretaris": "fatik3762",
    "bendahara 1": "hadi5028",
    "bendahara 2": "riki6522",
    "koor donasi 1": "bayu0255",
    "koor donasi 2": "roni9044"
}

# =====================================================
#  UI PREMIUM – GOLD THEME
# =====================================================
st.markdown("""
<style>
.stApp { background-color: #faf7e8 !important; }

h1,h2,h3,h4 { color:#b8860b !important; font-weight:800; }

.header-box {
    background: linear-gradient(90deg,#b8860b,#e1c16e);
    padding:22px 26px; border-radius:14px;
    color:white !important; margin-bottom:16px;
}
.header-title { font-size:30px; font-weight:900; }

section[data-testid="stSidebar"] {
    background:#b8860b; padding:20px;
}
section[data-testid="stSidebar"] * { color:white !important; }

.stButton>button {
    background: linear-gradient(90deg,#b8860b,#e1c16e);
    color:white !important; font-weight:700;
    padding:8px 22px; border-radius:10px;
}
.stButton>button:hover {
    background: linear-gradient(90deg,#e1c16e,#b8860b);
    transform:scale(1.03);
}

input, textarea, select {
    border-radius:10px !important;
    border:1px solid #b8860b !important;
}

.infocard {
    background:white; border-radius:14px;
    padding:18px; text-align:center;
    border:1px solid #e2d6a6;
    margin-bottom:15px;
}
.infocard h3 { margin:4px 0; font-size:20px; }
.infocard p { margin:0; font-weight:700; font-size:18px; }
</style>
""", unsafe_allow_html=True)


# =====================================================
#  FUNGSI UTILITAS
# =====================================================
def load_csv(file, columns):
    if os.path.exists(file):
        try:
            return pd.read_csv(file)
        except:
            return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

def save_csv(df, file):
    df.to_csv(file, index=False)

def preview_link(url):
    if pd.isna(url) or url == "":
        return "-"
    return f"[Lihat Bukti]({url})"


# =====================================================
#  LOAD DATA
# =====================================================
df_keu = load_csv(FILE_KEUANGAN,
    ["Tanggal","Keterangan","Kategori","Masuk","Keluar","Saldo","bukti_url"]
)

df_barang = load_csv(FILE_BARANG,
    ["tanggal","jenis","keterangan","jumlah","satuan","bukti","bukti_penerimaan"]
)

# =====================================================
#  HEADER
# =====================================================
st.markdown("""
<div class="header-box">
    <div class="header-title">Sistem Keuangan Musholla At-Taqwa</div>
</div>
""", unsafe_allow_html=True)


# =====================================================
#  LOGIN
# =====================================================
st.sidebar.header("Login sebagai:")

level = st.sidebar.radio("", [
    "Publik",
    "Ketua",
    "Sekretaris",
    "Bendahara 1",
    "Bendahara 2",
    "Koor Donasi 1",
    "Koor Donasi 2"
], key="login_select")

if level != "Publik":
    password = st.sidebar.text_input("Password:", type="password", key="pw")
    key = level.lower()
    if key not in PANITIA or password != PANITIA[key]:
        st.warning("🔒 Masukkan password yang benar.")
        st.stop()


# =====================================================
#  MENU
# =====================================================
menu = st.sidebar.radio("Menu:", ["💰 Keuangan", "📦 Barang Masuk", "📄 Laporan"], key="menu")


# =====================================================
#  💰 MENU KEUANGAN
# =====================================================
if menu == "💰 Keuangan":

    st.header("💰 Keuangan")

    # Dashboard
    if len(df_keu) > 0:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"<div class='infocard'><h3>Total Masuk</h3><p>Rp {df_keu['Masuk'].sum():,}</p></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='infocard'><h3>Total Keluar</h3><p>Rp {df_keu['Keluar'].sum():,}</p></div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div class='infocard'><h3>Saldo Akhir</h3><p>Rp {df_keu['Saldo'].iloc[-1]:,}</p></div>", unsafe_allow_html=True)

    # -------------------------------------------------
    # INPUT KEUANGAN
    # -------------------------------------------------
    st.subheader("Input Keuangan")

    if level == "Publik":
        st.info("🔒 Hanya panitia yang dapat input data.")
    else:
        tgl = st.date_input("Tanggal", key="tgl_in")
        ket = st.text_input("Keterangan", key="ket_in")
        kategori = st.selectbox("Kategori", ["Kas Masuk", "Kas Keluar"], key="kat_in")
        masuk = st.number_input("Masuk (Rp)", min_value=0, key="masuk_in")
        keluar = st.number_input("Keluar (Rp)", min_value=0, key="keluar_in")
        bukti = st.file_uploader("Upload Bukti", key="bukti_in")

        if st.button("Simpan Data", key="save_in"):
            bukti_url = ""
            if bukti:
                bukti_url = f"{UPLOADS_DIR}/{bukti.name}"
                with open(bukti_url, "wb") as f:
                    f.write(bukti.read())

            saldo_akhir = (df_keu["Saldo"].iloc[-1] if len(df_keu) else 0) + masuk - keluar

            df_keu.loc[len(df_keu)] = [
                str(tgl), ket, kategori, masuk, keluar, saldo_akhir, bukti_url
            ]

            save_csv(df_keu, FILE_KEUANGAN)
            st.success("Data berhasil disimpan!")
            st.rerun()

    # -------------------------------------------------
    #  TABEL + EDIT MODE
    # -------------------------------------------------
    st.subheader("Laporan Keuangan")

    if len(df_keu) > 0:

        df_show = df_keu.copy()
        df_show["Bukti"] = df_show["bukti_url"].apply(preview_link)

        st.write(df_show.to_html(escape=False), unsafe_allow_html=True)

        # =======================
        # EDIT MODE KHUSUS KETUA
        # =======================
        if level == "Ketua":
            st.write("---")
            st.subheader("✏️ Edit Data")

            row_id = st.number_input(
                "Pilih baris yang akan diedit (mulai dari 0)",
                min_value=0,
                max_value=len(df_keu)-1,
                key="edit_row"
            )

            row = df_keu.loc[row_id]

            tgl_e = st.date_input("Tanggal", value=pd.to_datetime(row["Tanggal"]), key="tgl_edit")
            ket_e = st.text_input("Keterangan", value=row["Keterangan"], key="ket_edit")
            kategori_e = st.selectbox("Kategori", ["Kas Masuk", "Kas Keluar"], index=0 if row["Kategori"]=="Kas Masuk" else 1, key="kat_edit")
            masuk_e = st.number_input("Masuk", min_value=0, value=int(row["Masuk"]), key="masuk_edit")
            keluar_e = st.number_input("Keluar", min_value=0, value=int(row["Keluar"]), key="keluar_edit")

            if st.button("Simpan Perubahan", key="save_edit"):
                df_keu.loc[row_id, "Tanggal"] = str(tgl_e)
                df_keu.loc[row_id, "Keterangan"] = ket_e
                df_keu.loc[row_id, "Kategori"] = kategori_e
                df_keu.loc[row_id, "Masuk"] = masuk_e
                df_keu.loc[row_id, "Keluar"] = keluar_e

                # hitung ulang saldo
                saldo = 0
                new_saldo = []
                for i, r in df_keu.iterrows():
                    saldo += r["Masuk"] - r["Keluar"]
                    new_saldo.append(saldo)
                df_keu["Saldo"] = new_saldo

                save_csv(df_keu, FILE_KEUANGAN)
                st.success("Data berhasil diperbarui!")
                st.rerun()


# =====================================================
#  📄 LAPORAN
# =====================================================
elif menu == "📄 Laporan":

    st.header("📄 Laporan Keuangan")

    if len(df_keu) > 0:
        df_show = df_keu.copy()
        df_show["Bukti"] = df_show["bukti_url"].apply(preview_link)
        st.write(df_show.to_html(escape=False), unsafe_allow_html=True)
    else:
        st.info("Belum ada data.")


# =====================================================
#  📦 BARANG MASUK
# =====================================================
elif menu == "📦 Barang Masuk":

    st.header("📦 Barang Masuk")

    if level == "Publik":
        st.info("🔒 Hanya panitia yang dapat input.")
        st.write(df_barang)
    else:
        tgl_b = st.date_input("Tanggal", key="tgl_b")
        jenis_b = st.text_input("Jenis Barang", key="jenis_b")
        ket_b = st.text_input("Keterangan", key="ket_b")
        jml_b = st.number_input("Jumlah", min_value=0, key="jml_b")
        satuan_b = st.text_input("Satuan", key="satuan_b")
        bukti_b = st.file_uploader("Upload Bukti", key="bukti_b")

        if st.button("Simpan Barang", key="save_b"):
            bukti_url = ""
            if bukti_b:
                bukti_url = f"{UPLOADS_DIR}/{bukti_b.name}"
                with open(bukti_url, "wb") as f:
                    f.write(bukti_b.read())

            df_barang.loc[len(df_barang)] = [
                str(tgl_b), jenis_b, ket_b, jml_b, satuan_b, bukti_url, bukti_url
            ]

            save_csv(df_barang, FILE_BARANG)
            st.success("Berhasil disimpan!")
            st.rerun()

    st.write(df_barang)
