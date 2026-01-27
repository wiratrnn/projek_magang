import streamlit as st
from utils import fetch_one

st.title(f"Hallo, {st.session_state.name} 👋")

nilai = fetch_one("""
    SELECT
        u.id_user,
        u.name_user,
        a.id_appraisal,
        a.periode,
        n.nilai,
        n.keterangan
    FROM user u
    JOIN appraisal a ON u.id_user = a.id_user
    JOIN nilai n ON a.id_appraisal = n.id_appraisal
    WHERE u.id_user = %s
    """, (st.session_state.user_id,)
)

st.metric(
    label="Nilai Kinerja Saat Ini",
    value=f"{nilai['nilai']:.2f}"
)

st.divider()