import streamlit as st
from utils import fetch_one

if "user" not in st.session_state:
    st.session_state.user = None

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
        st.session_state.user = fetch_one(""" 
                        SELECT
                            id_user,
                            department,
                            name_user
                        FROM user
                        WHERE name_user = %s AND department = %s
                            """, (nama, unit))
        if st.session_state.user:
            st.toast(f"berhasil {st.session_state.user['name_user']}")
        else :
            st.error("Karyawan tidak ditemukan, perbaiki nama atau departmentnya")

if st.session_state.user:
    # Form penilaian
    with st.form("form_penilaian", clear_on_submit=False):
        with st.container(border=True):
            st.subheader("Disiplin")
            col_disiplin1, col_disiplin2, col_disiplin3= st.columns(3)
            ketepatan = col_disiplin1.number_input(f"**Ketepatan (10%)**", min_value=0, max_value=100, step=1, key="ketepatan")
            kerapihan = col_disiplin2.number_input(f"**Kerapihan (10%)**", min_value=0, max_value=100, step=1, key="kerapihan")
            waktu = col_disiplin3.number_input(f"**Waktu (10%)**", min_value=0, max_value=100, step=1, key="waktu")

        with st.container(border=True):
            st.subheader("Sikap Kerja")
            col_sikap1, col_sikap2 = st.columns(2)
            motivasi = col_sikap1.number_input(f"**Motivasi (15%)**", min_value=0, max_value=100, step=1, key="motivasi")
            komunikasi = col_sikap2.number_input(f"**Komunikasi (15%)**", min_value=0, max_value=100, step=1, key="komunikasi")

        with st.container(border=True):
            st.subheader("Hasil Kerja")
            col_kerja1, col_kerja2, col_kerja3 = st.columns(3)
            kualitas = col_kerja1.number_input(f"**Kualitas (15%)**", min_value=0, max_value=100, step=1, key="kualitas")
            kuantitas = col_kerja2.number_input(f"**Kuantitas (10%)**", min_value=0, max_value=100, step=1, key="kuantitas")
            tanggungjawab = col_kerja3.number_input(f"**Tanggungjawab (15%)**", min_value=0, max_value=100, step=1, key="tanggungjawab")
        
        if st.form_submit_button("✅ hitung", width='stretch', type="primary"):
            total = (ketepatan*0.1 + kerapihan*0.1 + waktu*0.1 +
                     motivasi*0.15 + komunikasi*0.15 +
                     kualitas*0.15 + kuantitas*0.1 + tanggungjawab*0.15)
            
            hasil0, hasil1, hasil2, hasil3 = st.columns(4)
            with hasil0:
                st.metric("Total Skor", f"{total:.2f}")
            with hasil1:
                st.metric("Disiplin", f"{ketepatan*0.1 + kerapihan*0.1 + waktu*0.1:.2f}")
            with hasil2:
                st.metric("Sikap Kerja", f"{motivasi*0.15 + komunikasi*0.15:.2f}")
            with hasil3:
                st.metric("Hasil Kerja", f"{kualitas*0.15 + kuantitas*0.1 + tanggungjawab*0.15:.2f}")
    
