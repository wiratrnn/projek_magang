from streamlit_cookies_controller import CookieController
from utils import fetch_one, hash
import streamlit as st
import time
import base64

@st.cache_data
def get_images():
    with open("images/maleprofil.png", "rb") as f:
        male = base64.b64encode(f.read()).decode()
        
    with open("images/femaleprofil.png", "rb") as f:
        female = base64.b64encode(f.read()).decode()
    
    with open("images/logobps.png", "rb") as f:
        bps = base64.b64encode(f.read()).decode()

    with open("images/logopendekar.png", "rb") as f:
        logo = base64.b64encode(f.read()).decode()
    
    return male, female, bps, logo

male, female, bps, logo = get_images()
cookie = CookieController()

st.html("""
        <style>
        .st-key-my_blue_container {
            background-color: rgb(145, 250, 210);
        }

        .st-key-login_container {
            background-color: white;
            padding: 20px;
            border-radius: 5px;
        }
        </style>
        """)
st.set_page_config(page_title="SiPENDEKAR", page_icon="images/logopendekar.png")

@st.fragment
def login_page():
    with st.container(key='my_blue_container', border=True, gap='xxsmall'):
        st.space('small')
        col_info, col_login = st.columns(2)
        with col_info:
            st.markdown("### *Selamat Datang*👋😄", text_alignment='center')
            st.markdown(
                f"""
                <div style="
                    display:flex;
                    flex-direction:column;
                    align-items:center;
                    justify-content:center;
                ">
                    <img src="data:image/png;base64,{logo}"
                        width="100"
                        style="margin-left:-30px;">
                    <h1 style="
                        margin-left:18px;
                        font-weight:bold;
                        letter-spacing:0;
                        line-height:0;
                        white-space:nowrap;
                    ">
                        <span style="color:#2563eb">Si</span><span style="color:#16a34a">PEND</span><span style="color:#f97316">EKAR</span>
                    </h1>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown("<h6 style='text-align: center; color: black;'>(Sistem Penilaian dan Evaluasi Karyawan)</h6>", unsafe_allow_html=True)
            st.markdown(
                f"""
                <div style="
                    display:flex;
                    justify-content:center;
                    gap:8px;
                ">
                    <img src="data:image/png;base64,{bps}" width="30">
                    <span style="
                        margin:0;
                        font-weight:bold;
                        font-size:18;
                    ">
                        BPS Kabupaten Simalungun
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.space('xxsmall')
        with col_login:
            with st.container(key="login_container", gap='xxsmall'):
                with st.form(key="login", border=False):
                    st.write("#### :material/account_circle: username")
                    uname = st.text_input("l", label_visibility='collapsed')
                    st.write("#### :material/lock: password")
                    password = st.text_input("p", type="password", label_visibility='collapsed')

                    if st.form_submit_button("Login", type="primary"):
                        with st.spinner("Memproses login..."):
                            user = fetch_one("""
                                        SELECT
                                            u.id_user,
                                            u.password,
                                            u.penilai AS role,
                                            p.nama,
                                            p.unit_kerja,
                                            p.jabatan,
                                            p.jenis_kelamin
                                        FROM users u
                                        JOIN pegawai p ON u.id_pegawai = p.id_pegawai
                                        WHERE u.username = %s AND u.password = %s
                                    """, (uname, password))

                            if user:
                                cookie.set('role', user['role'])
                                cookie.set('id_user', user['id_user'])
                                cookie.set('key', hash(user['password']))

                                st.session_state['key'] = hash(user['password'])
                                user.pop('password', None)
                                st.session_state.update(user)
                                st.toast(f"Login Berhasil, Selamat Datang {user['nama']}")
                                time.sleep(2)

                                st.rerun()
                            else:
                                st.error("❌ Email atau password salah. Silakan coba lagi.")

                    st.caption("Dibuat Oleh Mahasiswa Statistika Universitas Negeri Medan © 2026.", text_alignment='center')
        st.info("ℹ️ Hubungi pihak Operator untuk mereset password atau mendaftar.")

@st.dialog("Apakah Anda yakin ingin keluar?")
def logout():
    logout_area = st.empty()
    with logout_area.container():
        col1, col2 = st.columns([1.8, 9])
        if col1.button("Batal", key="reject"):
            st.switch_page("admin/dashboard.py")
        confirm_logout = col2.button("Ya, Keluar", type="primary", key='accept')

    if confirm_logout:
        logout_area.empty() 
        with st.spinner("Sedang Memproses..."):
            st.session_state.clear()
            cookie.remove('role')
            cookie.remove('id_user')
            cookie.remove('key')
            time.sleep(3)
            st.switch_page(st.Page(login_page))

if not (st.session_state.get('id_user') or st.session_state.get('key')):
    st.session_state.role = cookie.get("role")
    st.session_state.id_user = cookie.get("id_user")
    st.session_state.key = cookie.get('key')
    time.sleep(2)

    if cookie.get("key") and cookie.get('id_user'):
        key = fetch_one("SELECT password FROM users WHERE id_user = %s",(cookie.get("id_user"),))['password']
        st.session_state.key = hash(key) if key is not None else None
        if st.session_state.key is not None and str(st.session_state.key) == str(cookie.get("key")):
            user = fetch_one("""
                            SELECT
                                p.nama,
                                p.unit_kerja,
                                p.jabatan,
                                p.jenis_kelamin
                            FROM users u
                            JOIN pegawai p ON u.id_pegawai = p.id_pegawai
                            WHERE p.id_pegawai = %s AND u.password = %s
                        """, (cookie.get('id_user'), key))
            
            st.session_state.update(user)
            st.rerun()

if (not st.session_state.id_user
    or not cookie.get("id_user")
    or not st.session_state.key
    or not cookie.get("key")
    or st.session_state.id_user != cookie.get("id_user")
    or st.session_state.key != cookie.get("key")):
    st.markdown("""
        <style>
        section[data-testid="stSidebar"] {
            display: none;
        }
        </style>
        """, unsafe_allow_html=True)
    nav = st.navigation([st.Page(login_page)])

else:
    role = st.session_state.get('role', None)
    gender = st.session_state.get('jenis_kelamin')
    with st.sidebar:
        st.markdown(
            f"""
            <div style="text-align:center; padding:12px 0;">
                <img src="data:image/png;base64,{male if gender == 1 else female}"
                    style="border-radius:50%;
                            width:80px;
                            height:80px;">
                <div style="margin-top:8px; font-weight:600;">{st.session_state.get('nama',None)} | {st.session_state.get('unit_kerja',None)}</div>
                <div style="font-size:12px; opacity:0.6;">{st.session_state.get('jabatan')}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.button("Logout", type='primary', on_click=logout)
        st.divider()
        if role == 1 :
            st.page_link(st.Page("admin/dashboard.py"), icon='📊')
            st.page_link(st.Page("admin/penilaian.py"), icon=":material/person_add:")
        else :
            st.page_link(st.Page("admin/dashboard.py"), icon='📊')

    
    if role == 1:
        nav = st.navigation([st.Page("admin/dashboard.py", default=True),
                            st.Page("admin/penilaian.py")], 
                            position='hidden')

    else:
        nav = st.navigation([st.Page("admin/dashboard.py")], 
                            position='hidden')

nav.run()
