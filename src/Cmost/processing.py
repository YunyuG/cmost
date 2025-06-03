import numpy as np
import pandas as pd

from scipy import interpolate
from .mtypes import array_like
from .utils import to_ndarray
        
def minmax_function(spectrum_data:pd.DataFrame)->pd.DataFrame:
    spectrum_data["Flux"] = (spectrum_data["Flux"] - spectrum_data["Flux"].min()) \
                            /(spectrum_data["Flux"].max() - spectrum_data["Flux"].min())
    return spectrum_data



def align_wavelength(spectrum_data:pd.DataFrame
                     ,aligned_wavelength:array_like)->pd.DataFrame:

    aligned_wavelength = to_ndarray(aligned_wavelength)
    
    Wavelength = spectrum_data["Wavelength"]
    Flux = spectrum_data["Flux"]

    F = interpolate.interp1d(Wavelength,Flux,kind="linear"
                            ,bounds_error=False
                            ,fill_value=(Flux[0],Flux[Flux.index[-1]]))
    
    spectrum_data_after = pd.DataFrame(data={
        "Wavelength":aligned_wavelength,
        "Flux":F(aligned_wavelength)
    })

    return spectrum_data_after


def remove_redshift(spectrum_data:pd.DataFrame
                    ,Z:float)->pd.DataFrame:
    # 删除红移
    # z=(wavelength_obs-wavelength_rest)/wavelength_rest
    
    Wavelength_obs = spectrum_data["Wavelength"]
    Flux_rest = spectrum_data["Flux"]
    Wavelength_rest = Wavelength_obs / (1 + Z)
    F = interpolate.interp1d(Wavelength_rest,Flux_rest,kind="linear"
                        ,bounds_error=False,fill_value=(Flux_rest[0],Flux_rest[Flux_rest.index[-1]]))
    spectrum_data["Flux"] = F(Wavelength_obs)
    return spectrum_data