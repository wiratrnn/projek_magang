import streamlit as st
import pandas as pd
from utils import get_cursor

st.title("📊 Dashboard Manajer")

# Contoh query untuk menampilkan data karyawan
def fetch_karyawan_data():
    cursor = get_cursor()
    cursor.execute("SELECT id_user, name_user, email FROM user WHERE jabatan = 'karyawan'")
    return cursor.fetchall()

karyawan_data = fetch_karyawan_data()
if karyawan_data:
    st.markdown("### Aksi Penilaian")

    for row in karyawan_data:
        col1, col2 = st.columns([4, 1])

        col1.write(row["name_user"])

        if col2.button("Nilai", key=row["email"]):
            st.session_state.selected_karyawan = row["id_user"]
            st.session_state.selected_karyawan_name = row["name_user"]
            st.switch_page("manajer/penilaian.py")

else:
    st.write("Tidak ada data karyawan tersedia.")
st.markdown("---")
