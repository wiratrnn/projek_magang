import streamlit as st
from utils import fetch_one

st.title(f"Hallo, {st.session_state.name} 👋")

nilai = fetch_one("""
        SELECT
            n.nilai,
            n.keterangan,
            a.aspek
        FROM nilai n
        JOIN aspek a
            ON n.id_aspek = a.id_aspek
        WHERE n.id_user = %s;
    """, (st.session_state.user_id,)
)

st.metric(
    label="Nilai Kinerja Saat Ini",
    value=f"{nilai['nilai']:.2f}"
)
st.divider()
st.write(f"**aspek** : {nilai['aspek']}")
st.markdown(f"**keterangan**: {nilai['keterangan']}")
st.divider()
