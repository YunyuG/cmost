__all__ = ["get_index_table","compute_LlIndices"]
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from ..__construct import FitsData
from scipy import integrate,interpolate
from pathlib import Path
from functools import cache


@cache
def get_index_table()->pd.DataFrame:
    index_path = Path(__file__).parent.parent / Path("assets") / "index.table"
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
    index_table.set_index("No.",inplace=True)
    return index_table


def extract_one_spectrum(spectrum_data: pd.DataFrame
                        , Wavelength_start: float, Wavelength_end: float)->pd.DataFrame:
    
    
    func = interpolate.interp1d(spectrum_data["Wavelength"]
                                , spectrum_data["Flux"], kind="linear")
    
    spectrum_data_intercept:pd.DataFrame = spectrum_data[
        (spectrum_data["Wavelength"] > Wavelength_start)
        & (spectrum_data["Wavelength"] < Wavelength_end)
        ].copy()

    Flux_start = func(Wavelength_start)
    Flux_end = func(Wavelength_end)
    spectrum_data_intercept = spectrum_data_intercept._append([{
        "Wavelength": Wavelength_start
        , "Flux": Flux_start
    }
        , {
            "Wavelength": Wavelength_end
            , "Flux": Flux_end
        }
    ], ignore_index=True)
    spectrum_data_intercept.sort_values("Wavelength", inplace=True)
    spectrum_data_intercept.reset_index(inplace=True)
    return spectrum_data_intercept
    

    
def compute_LlIndices(
    fits_or_spectrum_data:pd.DataFrame | FitsData
    ,index_table:pd.DataFrame = None
)->pd.DataFrame:
    """compute the LlIndices of the spectrum data.

    :param fits_or_spectrum_data: Input spectral data. Must be either:
        - A two-column pandas DataFrame with columns named `Flux` and `Wavelength`.
        - An instance of the package's default FitsData structure.
    :param index_table: A table contains band parameters in spectral analysis.
    This library comes with such an index table,
    which you can retrieve using `get_index_table`.
    It is sourced from https://astro.vaporia.com/start/lickindices.html

    :return: A pandas Series containing the computed LlIndices.

    **Examples:**
    1. Calculate Lick line Indices using the built-in index table:
    >>> import Cmost as cst
    >>> fits_path = "spec-60591-LN042429N340750BM01_sp01-001.fits.gz"
    >>> fits_data = cst.read_fits(fits_path,ignore_mask_1=True)
    >>> indices = cst.indices.compute_LlIndices(fits_data)
    >>> print(indices)
    CN_1       -0.029162
    CN_2       -0.002139
    Ca4227      1.482712
    G4300       6.125893
    Fe4383      5.898983
    Ca4455      1.643089
            ...
    Hdelta_A   -2.370209
    Hgamma_A   -5.547030
    Hdelta_F    0.305394
    Hgamma_F   -1.174197
    dtype: float64
    
    2. Calculate Lick line Indices using a custom index table:
    >>> custom_index_table = cst.indices.read_csv("****.csv") # you must keep the same format as the index table in the library
    >>> custom_index_table.columns = ['index_band_start'
    ...         ,'index_band_end'
    ...         ,'blue_continuum_start'
    ...         ,'blue_continuum_end'
    ...         ,'red_continuum_start'
    ...         ,'red_continuum_end'
    ...         ,'Units'
    ...         ,'name']
    >>> indices = cst.indices.compute_LlIndices(fits_data, index_table = custom_index_table)
    >>> print(indices)
    """
    if isinstance(fits_or_spectrum_data,FitsData):
        spectrum_data = fits_or_spectrum_data.spectrum_data
    else:
        spectrum_data = fits_or_spectrum_data
        
    if index_table is None:
        index_table = get_index_table()

    result: pd.Series = pd.Series()
    for i in range(len(index_table)):
        try:
            one_index_table = index_table.iloc[i, :]
            index_band_start = one_index_table["index_band_start"]
            index_band_end = one_index_table["index_band_end"]
            blue_continuum_start = one_index_table['blue_continuum_start']
            blue_continuum_end = one_index_table['blue_continuum_end']
            red_continuum_start = one_index_table['red_continuum_start']
            red_continuum_end = one_index_table['red_continuum_end']
            Units = one_index_table['Units']
            name = one_index_table['name']
        except Exception as e:
            error_info = """
The legitimate format of the index_table should be the same as the following table. Please check the column names or the entire table. 

    index_band_start  index_band_end  blue_continuum_start  blue_continuum_end  red_continuum_start  red_continuum_end  Units      name
No.
1            4142.125        4177.125              4080.125            4117.625             4244.125           4284.125      1      CN_1
2            4142.125        4177.125              4083.875            4096.375             4244.125           4284.125      1      CN_2
3            4222.250        4234.750              4211.000            4219.750             4241.000           4251.000      0    Ca4227
4            4281.375        4316.375              4266.375            4282.625             4318.875           4335.125      0     G4300
5            4369.125        4420.375              4359.125            4370.375             4442.875           4455.375      0    Fe4383
...             ...             ...                   ...                 ...                  ...               ...        ...    ..."""
            raise ValueError(error_info) from e
            

        FI_lambda, FC_lambda = compute_FI_lambda_FC_lambda(spectrum_data, index_band_start
                                                        , index_band_end, blue_continuum_start
                                                        , blue_continuum_end, red_continuum_start
                                                        , red_continuum_end)
        if Units == 0:
            result[name] = compute_EW(FI_lambda, FC_lambda)
        else:
            result[name] = compute_Mag(FI_lambda, FC_lambda)
    return result


