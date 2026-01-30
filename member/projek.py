import streamlit as st

nama_projek = st.text_input("Nama Proyek")
deskripsi_projek = st.text_area("Deskripsi Proyek")
keterlibatan = st.selectbox("Keterlibatan Anggota Tim", 
                            options=["Ketua", "Anggota", 
                                    "Koordinator", "Supervisor"])
st.file_uploader("Unggah Dokumen Proyek", type=["pdf", "docx"])

if st.button("Simpan Proyek"):
    st.success(f"Proyek '{nama_projek}' berhasil disimpan!")

    st.info("Fitur penyimpanan proyek masih dalam pengembangan.")
