import streamlit as st
from utils import get_connection
import time

# Inisialisasi session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None

def login_page():
    with st.container(border=True):
        # st.markdown("<h1 style='text-align: center; color: #1877F2; margin-bottom: 0px;'>SiPendEKar</h1>", unsafe_allow_html=True)
        # st.markdown("<h5 style='text-align: center; color: #666; margin-top: 0;'>(Sistem Penilaian dan Evaluasi Karyawan)</h5>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            img_col, text_col = st.columns([0.4, 1.6])
            with img_col:
                st.image("logoBPS.png", width=50)
            with text_col:
                st.markdown("<p style='margin: 0; padding-top: 5px; font-size: 18px; font-weight: bold; color: #1877F2;'>BPS Kabupaten Simalungun</p>", unsafe_allow_html=True)
        
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login", type="primary"):
            try:
                with get_connection() as conn:
                    with conn.cursor() as c:
                        c.execute("SELECT id_user, jabatan, name_user, email, password FROM user WHERE email = %s AND password = %s", (email, password))
                        user = c.fetchone()
                        if user:
                            st.success(f"Selamat datang, {user[2]}! 👋")
                            st.session_state['logged_in'] = True
                            st.session_state['user_id'] = user[0]
                            st.session_state['role'] = user[1]  # jabatan: Karyawan atau Manajer
                            st.session_state['name'] = user[2]
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Email atau password salah. Silakan coba lagi.")
                        
                        c.close()
                        conn.close()
            except Exception as e:
                st.error(f"Koneksi database error: {e}")

        st.info("ℹ️ Hubungi administrator untuk mereset password Anda.")

def logout():
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state['user_id'] = None
    st.session_state['name'] = None
    st.rerun()

logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

manajer_page_1 = st.Page("manajer/dashboard.py", title="dashboard", 
                  icon=":material/handyman:",
                  default=(st.session_state['role'] == "manajer"))
manajer_page_2 = st.Page("manajer/penilaian.py", title="penilaian", 
                  icon=":material/help:")

karyawan_page = st.Page("karyawan/dashboard.py", title="dashboard_karyawan",
                   icon=":material/security:",
                   default=(st.session_state['role'] == "karyawan"))

manajer_pages = [logout_page, manajer_page_1, manajer_page_2]
karyawan_pages = [logout_page, karyawan_page]

page_dict = {}
if st.session_state.role == "staff":
    # pg = st.navigation(karyawan_pages)
    page_dict["karyawan"] = karyawan_pages

if st.session_state.role == None:
    pass
else:
    page_dict["manajer"] = manajer_pages

if len(page_dict) > 0:
    pg = st.navigation(page_dict)
else:
    pg = st.navigation([st.Page(login_page)])

pg.run()