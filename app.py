import streamlit as st
from utils import fetch_one
import time

st.set_page_config(page_title="Aplikasi Penilaian", page_icon="logoBPS.png")

@st.cache_resource
def initialize_login():
    return {}

sid = st.context.headers["X-Streamlit-User"]
login = initialize_login()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if login.get(sid, {}).get("logged_in"):
    st.session_state.logged_in = True

def login_page():
    with st.container(border=True):
        st.title(":blue[SI]:green[PEND]:orange[EKAR]", text_alignment='center')
        st.markdown("<h5 style='text-align: center; color: #666; margin-top: 0;'>(Sistem Penilaian dan Evaluasi Karyawan)</h5>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([0.5, 2, 0.5])
        with col2:
            left, colImg, colText, right = st.columns([2, 1.8, 9, 2])
            colImg.image("logoBPS.png")
            colText.markdown("<p style='font-size: 20px; font-weight: 600;'>BPS Kabupaten Simalungun</p>", unsafe_allow_html=True)
            
            with st.form(key="login_form", border=True):
                email = st.text_input("Email", placeholder="email@bps.go.id")
                password = st.text_input("Password", type="password")

                if st.form_submit_button("Login", type="primary"):
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
                            login[sid] = {
                                    "logged_in": True,
                                    "user_id": user["id_user"],
                                    "role": user["jabatan"],
                                }
                            st.session_state.logged_in = True
                            
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Email atau password salah. Silakan coba lagi.")

            st.caption("Dibuat Oleh Mahasiswa Statistika Universitas Negeri Medan © 2026.")
        
        st.info("ℹ️ Hubungi pihak Operator untuk mereset password atau mendaftar.")

def logout():
    login.pop(sid, None)
    st.session_state.pop("sid", None)
    st.session_state.logged_in = False
    st.rerun()

role = login.get(sid, {}).get("role")
if role == "admin":
    menu = [
        st.Page("admin/dashboard.py", title="Dashboard"),
        st.Page("admin/karyawan.py", title="Karyawan"),
        st.Page("admin/penilaian.py", title="Penilaian"),
        st.Page(logout, title="Logout"),
    ]
elif role == "member":
    menu = [
        st.Page("member/dashboard.py", title="Dashboard"),
        st.Page("member/projek.py", title="Projek"),
        st.Page(logout, title="Logout"),
    ]

if not st.session_state.logged_in :
    nav = st.navigation([st.Page(login_page, title="Login")])
else:
    nav = st.navigation(menu)

nav.run()








