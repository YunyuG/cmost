import numpy as np
import pandas as pd

from scipy import interpolate
from .mtypes import array_like
from .utils import to_ndarray
        
def minmax_function(spectrum_data:pd.DataFrame)->pd.DataFrame:
    """
    归一化光谱数据

    :param spectrum_data: 待处理的光谱数据

    :return: 处理后的光谱数据
    """
    spectrum_data["Flux"] = (spectrum_data["Flux"] - spectrum_data["Flux"].min()) \
                            /(spectrum_data["Flux"].max() - spectrum_data["Flux"].min())
    return spectrum_data



def align_wavelength(spectrum_data:pd.DataFrame
                     ,aligned_wavelength:array_like)->pd.DataFrame:
    """
    等距离对齐波长

    :param spectrum_data: 待处理的光谱数据
    :param normal_wavelength: 对齐后的波长

    :return: 处理后的光谱数据
    """

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
    """
    删除红移

    :param spectrum_data: 待处理的光谱数据
    :param Z: 红移

    :return: 处理后的光谱数据
    """
    # 删除红移
    # z=(wavelength_obs-wavelength_rest)/wavelength_rest
    
    Wavelength_obs = spectrum_data["Wavelength"]
    Flux_rest = spectrum_data["Flux"]
    Wavelength_rest = Wavelength_obs / (1 + Z)
    F = interpolate.interp1d(Wavelength_rest,Flux_rest,kind="linear"
                        ,bounds_error=False,fill_value=(Flux_rest[0],Flux_rest[Flux_rest.index[-1]]))
    spectrum_data["Flux"] = F(Wavelength_obs)
    return spectrum_data