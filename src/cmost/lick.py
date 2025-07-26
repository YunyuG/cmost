# !/usr/bin/env python3
# Copyright (C) 2025 YunyuG

from __future__ import annotations

import re
import numpy

from pathlib import Path
from dataclasses import dataclass
from functools import cache

from scipy import interpolate,integrate
from .io import FitsData

__all__ = ["read_LickLineIndex","compute_LickLineIndices"]

@dataclass
class LickLineIndex:
    index_band_start:float
    index_band_end:float
    blue_continuum_start:float
    blue_continuum_end:float
    red_continuum_start:float
    red_continuum_end:float
    units:int
    index_name:str


@cache
def read_LickLineIndex(fp:str)->list[LickLineIndex]:
    res = []
    pattern = r"[\d+._A-z]+"
    with open(fp,"r",encoding='utf-8') as file:
        try:
            for line in file.readlines():
                if "#" in line:
                    continue
                else:
                    f = re.findall(pattern,line)[1:] # ignore the index
                    l = LickLineIndex(
                        index_band_start=float(f[0]),
                        index_band_end=float(f[1]),
                        blue_continuum_start=float(f[2]),
                        blue_continuum_end=float(f[3]),
                        red_continuum_start=float(f[4]),
                        red_continuum_end=float(f[5]),
                        units=int(f[6]),
                        index_name=f[7]
                    )
                    res.append(l)
        except Exception as e:
            raise ValueError("The lick line index table does not meet the program's expectations."
                             "You need to ensure that the table format is as follows:\n\n"
                             "##        Index band       blue continuum     red continuum Units name\n"
                             "01    4142.125 4177.125  4080.125 4117.625  4244.125 4284.125 1  CN_1\n"
                             "02    4142.125 4177.125  4083.875 4096.375  4244.125 4284.125 1  CN_2\n" 
                             "03    4222.250 4234.750  4211.000 4219.750  4241.000 4251.000 0  Ca4227\n" 
                             "04    4281.375 4316.375  4266.375 4282.625  4318.875 4335.125 0  G4300\n"  
                             "05    4369.125 4420.375  4359.125 4370.375  4442.875 4455.375 0  Fe4383\n" 
                             "06    4452.125 4474.625  4445.875 4454.625  4477.125 4492.125 0  Ca4455\n"
                             "...          ...                ...                ...       ...   ...") from e
    return res

# print(read_LickLineIndex())

def compute_LickLineIndices(fits_data:FitsData = None
                            ,*
                            ,wavelength:numpy.ndarray = None
                            ,flux:numpy.ndarray = None
                            ,LickLineIndex_table:list[LickLineIndex] = None
                            )->dict:
    if (wavelength is None or flux is None) and fits_data is None:
        raise ValueError("must provide either `wavelength` and `flux` or `fits_data`")
    
    if fits_data is not None and (wavelength is not None or flux is not None):
        raise ValueError("must provide either `wavelength` and `flux` or `fits_data`")
    
    if LickLineIndex_table is None:
        LickLineIndex_table = read_LickLineIndex(str(Path(__file__).parent / Path("assets") / Path("index.table")))
    
    if fits_data is not None:
        wavelength = numpy.asarray(fits_data.wavelength)
        flux = numpy.asarray(fits_data.flux)
    else:
        wavelength = numpy.asarray(wavelength)
        flux = numpy.asarray(flux)

    res = dict()
    for lick_line_index in LickLineIndex_table:

        (wavelength_FI_lambda
        ,flux_FI_lambda
        ,wavelength_FC_lambda
        ,flux_FC_lambda) = compute_FI_lambda_FC_lambda(wavelength,flux
                                                       ,lick_line_index)
        if lick_line_index.units == 0:
            res[lick_line_index.index_name] = compute_EW(wavelength_FI_lambda,flux_FI_lambda,wavelength_FC_lambda,flux_FC_lambda)
        else:
            res[lick_line_index.index_name] = compute_Mag(wavelength_FI_lambda,flux_FI_lambda,wavelength_FC_lambda,flux_FC_lambda)
    return res
            
            

