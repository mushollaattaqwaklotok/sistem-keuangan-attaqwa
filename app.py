import streamlit as st
import pandas as pd
import os
from datetime import datetime
from pathlib import Path

# =====================================================
#  KONFIGURASI AWAL
# =====================================================
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

FILE_KEUANGAN = DATA_DIR / "keuangan.csv"
FILE_BARANG = DATA_DIR / "barang.csv"
FILE_LOG = DATA_DIR / "log_aktivitas.csv"

# Jika file belum ada, buat template
if not FILE_KEUANGAN.exists():
    pd.DataFrame(columns=["Tanggal","Keterangan","Kategori","Masuk","Keluar","Saldo","bukti_url"]).to_csv(FILE_KEUANGAN, index=False)
if not FILE_BARANG.exists():
    pd.DataFrame(columns=["tanggal","nama_barang","jumlah","keterangan"]).to_csv(FILE_BARANG, index=False)
if not FILE_LOG.exists():
    pd.DataFrame(columns=["waktu","aksi","user"]).to_csv(FILE_LOG, index=False)

# =====================================================
#  KONFIGURASI USER LOGIN
# =====================================================
PUBLIC_PASSWORD = "publik123"
PANITIA_USERS = {
    "Ketua": "ketua123",
    "Bendahara": "bendahara123",
    "Pengawas": "pengawas123",
    "Sekretaris": "sekretaris123",
    "Logistik": "logistik123",
    "Humas": "humas123",
}

# =====================================================
#  FUNGSI UTILITAS
# =====================================================
def load_data():
    return pd.read_csv(FILE_KEUANGAN)

def load_barang():
    return pd.read_csv(FILE_BARANG)

def save_data(df):
    df.to_csv(FILE_KEUANGAN, index=False)

def save_barang(df):
    df.to_csv(FILE_BARANG, index=False)

def log_aktivitas(aksi, user):
    df = pd.read_csv(FILE_LOG)
    df.loc[len(df)] = [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), aksi, user]
    df.to_csv(FILE_LOG, index=False)

# =====================================================
#  LOGIN
# =====================================================
st.title("📊 Sistem Keuangan Musholla At-Taqwa RT 1")
st.subheader("Transparansi • Amanah • Profesional")

login_type = st.selectbox("Login sebagai:", ["Publik"] + list(PANITIA_USERS.keys()))
password = st.text_input("Password:", type="password")

login_success = False
current_user = None

if st.button("Login"):
    if login_type == "Publik" and password == PUBLIC_PASSWORD:
        login_success = True
        current_user = "Publik"
    elif login_type in PANITIA_USERS and password == PANITIA_USERS[login_type]:
        login_success = True
        current_user = login_type
    else:
        st.error("Password salah!")

# =====================================================
#  MAIN APP
# =====================================================
if login_success:
    st.success(f"Login berhasil sebagai {current_user}")

    menu = st.sidebar.radio("Menu:", ["💰 Keuangan", "📦 Barang Masuk", "📄 Laporan", "🧾 Log"])

    # =================================================
    #  MENU KEUANGAN
    # =================================================
    if menu == "💰 Keuangan":
        st.header("💰 Input Keuangan")
        df = load_data()

        if current_user != "Publik":
            tanggal = st.date_input("Tanggal", datetime.now())
            ket = st.text_input("Keterangan")
            kategori = st.selectbox("Kategori", ["Kas_Masuk", "Kas_Keluar"])
            masuk = st.number_input("Masuk", min_value=0)
            keluar = st.number_input("Keluar", min_value=0)
            bukti = st.text_input("URL Bukti (opsional)")

            if st.button("Simpan"):
                saldo_akhir = df["Saldo"].iloc[-1] + masuk - keluar if not df.empty else masuk
                df.loc[len(df)] = [str(tanggal), ket, kategori, masuk, keluar, saldo_akhir, bukti]
                save_data(df)
                log_aktivitas(f"Input keuangan: {ket}", current_user)
                st.success("Data berhasil disimpan!")

        st.subheader("Data Keuangan")
        st.dataframe(df)

    # =================================================
    #  MENU BARANG MASUK
    # =================================================
    if menu == "📦 Barang Masuk":
        st.header("📦 Input Barang Masuk")
        dfb = load_barang()

        if current_user != "Publik":
            tgl = st.date_input("Tanggal", datetime.now())
            nama = st.text_input("Nama Barang")
            jml = st.number_input("Jumlah", min_value=1)
            ketb = st.text_area("Keterangan")

            if st.button("Simpan Barang"):
                dfb.loc[len(dfb)] = [str(tgl), nama, jml, ketb]
                save_barang(dfb)
                log_aktivitas(f"Input barang: {nama}", current_user)
                st.success("Barang berhasil disimpan!")

        st.subheader("Data Barang Masuk")
        st.dataframe(dfb)

        if current_user != "Publik":
            st.subheader("✏ Edit / Hapus Barang")
            idx = st.number_input("Pilih index data", min_value=0, max_value=len(dfb)-1 if len(dfb)>0 else 0)

            if st.button("Hapus Data"):
                dfb = dfb.drop(idx).reset_index(drop=True)
                save_barang(dfb)
                log_aktivitas(f"Hapus barang index {idx}", current_user)
                st.success("Data dihapus!")

    # =================================================
    #  MENU LAPORAN
    # =================================================
    if menu == "📄 Laporan":
        st.header("📄 Laporan Keuangan")
        df = load_data()
        st.dataframe(df)

        # --- Tombol Download CSV ---
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Laporan CSV",
            data=csv,
            file_name=f"laporan_keuangan_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )

    # =================================================
    #  MENU LOG
    # =================================================
    if menu == "🧾 Log":
        st.header("🧾 Log Aktivitas")
        logdf = pd.read_csv(FILE_LOG)
        st.dataframe(logdf)
