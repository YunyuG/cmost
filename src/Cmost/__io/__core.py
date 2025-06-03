import re
from pathlib import Path
import numpy as np
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
from ..__construct import FitsData
from ..mtypes import array_like
from ..utils import to_ndarray

__all__ = ['read_fits','accel_read_fits']

def read_fits(
        fp:str
        ,*
        ,ignore_mask_1:bool = False
    )->FitsData:
    """
    interface for reading `FITS` files

    :param fp: The address of the `FITS` file
    :param ignore_mask_1: Ignore bad pixel anomalies., defaults to False
    :return: FitsData which has header and spectrum data

    | **Member**         | **Type**         | **Description**                                                                                               |
    |--------------------|------------------|---------------------------------------------------------------------------------------------------------------|
    | `header`           | `pd.Series`      | FITS file header metadata (e.g., observation parameters, instrument configuration, converted to string type). |
    | `spectrum_data`    | `pd.DataFrame`   | Spectrum data with two columns: <br>`Wavelength` (wavelength values) and `Flux` (flux values).                |
    | `subclass`         | `str`            | Astronomical subclass (extracted from the `SUBCLASS` header field).                                           |
    | `obsid`            | `str/int`        | Observation ID (extracted from the `OBSID` header field).                                                     |
    | `class_`           | `str`            | Astronomical class (extracted from the `CLASS` header field; suffix `_` avoids keyword conflict).             |
    | `redshift`         | `float`          | Redshift value (extracted from the `Z` header field).                                                         |
    | `file_name`        | `str`            | File name (extracted from the `FILENAME` header field).                                                       |
    | `dr_number`        | `int`            | Data release number (parsed from `DATA_V`, e.g., `13` from `LAMOST DR13`).                                    |

    **examples**
    >>> import Cmost as ct
    >>> import numpy as np
    >>> import matplotlib.pyplot as plt
    >>> fp = "spec-60591-LN042429N340750BM01_sp01-001.fits.gz"
    >>> fits_data = ct.read_fits(fp,ignore_mask_1=True)
    >>> print(fits_data)
    FitsData(filename=spec-60591-LN042429N340750BM01_sp01-001.fits,obsid=1247301001,data_v=LAMOST DR13)
    >>> print(fits_data.header) # header info
    SIMPLE      True
    BITPIX        16
    NAXIS          0
    NAXIS1      3909
    NAXIS2         5
            ...  
    SNRU        21.9
    SNRG      102.45
    SNRR      194.94
    SNRI      236.02
    SNRZ      187.13
    Length: 123, dtype: object
    >>> print(fits_data.spectrum_data) # spectrum data
           Wavelength        Flux
    0     3699.986328  317.118958
    1     3700.838379  315.441437
    2     3701.690674  331.342560
    3     3702.542969  302.750244
    4     3703.395752  304.119110
    ...           ...         ...
    3904  9090.758789    0.000000
    3905  9092.851562    0.000000
    3906  9094.945312    0.000000
    3907  9097.040039    0.000000
    3908  9099.134766    0.000000

    [3909 rows x 2 columns]
    >>> print(fits_data.subclass) # subclass info
    G5
    >>> fits_data2 = fits_data.minmax().del_redshift().align_wavelength(np.arange(3700,9100,2)) # minmax,del_redshift,align_wavelength
    >>> fig,ax = plt.subplots(2,1)
    >>> fits_data.visualize(ax=ax[0]) # visualize
    >>> fits_data2.visualize(ax=ax[1]) # visualize
    >>> plt.tight_layout()
    >>> plt.show()
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
    
        
def return_fp_spectrum(fp:str
                         ,ignore_mask_1:bool = True
                         ,aligned_wavelength:array_like = None
                         )->tuple[str,pd.DataFrame]:

    fits_data = read_fits(fp,ignore_mask_1=ignore_mask_1)
    if aligned_wavelength:
        fits_data = fits_data.minmax() \
                            .del_redshift() \
                            .align_wavelength(aligned_wavelength)
    
    spectrum_data = fits_data.spectrum_data
    header = fits_data.header
    spectrum_data.set_index("Wavelength",inplace=True)
    return header,spectrum_data

        
        
def accel_read_fits(fits_paths:str
                    ,max_workers:int=6
                    ,is_process:bool = True
                    ,aligned_wavelength:array_like = None)->pd.DataFrame:
    """Multiple processes read the FITS file

    :param fits_paths: A list of the paths of the FITS file to be read
    :param max_workers: Maximum number of processes, defaults to 6
    :param is_process: _description_, defaults to True
    :param aligned_wavelength: _description_, defaults to None
    :return: _description_
    """
    spectrum_datas = []
    headers = []
    fits_names = []

    if is_process:
        if aligned_wavelength is None:
            aligned_wavelength = np.arange(3700,9100,2)
        else:
            aligned_wavelength = to_ndarray(aligned_wavelength)

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(return_fp_spectrum,fp,aligned_wavelength):fp for fp in fits_paths}
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