def compute_FI_lambda_FC_lambda(spectrum_data: pd.DataFrame
                            , index_band_start: float
                            , index_band_end: float
                            , blue_continuum_start: float
                            , blue_continuum_end: float
                            , red_continuum_start: float
                            , red_continuum_end: float):
    FI_lambda: pd.DataFrame = extract_one_spectrum(spectrum_data, index_band_start, index_band_end)

    blue_continuum = extract_one_spectrum(spectrum_data, blue_continuum_start, blue_continuum_end)
    red_continuum = extract_one_spectrum(spectrum_data, red_continuum_start, red_continuum_end)

    blue_continuum_avg = compute_MeanFlux(blue_continuum)
    red_continuum_avg = compute_MeanFlux(red_continuum)

    blue_Wavelength_mid = (blue_continuum_start + blue_continuum_end) / 2.0
    red_Wavelength_mid = (red_continuum_start + red_continuum_end) / 2.0

    F = interpolate.interp1d(x=[blue_Wavelength_mid, red_Wavelength_mid]
                            , y=[blue_continuum_avg, red_continuum_avg]
                            , kind="linear")
    # FC_lambda = pd.Series(define=F(FI_lambda.index), index=FI_lambda.index)
    FC_lambda = pd.DataFrame({
        "Flux": F(FI_lambda["Wavelength"])
        , "Wavelength": FI_lambda["Wavelength"]
    })
    # print(FC_lambda,FI_lambda)
    return FI_lambda, FC_lambda


def compute_MeanFlux(spectrum_data: pd.DataFrame):
    lambda_1 = spectrum_data["Wavelength"].min()
    lambda_2 = spectrum_data["Wavelength"].max()
    AvgFlux = integrate.trapezoid(spectrum_data["Flux"], spectrum_data["Wavelength"]) / (lambda_2 - lambda_1)
    return AvgFlux


def compute_EW(FI_lambda, FC_lambda):
    return integrate.trapezoid(1 - (FI_lambda["Flux"] / FC_lambda["Flux"]), FI_lambda["Wavelength"])


def compute_Mag(FI_lambda, FC_lambda):
    lambda_1 = FI_lambda["Wavelength"].min()
    lambda_2 = FI_lambda["Wavelength"].max()
    return -2.5 * np.log10(integrate.trapezoid(FI_lambda["Flux"] / FC_lambda["Flux"], FI_lambda["Wavelength"]) / (lambda_2 - lambda_1))