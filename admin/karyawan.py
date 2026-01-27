import streamlit as st
from utils import fetch_all
st.title("👥 Manajemen Karyawan")

data = fetch_all(
    """
    SELECT 
        u.id_user,
        u.name_user,
        u.email,
        n.nilai
    FROM user u
    LEFT JOIN appraisal n ON u.id_user = n.id_user
    WHERE u.jabatan = 'Staff'
    GROUP BY u.id_user, u.name_user, u.email, n.nilai
    """
)

for row in data:
    with st.container(border=True):
        col_nama, col_email, col_nilai, col_upd, col_info = st.columns([2, 2, 1, 0.9, 0.8], 
                                                                       vertical_alignment="center")

        col_nama.markdown(f"**Nama**: {row['name_user']}")
        col_email.markdown(f"**Email:** {row['email']}")
        col_nilai.markdown(f"**Nilai:** {row['nilai']}")

        with col_upd:
            if st.button("Update", key=f"update_{row['id_user']}", type="primary"):
                st.info(f"Update user ID {row['id_user']} masih dalam pengembangan")
        with col_info:
            if st.button("detail", key=f"info_{row['id_user']}"):
                st.info(f"Info user ID {row['id_user']} masih dalam pengembangan")