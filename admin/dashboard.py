import streamlit as st
import pandas as pd
import plotly.express as px
from utils import *

warna = px.colors.qualitative.G10
bulans = ["Januari","Februari","Maret","April","Mei","Juni",
         "Juli","Agustus","September","Oktober","November","Desember"]

st.session_state.pop("target", None)

def fn(x):
    return f"{x:.2f}".rstrip("0").rstrip(".")

@st.cache_data(ttl=300)
def get_bar_data(periode):
    return fetch_all("""
        SELECT nilai
        FROM nilai_total
        WHERE id_periode = %s
        """, (periode,))

@st.cache_data(ttl=300)
def get_top5(periode):
    return fetch_all("""
        SELECT p.nama, n.nilai
        FROM nilai_total n
        JOIN pegawai p ON p.id_pegawai = n.id_pegawai
        WHERE id_periode = %s
        GROUP BY p.id_pegawai, p.nama
        ORDER BY nilai DESC
        """,(periode,))

@st.cache_data(ttl=300)
def get_line_data():
    return fetch_all("""
        SELECT p.id_periode, p.tahun, p.bulan,
            AVG(CASE WHEN n.id_jaspek = 1 THEN n.nilai END) AS disiplin,
            AVG(CASE WHEN n.id_jaspek = 2 THEN n.nilai END) AS sikap_kerja,
            AVG(CASE WHEN n.id_jaspek = 3 THEN n.nilai END) AS hasil_kerja
        FROM nilai_aspek n
        JOIN periode p ON p.id_periode = n.id_periode
        GROUP BY p.id_periode, p.tahun, p.bulan
        ORDER BY p.tahun, p.bulan
        """)

@st.cache_data(ttl=300)
def get_hbar_data(periode):
    return fetch_all("""
        SELECT a.nama_aspek, AVG(na.nilai) AS rata
        FROM nilai_aspek na
        JOIN aspek a ON a.id_aspek = na.id_aspek
        WHERE na.id_periode = %s
        GROUP BY a.id_aspek, a.nama_aspek
        ORDER BY rata
        """, (periode,))

@st.cache_data(ttl=300)
def periode_punya_nilai(id_periode):
    row = fetch_one("""
        SELECT COUNT(*) AS jumlah
        FROM nilai_aspek
        WHERE id_periode = %s
        """, (id_periode,))
    return row["jumlah"] > 0


st.title("📊 Dashboard")
jlh_pegawai = fetch_all("SELECT COUNT(*) AS jumlah FROM pegawai WHERE status = 1")
stats = fetch_all("""
        SELECT 
            AVG(nilai) AS avg_nilai, 
            MAX(nilai) AS max_nilai,
            MIN(nilai) AS min_nilai
        FROM nilai_aspek """)


colTahun, colBulan = st.columns(2)
Y = colTahun.selectbox("tahun periode", options=[2022, 2023, 2024, 2025, 
                                                2026, 2027, 2028, 2029])
M = colBulan.selectbox("Periode Penilaian", range(1, 13),
                        format_func=lambda x: bulans[x-1])

col1, col2, col3, col4 = st.columns(4)
col1.metric_card("Pegawai Aktif", fn(jlh_pegawai[0]['jumlah']), "👥", "#3366CC")
col2.metric_card("Rata-rata Nilai", fn(stats[0]['avg_nilai']), "⭐", "#109618")
col3.metric_card("Nilai Tertinggi", fn(stats[0]['max_nilai']), "🏆", "#FF9900")
col4.metric_card("Nilai Terendah", fn(stats[0]['min_nilai']), "🔻", "#DC3912")

periode_row = fetch_one("""
            SELECT id_periode
            FROM periode
            WHERE tahun=%s AND bulan=%s
            """, (Y, M))['id_periode']

if not periode_punya_nilai(periode_row):
    st.warning(f"Belum ada data penilaian untuk periode {bulans[M-1]} {Y}.")
    st.stop()

colBar, colTop = st.columns([8,4], gap='small', border=True)

@st.fragment
def bar_chart(periode):
    bar_df = get_bar_data(periode)
    
    df = pd.DataFrame(bar_df, columns=["nilai"])
    labels = ["0-50", "50-60", "61-70", "71-80", "81-90", "91-100"]
    bins = [0, 50, 60, 70, 80, 90, 100]
    df["range"] = pd.cut(df["nilai"], bins=bins, labels=labels)

    rekap_df = (
        df["range"]
        .value_counts()
        .reindex(labels, fill_value=0)
        .reset_index()
    )
    rekap_df.columns = ["range", "jumlah"]

    fig = px.bar(
        rekap_df,
        x="range",
        y="jumlah",
        color='range',
        color_discrete_sequence=warna
    )

    fig.update_traces(offsetgroup=0)
    fig.update_layout(
        margin=dict(t=10),
        barmode='overlay',
        xaxis_title=f'Kumulatif Nilai per {bulans[M-1]} {Y}',
        yaxis_title='jumlah pegawai',
        showlegend=False
    )

    colBar.subheader("Distribusi Nilai Pegawai")
    colBar.plotly_chart(fig)

bar_chart(periode_row)

