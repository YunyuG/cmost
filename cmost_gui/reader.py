from pathlib import Path
import streamlit as st
import numpy as np
import pandas as pd
import cmost as cst
from dataclasses import dataclass
from astropy.io import fits
from utils import read_fits_all


session_state = st.session_state

if "spectrum" not in st.session_state:
    st.session_state["spectrum"] = None
if "header" not in st.session_state:
    st.session_state["header"] = None

@dataclass
class UserInputInfo:
    fits_dir_path:str = ""
    fits_paths:dict = None
    fits_path:str = ""

    minmax:bool = False
    minmax_range:tuple = ()
    remove_redshift:bool = False
    align:bool = False
    aligned_wavelength:np.ndarray = None

    fitting:bool = False
    max_workers:int = 6


def init_page():
    st.set_page_config(page_title="CMOST GUI"
                        ,page_icon=str(Path(__file__).parent/"assets/ico.png")
                        ,layout="centered",
                        initial_sidebar_state="auto"
                        )

def header():
    c1,c2 = st.columns([1.5,1])
    with c1:
        st.header("Reading and Basic Preprocessing of FITS Files"
                    ,divider="gray")

    with c2:
        st.image(str(Path(__file__).parent/"assets/reader.jpg")
            ,width=350)
    

def sidebar()->UserInputInfo:
    u = UserInputInfo()
    u.fits_dir_path = st.text_input("Enter the path of the directory containing FITS files:",value="")
    u.fits_paths = {str(i.name):str(i) for i in (Path(u.fits_dir_path).iterdir())}
    u.fits_path = st.selectbox("Select the FITS file to read:",options=u.fits_paths.keys())
    u.minmax = st.toggle("Normalize Flux",value=True) 
    u.minmax_range = st.slider("range",-10,10,(0,1),disabled=not u.minmax)
    u.remove_redshift = st.toggle("remove redshift",value=True)
    u.align = st.toggle("align",value=True)
    u.fitting = st.toggle("fitting",value=False)
    u.max_workers = st.number_input("max_workers",value=6)

    c1,c2,c3 = st.columns([1,1,1])
    with c1:
        start_point = st.number_input("Start point",value=3700,disabled=not u.align)
    with c2:
        end_point = st.number_input("End point",value=9100,disabled=not u.align)
    with c3:
        step = st.number_input("Step",value=2,disabled=not u.align)
    if u.align:
        u.aligned_wavelength = np.arange(start_point,end_point,step)
    return u

def content(u:UserInputInfo)->None:
    with st.sidebar:
        button1 = st.button("Submit")
        button2 = st.button("Submit all")
    if button1 or button2 or (session_state['spectrum'] is not None and session_state['header'] is not None):
        fits_data = cst.read_fits(
            u.fits_paths[u.fits_path]
        )
        if u.minmax:
            fits_data.minmax(u.minmax_range)
        if u.remove_redshift:
            fits_data.remove_redshift()
        if u.align:
            fits_data.align(u.aligned_wavelength)

        if u.fitting:
            model = cst.fitting.SwFitting5d(fits_data)
            flux_fitting = model(fits_data)
        
        col1,col2 = st.columns([1,1])
        col3,col4 = st.columns([1,1])
        with col1:
            st.metric(label="OBSID",value=fits_data["obsid"],border=True)
        with col2:
            st.metric(label="VERSION",value=fits_data["data_v"],border=True)
        with col3:
            st.metric(label="class",value=fits_data["class"],border=True)
        with col4:
            st.metric(label="subclass",value=fits_data["subclass"],border=True)
        
        data = pd.DataFrame(
            data={
                'Wavelength':fits_data.wavelength
                ,'Flux':fits_data.flux
            }
        )
        if u.fitting:
            data['Flux_fitting'] = flux_fitting
        tab1,tab2,tab3 = st.tabs(["📈 Chart","🗃 Data","🗃 header"])
        tab2.write(data)
        if u.fitting:
            tab1.line_chart(x='Wavelength',y=['Flux','Flux_fitting'],data=data)
        else:
            tab1.line_chart(x='Wavelength',y='Flux',data=data)
        tab3.write(pd.Series(fits_data.header,dtype=str))



    if button2:
        fits_paths = u.fits_paths
        result,headers = read_fits_all(fits_paths=fits_paths
                                ,minmax=u.minmax
                                ,minmax_range=u.minmax_range
                                ,remove_redshift=u.remove_redshift
                                ,align_wavelength=u.aligned_wavelength
                                ,fitting=u.fitting
                                ,max_workers=u.max_workers)
        
        session_state['spectrum'] = result.to_csv()
        session_state['header'] = headers.to_csv()
        

    col1,col2 = st.columns([1,1])
    if session_state['spectrum'] is not None and session_state['header'] is not None:
        st.success("Download the files below.")
        with col1:
            st.download_button(label="spectrum",data=session_state['spectrum'],file_name="spectrums.csv")
                
        with col2:
            st.download_button(label="header",data=session_state['header'],file_name="headers.csv")

    if not button1 and not button2:
        if not session_state['spectrum'] is not None and session_state['header'] is not None:
            st.info("Please submit the form to read the FITS file.")

def main()->None:
    init_page()
    header()
    with st.sidebar:
        u = sidebar()
    content(u)


if __name__ == "__main__":
    main()