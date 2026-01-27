import streamlit as st
from utils import fetch_one

st.title("📝 Pemberian Skor Karyawan")

nama_karyawan = st.text_input("Nama Karyawan")
departemen_karyawan = st.selectbox("Departemen Karyawan", ["Umum", "Teknis", "Pengolahan"])
periode = st.selectbox("Periode Penilaian", ["jan-feb", "feb-mar", "mar-apr", 
                                             "apr-mei", "mei-jun", "jun-jul", 
                                             "jul-agu", "agu-sep", "sep-okt", 
                                             "okt-nov", "nov-des", "des-jan"])

if st.button("🔍 Cari Karyawan"):
    karyawan = fetch_one(
        "SELECT * FROM user WHERE name_user = %s AND department = %s",
        (nama_karyawan.title(), departemen_karyawan)
    )
    if not karyawan:
        st.error("Karyawan tidak ditemukan. Silakan periksa kembali nama dan departemen.")
    else:
        st.success(f"Karyawan {nama_karyawan.title()} ditemukan!")
        st.session_state.karyawan_id = karyawan['id_user']
        st.session_state.nilai_akhir = None

    st.markdown("---")
    st.subheader("⭐ Skala Penilaian")
    st.info("⭐ = Sangat Kurang\n\n⭐⭐ = Kurang\n\n⭐⭐⭐ = Cukup\n\n⭐⭐⭐⭐ = Baik\n\n⭐⭐⭐⭐⭐ = Sangat Baik")
    # Form penilaian
    with st.form("form_penilaian"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**1. Kehadiran**")
            kehadiran = st.feedback("stars", key="kehadiran")
            
            st.write("**2. Kualitas Kerja**")
            kualitas_kerja = st.feedback("stars", key="kualitas_kerja")
            
            st.write("**3. Kedisiplinan**")
            kedisiplinan = st.feedback("stars", key="kedisiplinan")

            st.write("**4. Tanggung Jawab**")
            tanggung_jawab = st.feedback("stars", key="tanggung_jawab")
        
        with col2:
            st.write("**5. Kerjasama**")
            kerjasama = st.feedback("stars", key="kerjasama")
            
            st.write("**6. Inisiatif**")
            inisiatif = st.feedback("stars", key="inisiatif")

            st.write("**7. Komunikasi**")
            komunikasi = st.feedback("stars", key="komunikasi")

            st.write("**8. Kreativitas**")
            kreativitas = st.feedback("stars", key="kreativitas")

        if st.form_submit_button("✅ hitung", use_container_width=True):
            try:
                total = (kehadiran + kualitas_kerja + kedisiplinan + 
                        tanggung_jawab + kerjasama + inisiatif + 
                        komunikasi + kreativitas) + 8
                st.metric(label="Total Skor", value=(total-8)/(32)*100)
                st.session_state.nilai_akhir = (total-8)/(32)*100
            except Exception as e:
                st.error("berikan penilaian terlebih dahulu")

    if st.session_state.nilai_akhir is not None:

        if st.button("💾 Simpan Penilaian"):
            st.success("Penilaian berhasil disimpan!")