import re
from pathlib import Path
import pandas as pd
from astropy.io import fits
from concurrent.futures import (
    ProcessPoolExecutor
    ,as_completed
)
from .strategy import (
    return_spectrum_le8
    ,return_spectrum_ge8
    ,return_header_info
)
from ..construct import FitsData

__all__ = ['read_fits','accel_read_fits']

def read_fits(
        fp:str
        ,*
        ,ignore_mask_1:bool = False
    )->FitsData:
        """
        read fits file,and return spectrum data

        :param fp: fits file path
        :return: spectrum data
        """
        
        with fits.open(fp) as hdu:
            header = return_header_info(hdu=hdu)
            DATA_V = header["DATA_V"]
            match = re.search(r'DR(\d{1,2})', DATA_V)
            dr_number = int(match.group(1))

            if dr_number>=8:
                spectrum_data = return_spectrum_ge8(hdu,ignore_mask_1)
            else:
                spectrum_data = return_spectrum_le8(hdu,ignore_mask_1)

        
        fits_data = FitsData(header=header
                          ,data=spectrum_data)

        return fits_data
    
        
def __return_fp_spectrum(fp:str
                         ,ignore_mask_1:bool = True
                         ,is_process:bool = True
                         ,**kwargs)->tuple[str,pd.DataFrame]:
    """
    return fp and spectrum data
    """
    if is_process:
        aligned_wavelength = kwargs["aligned_wavelength"]

    fits_data = read_fits(fp,ignore_mask_1=ignore_mask_1)
    if is_process:
        fits_data = fits_data.minmax() \
                            .del_redshift() \
                            .align_wavelength(aligned_wavelength)
    spectrum_data = fits_data.spectrum_data
    header = fits_data.header
    spectrum_data.set_index("Wavelength",inplace=True)
    return header,spectrum_data

        
        
def accel_read_fits(fits_paths:str,max_workers:int=6,**kwargs)->pd.DataFrame:
    spectrum_datas = []
    headers = []
    fits_names = []
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(__return_fp_spectrum,fp,**kwargs):fp for fp in fits_paths}
        num = 0
        for future in as_completed(futures):
            try:
                header,spectrum_data = future.result()
                if spectrum_data is not None:
                    fp = futures[future].split("/")[-1]
                    spectrum_datas.append(spectrum_data)
                    headers.append(header)
                    fits_names.append(fp)
            except Exception as e:
                print(f"Error:{e}")
            finally:
                num += 1
                print(f"Done:{num}",end='\r')

    
    spectrum_datas = pd.concat(spectrum_datas,axis=1).T
    spectrum_datas.index = fits_names
    headers = pd.concat(headers)
    return spectrum_datas,headers