@st.fragment
def TOP(periode):
    df2 = get_top5(periode)

    medals = [("🥇", "#D4AF37"), 
            ("🥈", "#C0C0C0"), 
            ("🥉", "#CD7F32"), 
            ("🏅", "#00CC96"), 
            ("🏅", "#00CC96")]

    with colTop.container(height=490, width=300, border=False):
        st.markdown("##### TOP bulanan")
        for i, data in enumerate(df2[:5]):
            icon, color = medals[i]
            metric_card(st,f"{data['nama']}", fn(data['nilai']), f"{icon}", color)
    
        if st.session_state.role == 1:
            for i, data in enumerate(df2[5:], start=6):
                metric_card(st,f"{data['nama']}", fn(data['nilai']), icon=f"•{i}" ,bg_color="#8b8b8b")

TOP(periode_row)

@st.fragment
def line():
    line_df = get_line_data()
    df3 = pd.DataFrame(line_df, 
                    columns=["id_periode", "tahun", "bulan",
                              "disiplin", "sikap_kerja", "hasil_kerja",
                            ]).set_index('id_periode')

    df3["overall"] = df3[["disiplin", "sikap_kerja", "hasil_kerja"]].mean(axis=1)
    df3 = df3.apply(pd.to_numeric, errors="coerce")
    df3["periode"] = df3["tahun"].astype(str) + "-" + df3["bulan"].astype(str).str.zfill(2)

    fig = px.line(df3, 
                x='periode', 
                y = ["disiplin","sikap_kerja","hasil_kerja",'overall'],
                color_discrete_sequence=warna)
    fig.update_xaxes(
        dtick="M1",
        tickformat="%b %Y",
        title=""
    )
    fig.update_yaxes(title="Nilai")
    fig.update_layout(
        margin=dict(t=30),
        showlegend=True
    )
    with st.container(border=True):
        st.subheader("Tren Kinerja Pegawai")
        st.plotly_chart(fig, height=350)

line()

colDetail, colHbar, = st.columns([4,6], gap='xxsmall', border=True)
@st.fragment
def hbar(periode):
    rows = get_hbar_data(periode)
    
    nama_aspek = [r["nama_aspek"] for r in rows]
    nilai = [float(r["rata"]) for r in rows]

    colHbar.markdown('#### **Performa Pegawai per Sub-aspek**')
    fig = px.bar(
        x=nilai,
        y=nama_aspek,
        orientation="h",
        color=nama_aspek,
        color_discrete_sequence=warna,
        text=nama_aspek
    )

    fig.update_traces(offsetgroup=0,
                      width=1,
                      textposition="inside")
    fig.update_yaxes(visible=False)
    fig.update_layout(
        margin=dict(t=30, l=0, r=0, b=30),
        barmode='overlay',
        xaxis_title="Rata-rata Nilai",
        yaxis_title="",
        showlegend=False
    )
    fig.update_xaxes(range=[50, 100])
    colHbar.plotly_chart(fig, height=300)

hbar(periode_row)

def t_jaspek(judul):
    st.markdown(
            f"""
            <div style="text-align: left; margin-bottom:1rem;">
                <span style="
                    background-color: #008f58;
                    color: #f3f3f3;
                    font-weight: 700;
                    padding: 6px 14px;
                    border-radius: 8px;
                    font-size: 18px;
                ">
                    {judul}
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )
    
colDetail.header("Detail Penilaian Pegawai")

with colDetail.expander("Disiplin [30%]"):
    aspek = fetch_all("SELECT * FROM aspek WHERE id_jaspek = 1")
    col1, col2 = st.columns([5, 2])

    for disiplin in aspek:
        with st.container():
            col1, col2 = st.columns([5, 2])

            with col1:
                t_jaspek(disiplin['nama_aspek'])

            with col2:
                st.markdown(
                    f"""
                    <div style="
                        text-align:center;
                        padding:2px;
                        border-radius:8px;
                        font-weight:600;
                        border:1px solid #ddd;">
                        {fn(disiplin['bobot'])}%
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.caption(disiplin["detail_aspek"])

with colDetail.expander("Sikap Kerja [30%]"):
    aspek = fetch_all("SELECT * FROM aspek WHERE id_jaspek = 2")
    col1, col2 = st.columns([5, 2])

    for disiplin in aspek:
        with st.container():
            col1, col2 = st.columns([5, 2])

            with col1:
                t_jaspek(disiplin['nama_aspek'])

            with col2:
                st.markdown(
                    f"""
                    <div style="
                        text-align:center;
                        padding:2px;
                        border-radius:8px;
                        font-weight:600;
                        border:1px solid #ddd;">
                        {fn(disiplin['bobot'])}%
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.caption(disiplin["detail_aspek"])

with colDetail.expander("Hasil Kerja [40%]"):
    aspek = fetch_all("SELECT * FROM aspek WHERE id_jaspek = 3")
    col1, col2 = st.columns([5, 2])

    for disiplin in aspek:
        with st.container():
            col1, col2 = st.columns([5, 2])

            with col1:
                t_jaspek(disiplin['nama_aspek'])

            with col2:
                st.markdown(
                    f"""
                    <div style="
                        text-align:center;
                        padding:2px;
                        border-radius:8px;
                        font-weight:600;
                        border:1px solid #ddd;">
                        {fn(disiplin['bobot'])}%
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.caption(disiplin["detail_aspek"])

