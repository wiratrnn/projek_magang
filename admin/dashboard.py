import streamlit as st
import pandas as pd
from utils import fetch_all

st.title("📊 Dashboard Manajer")
jaspek = fetch_all("SELECT * FROM jaspek")

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
                    use_container_width=True,
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

