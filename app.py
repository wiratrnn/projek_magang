import streamlit as st
from utils import fetch_one
import time

# Inisialisasi session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None

def login_page():
    with st.container(border=True):
        
        st.markdown("<h1 style='text-align: center; color: #1877F2; margin-bottom: 0px;'>SiPendEKar</h1>", unsafe_allow_html=True)
        st.markdown("<h5 style='text-align: center; color: #666; margin-top: 0;'>(Sistem Penilaian dan Evaluasi Karyawan)</h5>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([0.5, 2, 0.5])
        with col2:
            img_col, text_col = st.columns([0.4, 1.6])
            with img_col:
                st.image("logoBPS.png", width=50)
            with text_col:
                st.markdown("<p style='margin: 0; padding-top: 5px; font-size: 18px; font-weight: bold; color: #1877F2;'>BPS Kabupaten Simalungun</p>", unsafe_allow_html=True)
            with st.container(border=True):
                email = st.text_input("Email", placeholder="email@bps.go.id")
                password = st.text_input("Password", type="password")

                if st.button("Login", type="primary"):
                    with st.spinner("Memproses login..."):
                        user = fetch_one("""
                                        SELECT 
                                            id_user, 
                                            CASE
                                                WHEN jabatan = 'Staff' THEN 'member'
                                                ELSE 'admin'
                                            END AS jabatan, 
                                            name_user, 
                                            email, 
                                            password 
                                        FROM user 
                                        WHERE email = %s AND password = %s
                                        """, (email, password))
                        if user:
                            st.success(f"Selamat datang, {user['name_user']}! 👋")
                            st.session_state['logged_in'] = True
                            st.session_state['user_id'] = user['id_user']
                            st.session_state['role'] = user['jabatan']
                            st.session_state['name'] = user['name_user']
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Email atau password salah. Silakan coba lagi.")

            st.caption("Dibuat Oleh Mahasiswa Statistika Universitas Negeri Medan © 2026.")
        
        st.info("ℹ️ Hubungi administrator untuk mereset password atau mendaftar.")

def logout():
    st.session_state.logged_in = False
    st.session_state.role = None
    st.session_state['user_id'] = None
    st.session_state['name'] = None
    st.rerun()

logout_page = st.Page(logout, title="Log out", icon=":material/logout:")

# tab untuk admin
admin_page_1 = st.Page("admin/dashboard.py", 
                       title="dashboard", 
                       icon=":material/handyman:")
admin_page_2 = st.Page("admin/karyawan.py", 
                       title="karyawan",
                       icon=":material/help:")
admin_page_3 = st.Page("admin/penilaian.py", 
                       title="penilaian",
                       icon=":material/help:")

# tab untuk member
member_page = st.Page("member/dashboard.py", 
                      title="dashboard_member",
                      icon=":material/security:")
member_page2 = st.Page("member/projek.py", 
                      title="projek_member",
                      icon=":material/handyman:")

role = st.session_state.get("role", None)
if role == "admin":
    nav = st.navigation([
        admin_page_1,
        admin_page_2,
        admin_page_3,
        logout_page
    ])
elif role == "member":
    nav = st.navigation([
        member_page,
        member_page2,
        logout_page
    ])
else:
    nav = st.navigation([
        st.Page(login_page, title="Login", icon=":material/login:")
    ])

nav.run()
