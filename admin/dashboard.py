import streamlit as st
import pandas as pd
from utils import fetch_all

st.session_state.pop("penilaian", None)

st.title("📊 Dashboard Manajer")
jaspek = fetch_all("SELECT * FROM jaspek")
jlh_karyawan = fetch_all("SELECT COUNT(*) AS jumlah FROM user WHERE status = 'aktif'")
nilai_stats = fetch_all(
    """
    SELECT 
        AVG(nilai) AS avg_nilai, 
        MAX(nilai) AS max_nilai,
        MIN(nilai) AS min_nilai
    FROM appraisal
    WHERE tahun_periode = 2025
    """
)

def metric_card(title, value, icon, bg_color):
    st.markdown(
        f"""
        <div style="
            background-color:{bg_color};
            padding:10px;
            border-radius:12px;
            color:white;
            height:110px;
            display:flex;
            align-items:center;
            justify-content:flex-start;
        ">
            <div style="font-size:48px; opacity:0.8;">
                {icon}
            </div>
            <div style="display:flex; flex-direction:column; align-items:flex-end; justify-content:space-between; height:110px; width:100%;">
                <div style="font-size:19px;">{title}</div>
                <div style="font-size:34px; font-weight:bold; align-self:flex-start;">{value}</div>
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

col1, col2, col3, col4 = st.columns(4)

with col1:
    metric_card(
        "Pegawai Aktif",
        jlh_karyawan[0]['jumlah'],
        "👥",
        "#3B82F6"   # biru
    )

with col2:
    metric_card(
        "Rata-rata Nilai",
        f"{nilai_stats[0]['avg_nilai']:.2f}",
        "⭐",
        "#0F9266"   # hijau
    )

with col3:
    metric_card(
        "Nilai Tertinggi",
        nilai_stats[0]['max_nilai'],
        "🏆",
        "#F59E0B"   # kuning
    )

with col4:
    metric_card(
        "Nilai Terendah",
        nilai_stats[0]['min_nilai'],
        "🔻",
        "#EF4444"   # merah
    )



st.markdown(
    """
    <h1 style="
        text-align: center;
        color: #1877F2;
        font-weight: 800;
        margin-bottom: 2rem;
    ">
        Detail Aspek Penilaian
    </h1>
    """,
    unsafe_allow_html=True
)

for item in jaspek:
    with st.container(border=True):
        st.markdown(
            f"""
            <div style="text-align: left; margin-bottom:1rem;">
                <span style="
                    background-color: #e8f0ff;
                    color: #1877F2;
                    font-weight: 700;
                    padding: 6px 14px;
                    border-radius: 8px;
                    font-size: 2.25rem;
                ">
                    {item['judul_aspek']}
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

        aspek = fetch_all(
            "SELECT * FROM aspek WHERE id_jaspek = %s", (item['id_jaspek'],)
        )
        st.data_editor(pd.DataFrame(aspek, columns=["aspek", "detail_aspek", "bobot"]),
                    width='stretch',
                    hide_index=True,
                    disabled=["aspek", "detail_aspek"],   # hanya bobot yang editable
                    column_config={
                        "aspek": st.column_config.TextColumn(
                            "Aspek", width="medium"
                        ),
                        "detail_aspek": st.column_config.TextColumn(
                            "Detail Aspek",
                            width="large"
                        ),
                        "bobot": st.column_config.NumberColumn(
                            "Bobot",
                            min_value=0,
                            max_value=100,
                            step=1,
                            format="%d",
                            width="small"
                        )})