def compute_FI_lambda_FC_lambda(
        wavelength:numpy.ndarray
        ,flux:numpy.ndarray
        , lick_line_index: LickLineIndex
):
    func = interpolate.interp1d(wavelength
                                   ,flux,kind="linear")
    
    wavelength_FI_lambda,flux_FI_lambda = extract_one_spectrum(wavelength
                                     ,flux
                                    ,lick_line_index.index_band_start,
                                    lick_line_index.index_band_end
                                    ,func=func)

    wavelength_blue_continuum,flux_blue_continuum = extract_one_spectrum(wavelength
                                          ,flux
                                        ,lick_line_index.blue_continuum_start
                                        ,lick_line_index.blue_continuum_end
                                        ,func=func)
    
    wavelength_red_continuum,flux_red_continuum = extract_one_spectrum(wavelength
                                         ,flux
                                        ,lick_line_index.red_continuum_start
                                        ,lick_line_index.red_continuum_end
                                        ,func=func)
    
    blue_wavelength_mid = (lick_line_index.blue_continuum_start + lick_line_index.blue_continuum_end) / 2
    red_wavelength_mid = (lick_line_index.red_continuum_start + lick_line_index.red_continuum_end) / 2

    blue_mean_flux = compute_mean_flux(wavelength_blue_continuum,flux_blue_continuum)
    red_mean_flux = compute_mean_flux(wavelength_red_continuum,flux_red_continuum)

    F = interpolate.interp1d(y=[blue_mean_flux,red_mean_flux]
                            ,x=[blue_wavelength_mid,red_wavelength_mid]
                            ,kind="linear")
    # FC_lambda = Spectrum(FI_lambda.wavelength
    #                      ,F(FI_lambda.wavelength))
    wavelength_FC_lambda = wavelength_FI_lambda.copy()
    flux_FC_lambda = F(wavelength_FC_lambda)

    return wavelength_FI_lambda,flux_FI_lambda,wavelength_FC_lambda,flux_FC_lambda



def compute_mean_flux(
    wavelength:numpy.ndarray
    ,flux:numpy.ndarray
)->tuple[float]:
    lambda_1 = numpy.min(wavelength)
    lambda_2 = numpy.max(wavelength)
    mean_flux = integrate.trapezoid(flux,wavelength) / (lambda_2 - lambda_1)
    return mean_flux

    

def extract_one_spectrum(wavelength:numpy.ndarray
                         ,flux:numpy.ndarray
                        ,index_band_start:float
                        ,index_band_end:float
                        ,func:callable = None):
    if func is None:
        func = interpolate.interp1d(wavelength
                                   ,flux,kind="linear")
    
    index_ = numpy.where((wavelength > index_band_start) 
                    & (wavelength < index_band_end))[0]
    
    wavelength_intercept = wavelength[index_]
    flux_intercept = flux[index_]

    # low effecency
    # wavelength_intercept = np.insert(wavelength_intercept,[0,n]
    #                                                 ,[Wavelength_start,Wavelength_end])
    # flux_intercept = np.insert(flux_intercept,[0,n]
    #                                         ,[func(Wavelength_start),func(Wavelength_end)])

    wavelength_intercept = numpy.concatenate(([index_band_start]
                                              ,wavelength_intercept
                                             ,[index_band_end]))
    
    flux_intercept = numpy.concatenate(([func(index_band_start)]
                                        ,flux_intercept
                                       ,[func(index_band_end)]))
    return wavelength_intercept,flux_intercept
    # return wavelength_intercept,flux_intercept

def compute_EW(wavelength_FI_lambda
               ,flux_FI_lambda
               ,wavelength_FC_lambda
               ,flux_FC_lambda)->float:
    
    return integrate.trapezoid(1 - (flux_FI_lambda / flux_FC_lambda), wavelength_FI_lambda)


def compute_Mag(wavelength_FI_lambda
               ,flux_FI_lambda
               ,wavelength_FC_lambda
               ,flux_FC_lambda
               )->float:
    
    lambda_1 = numpy.min(wavelength_FI_lambda)
    lambda_2 = numpy.max(wavelength_FI_lambda)
    return -2.5 * numpy.log10(integrate.trapezoid(flux_FI_lambda/ flux_FC_lambda, wavelength_FI_lambda) / (lambda_2 - lambda_1))
