import streamlit as st
from utils import fetch_one

user = None

st.title("📝 Pemberian Skor Karyawan")
nama_karyawan = fetch_one("SELECT GROUP_CONCAT(name_user ORDER BY name_user) AS names FROM user")

with st.form("Pencarian Karyawan", border=False):
    col1, col2 = st.columns(2)
    with col1:
        nama = st.selectbox("Nama Karyawan", nama_karyawan["names"].split(","), placeholder="pilih", index=None )
        bulan = st.selectbox("Periode Penilaian", ["jan", "feb", "mar", "apr", "mei", "jun", 
                                                    "jul", "agu", "sep", "okt", "nov", "des"])

    with col2:
        unit = st.selectbox("Unit Kerja", ["Umum", "Teknis", "Pengolahan"])
        tahun = st.selectbox("Tahun Penilaian", ["2022", "2023", "2024", "2025", 
                                                "2026", "2027", "2028", "2029"])
    if st.form_submit_button("🔍 Cari", type="primary"):
        user = fetch_one(""" 
                        SELECT
                            id_user,
                            department,
                            name_user
                        FROM user
                        WHERE name_user = %s AND department = %s
                            """, (nama, unit))
        if user:
            st.toast(f"berhasil {user['name_user']}")
        else :
            st.error("Karyawan tidak ditemukan, perbaiki nama atau departmentnya")

if user:
    # Form penilaian
    with st.form("form_penilaian", clear_on_submit=False):
        with st.container(border=True):
            st.subheader("Disiplin")
            col_disiplin1, col_disiplin2 = st.columns(2)
            ketepatan = col_disiplin1.number_input(f"**Ketepatan**", min_value=0, max_value=100, step=1, key="ketepatan")
            absensi = col_disiplin2.number_input(f"**Absensi**", min_value=0, max_value=100, step=1, key="absensi")

        with st.container(border=True):
            st.subheader("Sikap Kerja")
            col_sikap1, col_sikap2 = st.columns(2)
            motivasi = col_sikap1.number_input(f"**Motivasi**", min_value=0, max_value=100, step=1, key="motivasi")
            komunikasi = col_sikap2.number_input(f"**Komunikasi**", min_value=0, max_value=100, step=1, key="komunikasi")

        with st.container(border=True):
            st.subheader("Potensi Kemampuan")
            col_potensi1, col_potensi2, col_potensi3 = st.columns(3)
            pemahaman = col_potensi1.number_input(f"**Pemahaman dan Penugasan**", min_value=0, max_value=100, step=1, key="pemahaman")
            pengembangan = col_potensi2.number_input(f"**Pengembangan Diri**", min_value=0, max_value=100, step=1, key="pengembangan")
            teoritis = col_potensi3.number_input(f"**Teoritis**", min_value=0, max_value=100, step=1, key="teoritis")

        with st.container(border=True):
            st.subheader("Hasil Kerja")
            col_kerja1, col_kerja2 = st.columns(2)
            mutu = col_kerja1.number_input(f"**Mutu**", min_value=0, max_value=100, step=1, key="mutu")
            kuantitas = col_kerja2.number_input(f"**Kuantitas**", min_value=0, max_value=100, step=1, key="kuantitas")
        
        if st.form_submit_button("✅ hitung", width='stretch', type="primary"):
            total = (ketepatan*0.15 + absensi*0.15 + 
                     motivasi*0.2 + komunikasi*0.2 +
                     pemahaman*0.15 + pengembangan*0.10 + teoritis*0.10 + 
                     mutu*0.15 + kuantitas*0.15)
            st.metric(label="Total Skor", value=f"{(total/135)*100:.2f}")
    
