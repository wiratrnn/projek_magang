import streamlit as st
from utils import fetch_all

st.session_state.pop("target", None)
st.title("👥 Daftar Pegawai")

data = fetch_all(
    """
    SELECT 
        p.id_pegawai,
        p.nama,
        p.nip,
        p.unit_kerja,
        p.jabatan,
        p.jenis_kelamin,
        u.email
    FROM pegawai p
    JOIN users u ON u.id_user = p.id_pegawai;
    """
)

for row in data:
    with st.container(border=True):
        col_1, col_2 = st.columns([8, 1], vertical_alignment="center")
        with col_1:
            colNama, colEmail = st.columns(2)
            colNama.markdown(f"**Nama**: {row['nama']} || {row['unit_kerja']}")
            colEmail.markdown(f"**Email:** {row['email']}")

        with col_2:
            if st.button("detail", key=f"info_{row['id_pegawai']}"):
                st.session_state["id_pegawai_detail"] = row["id_pegawai"]
                st.session_state['nama_detail'] = row['nama']
                st.session_state["jabatan_detail"] = row['jabatan']
                st.session_state['nip_detail'] = row['nip']
                st.session_state['unit_kerja_detail'] = row['unit_kerja']
                st.session_state['email_detail'] = row['email']
                st.session_state['jenis_kelamin_detail'] = row['jenis_kelamin']
                st.switch_page("pages/data_pegawai.py")