import numpy as np
import pandas as pd
from scipy.ndimage import median_filter
from ..__construct import FitsData

__all__ = ["fit_by_window"]


def Heaviside_Function(s):
    
    c = 5 # 文献中c取5
    Hc = 1 / 2 * (1 + 2 / np.pi * np.arctan(s / c))
    return Hc

def compute_U_L(s):
    
    U = 55 + (Heaviside_Function(s) - Heaviside_Function(0))  \
        / 50 * (Heaviside_Function(100) - Heaviside_Function(0))
    L = 45 + (Heaviside_Function(s) - Heaviside_Function(0))  \
        / 50 * (Heaviside_Function(100) - Heaviside_Function(0))
    return U, L


def compute_S(origin_flux, filter_flux):
    
    S_up_formula = np.sum(np.abs(origin_flux - filter_flux))
    S_down_formula = np.sum(filter_flux)
    return S_up_formula / S_down_formula


def catch_one_window(spectrum_data: pd.DataFrame
                    , window_start_point: int
                    , window_end_point: int
                    , kernel_size:int):
    
    spectrum_intercept_window = spectrum_data[(spectrum_data["Wavelength"] >= window_start_point)
                & (spectrum_data["Wavelength"] <= window_end_point)].copy()
    # print(window)
    # f = spectrum_intercept_window["flux"]
    # m = spectrum_intercept_window["m"]
    
    # median_filter
    flux = spectrum_intercept_window["Flux"]
    filter_flux = median_filter(flux, kernel_size)

    S = compute_S(flux, filter_flux)
    U, L = compute_U_L(S)
    # sort
    spectrum_intercept_window.sort_values(by="Flux", inplace=True)
    spectrum_intercept_window.reset_index(drop=True, inplace=True)
    # note: U,L is percentage
    ub = int(U * 1e-2 * len(spectrum_intercept_window))
    lb = int(L * 1e-2 * len(spectrum_intercept_window))
    # print(ub,lb)
    # delete the data out of the range
    spectrum_intercept_window.drop(spectrum_intercept_window[(spectrum_intercept_window.index >= ub)
                    | (spectrum_intercept_window.index <=lb)].index, inplace=True, axis=0)
    return spectrum_intercept_window


def select_point(spectrum_data: pd.DataFrame
                 ,window_length:int
                 ,kernel_size:int ):
    

    wavelength_start_point = spectrum_data["Wavelength"].min()
    wavelength_end_point = spectrum_data["Wavelength"].max()
    windows = pd.DataFrame()
    for i in np.arange(wavelength_start_point + window_length
            , wavelength_end_point + window_length
            , window_length):
        window = catch_one_window(spectrum_data
                                  , i - window_length
                                  , i
                                  ,kernel_size=kernel_size)
        windows = pd.concat([windows, window], axis=0)
    windows.sort_values(by="Wavelength", inplace=True)
    windows.reset_index(drop=True, inplace=True)
    return windows


def fit_by_window(fits_or_spectrum_data:pd.DataFrame | FitsData
                  ,window_length:int=100
                  ,kernel_size:int=5
                  ,max_iterate_nums:int=10):
    """
    One-dimensional spectral fitting based on statistical windows.
    The reference paper is: doi:10.3964/j.issn.1000-0593(2012)08-2260-04

    :param data: Input spectral data. Must be either:
        - A two-column pandas DataFrame with columns named `Flux` and `Wavelength`.
        - An instance of the package's default FitsData structure.
    :param window_length: Size of each statistical window. Defaults to 100.
    :param kernel_size: Kernel size for median filtering. Defaults to 5.
    :param iterate_nums: Maximum number of fitting iterations. Defaults to 10.
    :return: Fitted spectrum data (same type as input).

    **Examples:**
    >>> import matplotlib.pyplot as plt
    >>> import Cmost as cst
    >>> import numpy as np
    >>> aligned_wavelength = np.arange(3700, 9100, 2)  # Example wavelength grid
    >>> fits_path = "spec-60591-LN042429N340750BM01_sp01-001.fits.gz"
    >>> fits_data = cst.read_fits(fits_path,ignore_mask_1=True)
    >>> # data processing
    >>> fits_data = fits_data.minmax().del_redshift().align_wavelength(aligned_wavelength)
    >>> fits_data2 = cst.fitting.fit_by_window(fits_data)
    >>> fits_data.visualize()
    >>> fits_data2.visualize()
    >>> plt.legend(['Original', 'Fitted'])
    >>> plt.show()
    """
    if isinstance(fits_or_spectrum_data, FitsData):
        spectrum_data = fits_or_spectrum_data.spectrum_data
    

    windows = select_point(spectrum_data
                           ,window_length=window_length
                           ,kernel_size=kernel_size)
    fw_set = windows.copy()
    # print(fw_set)
    fw_set["removed"] = [False] * len(fw_set)

    for i in range(max_iterate_nums):
        ws = fw_set.loc[fw_set['removed'] == False, "Wavelength"]
        fs = fw_set.loc[fw_set['removed'] == False, "Flux"]
        # five-degree polynomial fitting
        v = np.polyfit(ws, fs, 5)
        fc = np.polyval(v, ws)

        fn = fs / fc 
        a = fn.mean()  
        b = fn.std()  
        removed_point = np.r_[ws[fn < a - 3 * b], ws[fn > a + 3 * b]]
        if len(removed_point) == 0:
            break
        else:
            for r in removed_point:
                fw_set.loc[fw_set["Wavelength"] == r, "removed"] = True
    
    coef = v
    spectrum_data_after_fitting = pd.DataFrame(data={
                    "Wavelength":spectrum_data['Wavelength'].values
                    ,"Flux": np.polyval(coef, spectrum_data["Wavelength"])
                })
    if isinstance(fits_or_spectrum_data, FitsData):
        fits_data2 = FitsData(fits_or_spectrum_data.header,
                            spectrum_data_after_fitting)
        return fits_data2
    else:
        return spectrum_data_after_fitting