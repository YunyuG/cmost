import streamlit as st


pg = st.navigation([
    st.Page("index.py", title="welcome", icon="💻"),
    st.Page("download.py", title="download", icon="🚀"),
    st.Page("reader.py", title="read", icon="📖"),
    st.Page("lick.py", title="lick", icon="🛰"),
    ])

pg.run()