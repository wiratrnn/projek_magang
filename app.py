from streamlit_cookies_controller import CookieController
import streamlit as st
from utils import fetch_one
import time

st.set_page_config(page_title="SiPENDEKAR", page_icon="logoBPS.png")

cookie = CookieController()

if "is_login" not in st.session_state:
    time.sleep(2)
    st.session_state.is_login = cookie.get("is_login") == True
    st.session_state.role = cookie.get("role")
    st.session_state.id_user = cookie.get("id_user")

def login_page():
    with st.container(border=True):
        st.title(":blue[SI]:green[PEND]:orange[EKAR]", text_alignment="center")
        st.markdown("<h5 style='text-align: center; color: #666;'>(Sistem Penilaian dan Evaluasi Karyawan)</h5>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([0.5, 2, 0.5])
        with col2:
            left, colImg, colText, right = st.columns([2, 1.8, 9, 2])
            colImg.image("logoBPS.png")
            colText.markdown("<p style='font-size: 20px; font-weight: 600;'>BPS Kabupaten Simalungun</p>", unsafe_allow_html=True)
            
            with st.form(key="login_form", border=True):
                email = st.text_input("e",placeholder="username", label_visibility='hidden')
                password = st.text_input("p",placeholder="Password", type="password", label_visibility='collapsed')

                if st.form_submit_button("Login", type="primary"):
                    with st.spinner("Memproses login..."):
                        user = fetch_one("""
                                SELECT
                                  id_user,
                                    CASE WHEN jabatan = 'Staff' THEN 'member'
                                    ELSE 'admin'
                                  END AS jabatan,
                                  name_user,
                                  email,
                                  password
                                FROM user
                                WHERE email = %s AND password = %s
                                  """, (email, password))
                        
                        if user:
                            cookie.set('is_login', True)
                            cookie.set('role', user['jabatan'])
                            cookie.set('id_user', user['id_user'])

                            st.session_state['is_login'] = True
                            st.session_state['role'] = user['jabatan']
                            st.session_state['id_user'] = user['id_user']
                            st.toast(f"Login Berhasil, Selamat Datang {user['name_user']}")
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error("❌ Email atau password salah. Silakan coba lagi.")

            st.caption("Dibuat Oleh Mahasiswa Statistika Universitas Negeri Medan © 2026.")
        st.info("ℹ️ Hubungi pihak Operator untuk mereset password atau mendaftar.")

@st.dialog("Apakah Anda yakin ingin keluar?")
def logout(): 
    col1, col2 = st.columns([1.8,9])
    with col1:
        if st.button("Batal", key="reject"):
            st.stop()

    with col2:
        if st.button("Ya, Keluar", type="primary", key='accept'):
            with st.spinner("Memproses Logout.."):
                st.session_state.clear()
                cookie.remove('is_login')
                cookie.remove('role')
                cookie.remove('id_user')

                time.sleep(3)
                st.rerun()

if not st.session_state.is_login:
    nav = st.navigation([st.Page(login_page, title="Login")])


else:
    role = st.session_state.get('role', None)
    if st.button("Logout", key='out'):
        logout()
    if role == "admin":
        nav = st.navigation([
            st.Page("admin/dashboard.py", title="Dashboard"),
            st.Page("admin/karyawan.py", title="Karyawan"),
            st.Page("admin/penilaian.py", title="Penilaian"),
        ])
    else:
        nav = st.navigation([
            st.Page("member/dashboard.py", title="Dashboard"),
            st.Page("member/projek.py", title="Projek"),
        ])

nav.run()
