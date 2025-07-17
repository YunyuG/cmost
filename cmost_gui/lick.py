from pathlib import Path
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cmost as cst
from dataclasses import dataclass
from utils import read_fits_single,lick_plot,compute_lick_indices,get_index_table,clean_cache,compute_lick_indices_all

clean_cache()

@dataclass
class UserInputInfo:
    fits_dir_path:str = ""
    fits_paths:dict = None
    fits_path:str = ""
    index:str = ""

class LickPage:
    def __init__(self):
        st.set_page_config(page_title="CMOST GUI"
                        ,page_icon=str(Path(__file__).parent/"assets/ico.png")
                        ,layout="centered",
                        initial_sidebar_state="auto"
                        )
        self.u = UserInputInfo()
        self.band()

    def header(self):
        c1,c2 = st.columns([1.5,1])
        with c1:
            st.header("Compute the Lick Index"
                    ,divider="gray")

        with c2:
            st.image(str(Path(__file__).parent/"assets/lick.jpg")
                    ,width=300)
    def band(self):
        self.header()
        with st.sidebar:
            self.sidebar()
        self.content()

    def sidebar(self):
        self.u.fits_dir_path = st.text_input("Enter the path of the directory containing FITS files:",value="")
        self.u.fits_paths = {str(i.name):str(i) for i in (Path(self.u.fits_dir_path).iterdir())}
        self.u.fits_path = st.selectbox("Select the FITS file to read:",options=self.u.fits_paths.keys())
        self.index_table = get_index_table()
        self.u.index = st.selectbox("Select the Lick Index to plot:",options=self.index_table.index)
        self.button1 = st.button("Compute Lick Index")
        self.button2 = st.button("Compute Lick Index for all FITS files in the directory")
    
    def content(self):

        if self.button1:
            fits_data = read_fits_single(
                self.u.fits_paths[self.u.fits_path],
                minmax=False,
                remove_redshift=False,
                align_wavelength=None
            )
            spectrum_data = pd.DataFrame(
                data={
                    "Wavelength":fits_data.wavelength,
                    "Flux":fits_data.flux,
                }
            )
            index = self.index_table.loc[self.u.index]
            fig,ax = plt.subplots()
            lick_plot(spectrum_data
                        ,index['blue_continuum_start']
                        ,index['blue_continuum_end']
                        ,index['red_continuum_start']
                        ,index['red_continuum_end']
                        ,index['index_band_start']
                        ,index['index_band_end']
                        ,ax)
            st.write("Lick Index Plot:")
            st.pyplot(fig)
            c1,c2 = st.columns([1,1])
            with c1:
                st.write("+ Lick line Index:")
                indices = compute_lick_indices(self.u.fits_paths[self.u.fits_path])
                st.write(indices)
            with c2:
                st.write("+ Index Table:")
                st.write(self.index_table)
            st.write("")
        if self.button2:
            lick_indices = compute_lick_indices_all(self.u.fits_paths)
            lc = lick_indices.to_csv()
            st.download_button(label="Download Lick Index Table",data=lc,file_name="lick_indices.csv",mime="text/csv")

              
if __name__ == "__main__":
    l = LickPage()
