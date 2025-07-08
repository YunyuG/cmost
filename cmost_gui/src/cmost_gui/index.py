import streamlit as st
from pathlib import Path
from utils import clean_cache

clean_cache()

st.set_page_config(page_title="CMOST GUI"
                   ,page_icon=str(Path(__file__).parent/"assets/ico.png")
                   ,layout="centered",
                   initial_sidebar_state="auto"
                   )
st.balloons()
c1,c2 = st.columns([3,1])
with c1:
    st.header("Welcome to CMOST GUI"
            ,width="stretch"
            ,divider="gray")
    st.subheader("version 0.0.1"
                ,width="stretch"
                ,divider="gray")
with c2:
    st.image(str(Path(__file__).parent/"assets/ico.png"),width=200)

st.write("""
This is originally a third-party Python library 
designed to assist astronomers and astronomy enthusiasts in 
processing LAMOST spectral data. However, considering that some 
of our users are novice researchers who may not be familiar with Python, 
we have provided a simple web page integrated with essential tools. 
This tool enables you to perform basic spectral processing tasks and data download tasks without writing code.
You only need to download the wheel package we provide and install it in your Python environment. 
We hope this tool can help you process LAMOST spectral data more easily, 
making your work more efficient and convenient. We also welcome you to raise any questions or suggestions during use, 
so that we can continuously improve this tool and provide you with better services.
Wish you a pleasant use!! :smile:\n
If you find our tool helpful
, we would appreciate it if you could star our project on GitHub.
 Thank you again for your support!:)\n
our GitHub repository: https://github.com/CMOST
         """)


