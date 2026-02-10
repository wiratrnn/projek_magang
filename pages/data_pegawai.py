import streamlit as st
import pandas as pd
import plotly.express as px
from utils import fetch_all

def fn(x):
    return f"{x:.2f}".rstrip("0").rstrip(".")

@st.cache_data(ttl=300)
def get_detail():
    return fetch_all("""
        SELECT 
            na.*,
            a.nama_aspek,
            j.judul_aspek,
            p.bulan,
            p.tahun,
            nt.nilai AS total
        FROM nilai_aspek na
        JOIN nilai_total nt 
            ON nt.id_pegawai = na.id_pegawai
            AND nt.id_periode = na.id_periode
        JOIN aspek a
            ON a.id_aspek = na.id_aspek
        JOIN jaspek j
            ON j.id_jaspek = na.id_jaspek
        JOIN periode p
            ON p.id_periode = na.id_periode
        WHERE na.id_pegawai = %s
        """, (st.session_state.id_pegawai_detail,))

@st.cache_data(ttl=300)
def get_jaspek():
    return fetch_all("""
        SELECT 
            na.id_periode,
            p.bulan,
            p.tahun,
            na.id_jaspek,
            j.judul_aspek,
            ROUND(
                (SUM(na.nilai * a.bobot) / 100) 
                / COUNT(DISTINCT na.id_penilai), 
            2) AS hasil
        FROM nilai_aspek na
        JOIN aspek a ON a.id_aspek = na.id_aspek
        JOIN periode p ON p.id_periode = na.id_periode
        JOIN jaspek j ON j.id_jaspek = na.id_jaspek
        WHERE na.id_pegawai = %s
        GROUP BY 
            na.id_periode, p.bulan, p.tahun,
            na.id_jaspek, j.judul_aspek
        ORDER BY p.tahun, p.bulan
        """, (st.session_state.id_pegawai_detail,))

jaspek_df = pd.DataFrame(get_jaspek())
data_df = pd.DataFrame(get_detail())

col1, col2, col3 = st.columns([1, 3, 3])
with col1:
    st.space()
    if st.session_state.jenis_kelamin_detail == 1:
        st.image("images/maleprofil.png", width=90)
    else :
        st.image("images/femaleprofil.png", width=90)

with col2:
    st.subheader(st.session_state.nama_detail)
    st.caption(f"NIP: {st.session_state.nip_detail}")
    st.caption(f"{st.session_state.email_detail}")
    st.caption(f"{st.session_state.jabatan_detail} • {st.session_state.unit_kerja_detail}")

total_per_periode = (data_df[["id_periode", "total"]].drop_duplicates().sort_values("id_periode"))
delta_total = total_per_periode.iloc[-1]['total'] - total_per_periode.iloc[-2]['total']
col3.metric("Nilai Total", 
          total_per_periode.iloc[-1]['total'], 
          delta=delta_total, 
          border=True)
opsi = (
    data_df[["id_periode", "bulan", "tahun"]]
    .drop_duplicates()
    .sort_values("id_periode")
    .sort_index(ascending=True)
)

periode = st.selectbox(
    "Pilih periode",
    opsi,
    format_func=lambda x: f"{opsi.set_index('id_periode').loc[x, 'bulan']}/"
                          f"{opsi.set_index('id_periode').loc[x, 'tahun']}"
)

def hitung_delta(df, periode):
    now = df[df["id_periode"] == periode]
    prev = df[df["id_periode"] == periode - 1]

    if not now.empty and not prev.empty:
        return now.iloc[0]["hasil"] - prev.iloc[0]["hasil"]
    return None

def get_nilai(df, periode):
    now = df[df["id_periode"] == periode]
    if not now.empty:
        return now.iloc[0]["hasil"]
    return 0

disiplin_per_periode = jaspek_df[jaspek_df["id_jaspek"] == 1][["id_periode", "hasil"]]
sikap_per_periode    = jaspek_df[jaspek_df["id_jaspek"] == 2][["id_periode", "hasil"]]
kerja_per_periode    = jaspek_df[jaspek_df["id_jaspek"] == 3][["id_periode", "hasil"]]

