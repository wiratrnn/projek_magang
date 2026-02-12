import streamlit as st
import pandas as pd
import plotly.express as px
from utils import *

warna = px.colors.qualitative.G10

st.session_state.pop("target", None)

def short_name(full):
    part = str(full).split(",", 1)[0].strip()
    return " ".join(part.split()[:2])

def get_bar_data(periode):
    return fetch_all("""
        SELECT nilai
        FROM nilai_total
        WHERE id_periode = %s
        """, (periode,))

def get_top5_data(periode):
    return fetch_all("""
        SELECT 
            p.nama, 
            COALESCE(CAST(n.nilai AS CHAR), '-') AS nilai
        FROM pegawai p
        LEFT JOIN nilai_total n ON p.id_pegawai = n.id_pegawai AND n.id_periode = %s
        ORDER BY n.nilai DESC
        """, (periode,))

def get_line_data(tahun):
    return fetch_all("""
        SELECT 
            p.id_periode, p.tahun, p.bulan,
            ROUND(AVG(CASE WHEN t.id_jaspek = 1 THEN t.skor_pegawai END), 2) AS disiplin,
            ROUND(AVG(CASE WHEN t.id_jaspek = 2 THEN t.skor_pegawai END), 2) AS sikap_kerja,
            ROUND(AVG(CASE WHEN t.id_jaspek = 3 THEN t.skor_pegawai END), 2) AS hasil_kerja,
            (SELECT ROUND(AVG(nt.nilai), 2) 
            FROM nilai_total nt 
            WHERE nt.id_periode = p.id_periode) AS total

        FROM (
            SELECT n.id_periode, n.id_pegawai, n.id_jaspek,
                SUM(n.nilai * a.bobot) / SUM(a.bobot) AS skor_pegawai
            FROM nilai_aspek n
            JOIN aspek a USING (id_aspek)
            GROUP BY n.id_periode, n.id_pegawai, n.id_jaspek
        ) t
        JOIN periode p USING (id_periode)
        WHERE p.tahun = %s
        GROUP BY p.id_periode, p.tahun, p.bulan
        ORDER BY p.bulan ASC
        """,(tahun,))

def get_hbar_data(periode):
    return fetch_all("""
        SELECT a.nama_aspek, AVG(na.nilai) AS rata
        FROM nilai_aspek na
        JOIN aspek a ON a.id_aspek = na.id_aspek
        WHERE na.id_periode = %s
        GROUP BY a.id_aspek, a.nama_aspek
        ORDER BY rata
        """, (periode,))

def metric_data(id_periode):
    return fetch_one("""
        SELECT 
            AVG(nilai) AS avg_nilai, 
            MAX(nilai) AS max_nilai,
            MIN(nilai) AS min_nilai
        FROM nilai_total
        WHERE id_periode = %s
        """,(id_periode,))

st.title("📊 Dashboard")

jlh_pegawai = fetch_one("SELECT COUNT(*) AS jumlah FROM pegawai WHERE status = 1")['jumlah']

colBulan, colTahun = st.columns(2)
Y = colTahun.selectbox("tahun periode", options=[row["tahun"] for row in get_tahun()])
M = colBulan.selectbox("Periode Penilaian", range(1, 13),
                        format_func=lambda x: st.session_state.bulan[x-1])

periode_row = fetch_one("""
            SELECT id_periode
            FROM periode
            WHERE tahun=%s AND bulan=%s
            """, (Y, M))['id_periode']

if not is_periode(periode_row):
    st.warning(f"Belum ada data penilaian untuk periode {st.session_state.bulan[M-1]} {Y}.")
    st.stop()

stats = metric_data(periode_row)
col1, col2, col3, col4 = st.columns(4)
col1.metric_card("Pegawai Aktif", fn(jlh_pegawai), "👥", "#3366CC")
col2.metric_card("Rata-rata Nilai", fn(stats['avg_nilai']), "⭐", "#109618")
col3.metric_card("Nilai Tertinggi", fn(stats['max_nilai']), "🏆", "#FF9900")
col4.metric_card("Nilai Terendah", fn(stats['min_nilai']), "🔻", "#DC3912")

colBar, colTop = st.columns([8,4], gap='small', border=True)

@st.fragment
def bar_chart(periode):
    bar_df = get_bar_data(periode)
    
    BINS = [-float("inf"), 50, 60, 70, 80, 90, 100]
    LABELS = ["< 50", "51-60", "61-70", "71-80", "81-90", "91-100"]

    df = pd.DataFrame(bar_df)
    rekap_df = (
        pd.cut(df["nilai"], bins=BINS, labels=LABELS, include_lowest=True)
        .value_counts(sort=False)
        .rename_axis("range")
        .reset_index(name="jumlah")
    )

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
        xaxis_title=f'Kumulatif Nilai per {st.session_state.bulan[M-1]} {Y}',
        yaxis_title='jumlah karyawan',
        showlegend=False
    )

    colBar.subheader("Distribusi Nilai Karyawan")
    colBar.plotly_chart(fig)

bar_chart(periode_row)

@st.fragment
def TOP(periode):
    df2 = get_top5_data(periode)

    medals = [("🥇", "#D4AF37"), 
            ("🥈", "#C0C0C0"), 
            ("🥉", "#CD7F32"), 
            ("🏅", "#00CC96"), 
            ("🏅", "#00CC96")]

    with colTop.container(height=490, width=300, border=False):
        st.markdown("##### TOP bulanan")
        for i, data in enumerate(df2[:5]):
            icon, color = medals[i]
            metric_card(st,short_name(data['nama']), data['nilai'], f"{icon}", color)
    
        if st.session_state.role == 1:
            for i, data in enumerate(df2[5:], start=6):
                metric_card(st,short_name(data['nama']), data['nilai'], icon=f"•{i}" ,bg_color="#8b8b8b")

TOP(periode_row)

@st.fragment
def line(tahun):
    line_df = get_line_data(tahun)
    df3 = pd.DataFrame(line_df).set_index('id_periode')

    df3 = df3.apply(pd.to_numeric, errors="coerce")
    df3["periode"] = df3["tahun"].astype(str) + "-" + df3["bulan"].astype(str).str.zfill(2)

    fig = px.line(df3, 
                x='periode', 
                y = ["disiplin","sikap_kerja","hasil_kerja",'total'],
                color_discrete_sequence=warna)
    fig.update_xaxes(
        dtick="M1",
        tickformat="%b %Y",
        title=""
    )
    fig.update_yaxes(title="Nilai (%)")
    fig.update_layout(
        margin=dict(t=30),
        showlegend=True
    )
    with st.container(border=True):
        st.subheader(f"Tren Kinerja Karyawan per Aspek Utama tahun {tahun}")
        st.plotly_chart(fig, height=350)

line(Y)

colDetail, colHbar, = st.columns([4,6], gap='xxsmall', border=True)
@st.fragment
def hbar(periode):
    rows = get_hbar_data(periode)
    
    nama_aspek = [r["nama_aspek"] for r in rows]
    nilai = [float(r["rata"]) for r in rows]

    colHbar.markdown('#### **Performa Karyawan per Sub-Aspek**')
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
    
colDetail.header("Detail Penilaian Karyawan")

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


