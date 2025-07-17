import cmost as cst
import numpy as np
import pandas as pd
from pathlib import Path
from functools import cache
from concurrent.futures import ProcessPoolExecutor, as_completed
import streamlit as st

def read_fits_single(fits_path:str
                     ,minmax:bool=True
                     ,minmax_range:tuple=()
                     ,remove_redshift:bool=True
                     ,align_wavelength:np.ndarray=None
                     ,fitting:bool=False)->pd.Series:
    
    fits_data = cst.read_fits(fits_path)
    if minmax:
        fits_data.minmax(minmax_range)
    if remove_redshift:
        fits_data.remove_redshift()
    if align_wavelength is not None:
        fits_data.align(aligned_wavelength=align_wavelength)
    if fitting:
        model = cst.fitting.SwFitting5d(fits_data=fits_data)
        # model.fit(fits_data)
        fits_data.flux = model(fits_data)
        # print(fits_data.flux)
    return fits_data


def read_fits_all(fits_paths:dict
                ,**kwargs)->pd.Series:
    max_workers = kwargs.pop("max_workers",6)
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        tasks = {executor.submit(read_fits_single,fits_paths[f],**kwargs):f for f in fits_paths}
        headers = []
        result = []
        names = []
        with st.spinner("Processing ..."):
            step = 0
            bar = st.progress(0)
            text = st.text("")
            for future in as_completed(tasks):
                try:
                    fits_name = tasks[future]
                    fits_data = future.result()
                    spectrum_data = pd.Series(fits_data.flux,index=fits_data.wavelength)
                    header = pd.Series(fits_data.header,dtype=str)
                    # 
                    bar.progress(int((step+1)/len(tasks)*100))
                    result.append(spectrum_data)
                    headers.append(header)
                    names.append(fits_name)
                    text.text(f"{fits_name} processed")
                    step += 1
                except Exception as e:
                    st.error(f"Error processing  {e}")
        result = pd.concat(result,axis=1).T
        headers = pd.concat(headers,axis=1).T
        result.index = names
    return result,headers

@cache
def get_index_table()->pd.DataFrame:
    index_path = Path(__file__).parent / Path("assets") / "index.table"
    index_table = pd.read_csv(index_path,skiprows=1,sep=" ",header=None)
    index_table.dropna(inplace=True,axis=1,how='any')
    col_name = ['No.','index_band_start'
                ,'index_band_end'
                ,'blue_continuum_start'
                ,'blue_continuum_end'
                ,'red_continuum_start'
                ,'red_continuum_end'
                ,'Units'
                ,'name']
    index_table.columns = col_name
    index_table.drop("No.",axis=1,inplace=True)
    index_table.set_index("name",inplace=True,drop=True)
    return index_table

def compute_lick_indices(fits_path:str)->pd.Series:
    fits_data = cst.read_fits(fits_path)
    lick_indices = cst.lick.compute_LickLineIndices(fits_data)
    return pd.Series(lick_indices)

def compute_lick_indices_all(fits_paths:dict)->pd.DataFrame:
    with ProcessPoolExecutor(max_workers=6) as executor:
        tasks = {executor.submit(compute_lick_indices,fits_paths[f]):f for f in fits_paths}
        lick_indices = []
        names = []
        with st.spinner("Processing ..."):
            step = 0
            bar = st.progress(0)
            text = st.text("")
            for future in as_completed(tasks):
                try:
                    fits_name = tasks[future]
                    lick_index = future.result()
                    lick_indices.append(lick_index)
                    names.append(fits_name)
                    bar.progress(int((step+1)/len(tasks)*100))
                    text.text(f"{fits_name} processed")
                    step += 1
                except Exception as e:
                    st.error(f"Error processing  {e}")
        lick_indices = pd.concat(lick_indices,axis=1).T
        lick_indices.index = names
    return lick_indices

def clean_cache():

    if "spectrum" in st.session_state:
        st.session_state.pop("spectrum")
    if "header"  in st.session_state:
        st.session_state.pop("header")


def lick_plot(spectral_data: pd.Series,
              blue_continuum_start, blue_continuum_end,
              red_continuum_start, red_continuum_end,
              index_band_start, index_band_end,
              ax=None):

    wavelength_FI_lamda, flux_FI_lamda = cst.lick.extract_one_spectrum(
        spectral_data['Wavelength'],
        spectral_data['Flux'],
        index_band_start, index_band_end
    )
    x_FI, y_FI = wavelength_FI_lamda, flux_FI_lamda


    wavelength_blue, flux_blue = cst.lick.extract_one_spectrum(
        spectral_data['Wavelength'],
        spectral_data['Flux'],
        blue_continuum_start, blue_continuum_end
    )
    blue_avg = cst.lick.compute_mean_flux(wavelength_blue, flux_blue)
    x_blue = [blue_continuum_start, blue_continuum_end]
    y_blue = [blue_avg, blue_avg]


    wavelength_red, flux_red = cst.lick.extract_one_spectrum(
        spectral_data['Wavelength'],
        spectral_data['Flux'],
        red_continuum_start, red_continuum_end
    )
    red_avg = cst.lick.compute_mean_flux(wavelength_red, flux_red)
    x_red = [red_continuum_start, red_continuum_end]
    y_red = [red_avg, red_avg]


    x_FC = [
        (blue_continuum_start + blue_continuum_end) / 2,
        (red_continuum_start + red_continuum_end) / 2
    ]
    y_FC = [blue_avg, red_avg]


    y_min, y_max = y_FI.min(), y_FI.max()
    x_border1, y_border1 = [index_band_start, index_band_start], [y_min, y_max]
    x_border2, y_border2 = [index_band_end, index_band_end], [y_min, y_max]

    ax.plot(x_FI, y_FI, color='#1f77b4', linewidth=1.5, label='FI')  
    ax.plot(x_blue, y_blue, color='#ff7f0e', linestyle='--', linewidth=1.2, label='Blue')  
    ax.plot(x_red, y_red, color='#2ca02c', linestyle='--', linewidth=1.2, label='Red')  
    ax.plot(x_FC, y_FC, color='#d62728', linewidth=1.2, label='FC')  

    ax.plot(x_border1, y_border1, color='#9467bd', linewidth=1, linestyle=':')  
    ax.plot(x_border2, y_border2, color='#9467bd', linewidth=1, linestyle=':')  
    ax.set_xlabel('Wavelength/($\AA$)')  
    ax.set_ylabel('Flux')  
    ax.legend(loc='upper right', frameon=False)  
    ax.spines['top'].set_visible(False)  
    ax.spines['right'].set_visible(False)  