delta_disiplin = hitung_delta(disiplin_per_periode, periode)
delta_sikap    = hitung_delta(sikap_per_periode, periode)
delta_kerja    = hitung_delta(kerja_per_periode, periode)

c1, c2, c3 = st.columns(3, gap='xxsmall')
c1.metric(
    "Disiplin [0 - 30]",
    get_nilai(disiplin_per_periode, periode),
    delta_disiplin,
    chart_data=disiplin_per_periode['hasil'],
    chart_type='line',
    border=True)
   
c2.metric("Hasil Kerja [0 - 40]",
    get_nilai(kerja_per_periode, periode),
    delta_kerja,
    chart_data=kerja_per_periode['hasil'],
    chart_type='line',
    border=True)

c3.metric("Sikap Kerja [0 - 30]",
    get_nilai(sikap_per_periode, periode),
    delta_sikap,
    chart_data=sikap_per_periode['hasil'],
    chart_type='line',
    border=True)

jaspek_df["periode"] = jaspek_df["bulan"].astype(str) + "/" + jaspek_df["tahun"].astype(str)
jaspek_df["hasil"] = pd.to_numeric(jaspek_df["hasil"], errors="coerce")

colBar, colRadar = st.columns([5,5], border=True, gap='xxsmall')
colBar.header("Performa Pegawai per Aspek Utama")
colBar.bar_chart(jaspek_df, x="periode", y="hasil", color="judul_aspek", 
                horizontal=True, width=300)

urutan = ["Kepatuhan", "Ketepatan", "Inisiatif",
          "Kolaboratif","Akuntabilitas","Kuantitas",
           "Kualitas","Kerapihan"]

map_periode = (
    data_df[["id_periode", "bulan", "tahun"]]
    .drop_duplicates()
    .set_index("id_periode")
)

radar_fix = (
    data_df[data_df["id_periode"].isin([periode-1, periode])]
    .groupby(["id_periode", "nama_aspek"], as_index=False)["nilai"]
    .mean()
    .pivot(index="nama_aspek", columns="id_periode", values="nilai")
    .reindex(urutan)
    .fillna(0)
    .infer_objects(copy=False)
    .reset_index()
    .melt(id_vars="nama_aspek", var_name="periode", value_name="nilai")
)

# ubah angka → bulan/tahun
radar_fix["periode"] = radar_fix["periode"].apply(
    lambda x: f"{map_periode.loc[x, 'bulan']}/{map_periode.loc[x, 'tahun']}"
)

fig = px.line_polar(
    radar_fix,
    r="nilai",
    theta="nama_aspek",
    color="periode",
    line_close=True,
    color_discrete_sequence=["#3366CC", "#FF9900"]
)

fig.update_traces(fill="toself", mode="lines+markers")

fig.update_layout(
    polar=dict(
        domain=dict(x=[0.3, 1], y=[0.3, 0.8]),
        angularaxis=dict(categoryorder="array", categoryarray=urutan)
    ),
    margin=dict(t=0, b=0, l=0, r=0)
)

colRadar.header("Performa Pegawai per Sub Aspek")
colRadar.plotly_chart(fig, height=300)

data_df["periode"] = (data_df["bulan"].astype(str) + "/" + data_df["tahun"].astype(str))

tabel = (
    data_df[["periode"]].drop_duplicates().assign(key=1)
    .merge(
        data_df[["judul_aspek", "nama_aspek"]].drop_duplicates().assign(key=1),
        on="key"
    )
    .drop("key", axis=1)
    .merge(
        data_df
        .groupby(["periode", "judul_aspek", "nama_aspek"], as_index=False)["nilai"]
        .mean(),
        how="left"
    )
    .pivot(
        index="periode",
        columns=["judul_aspek", "nama_aspek"],
        values="nilai"
    )
    .join(
        data_df
        .groupby("periode")["total"]
        .first()
        .rename(("Total", "Total"))
    )
    .reset_index()
    .fillna(0)
    .infer_objects(copy=False)
)

st.header("Tabel Rekap Penilaian")
num_cols = tabel.select_dtypes(include="number").columns
st.dataframe(tabel.style.highlight_max(axis=1,subset= num_cols)
                        .format(fn, subset=num_cols),

            width='stretch', hide_index=True)
