# !/usr/bin/env python3
# Copyright (C) 2025 YunyuG

from __future__ import annotations

import numpy

from scipy.ndimage import median_filter
from .__fits_data import FitsData


# def Heaviside_function_padding(func):
#     @wraps(func)
#     def wrapper(*args,**kwargs):
#         return 1.6 * func(*args,**kwargs) + 0.4
#     return wrapper

# @Heaviside_function_padding

# FIXME: This function is not matched the article
def Heaviside_function(s,c):
    return 0.5  * (1 + (2.0 / numpy.pi) * numpy.arctan(s / c))

def compute_Ulimit(s,c):
    # c=5
    U = 55 + (Heaviside_function(s,c) - Heaviside_function(0, c)) *\
          (Heaviside_function(100,c)-Heaviside_function(0,c)) / 50
    return U


def compute_Llimit(s,c):
    # c=5
    L = 45 + (Heaviside_function(s,c) - Heaviside_function(0, c)) * \
        (Heaviside_function(100,c)-Heaviside_function(0,c)) / 50
    return L

def compute_SNR(f:numpy.ndarray,m:numpy.ndarray):
    snr = numpy.sum(numpy.abs(f - m)) / numpy.sum(m)
    # print(snr)
    return snr


def sw_fit(fits_data:FitsData = None
            ,*
            ,wavelength:numpy.ndarray = None
            ,flux:numpy.ndarray = None
            ,window_num:int = 10
            ,mean_filter_size:int = 5
            ,c:int = 5
            ,max_iterate_nums:int = 10
            ,)->tuple[numpy.ndarray,numpy.ndarray]:
    """Continuum spectrum fitting based on statistical windows

    :param fits_data:You can pass a FitsData object,which can be obtained by the `read_fits` function. You can also explicitly pass in `wavelength` and `flux` directly.

    :param wavelength: _description_, defaults to None
    :param flux: _description_, defaults to None
    :param window_num: _description_, defaults to 10
    :param mean_filter_size: _description_, defaults to 5
    :param c: _description_, defaults to 5
    :param max_iterate_nums: _description_, defaults to 10
    :raises ValueError: _description_
    :raises ValueError: _description_
    :raises ValueError: _description_
    :return: _description_
    """
    
    if (wavelength is None or flux is None) and fits_data is None:
        raise ValueError("must provide either `wavelength` and `flux` or `fits_data`")
    
    if fits_data is not None and (wavelength is not None or flux is not None):
        raise ValueError("must provide either `wavelength` and `flux` or `fits_data`")
    
    if fits_data is not None:
        wavelength = numpy.asarray(fits_data.wavelength)
        flux = numpy.asarray(fits_data.flux)
    else:
        wavelength = numpy.asarray(wavelength)
        flux = numpy.asarray(flux)
    
    try:
        wavelength_set = numpy.reshape(wavelength,(window_num,-1))
        flux_set = numpy.reshape(flux,(window_num,-1))
    except Exception as e:
        raise ValueError("the length of `wavelength` or `flux` "
                         f"{len(wavelength)} div `window_num` {window_num} is not Integer") from e
    # print(wavelength_set.shape,flux_set.shape)
    
    ws,fs = [],[]
    for i in range(window_num):
        w,f = choose_point(wavelength_set[i],flux_set[i],mean_filter_size,c)
        ws.append(w)
        fs.append(f)
    
    ws = numpy.concatenate(ws,axis=0)
    fs = numpy.concatenate(fs,axis=0)
    index = range(len(ws))

    index = sorted(index,key=lambda i:ws[i])
    ws = ws[index]
    fs = fs[index]

    for _ in range(max_iterate_nums):
        F = numpy.polyfit(ws,fs,5)
        fc = numpy.polyval(F,ws)
        fn = fs / fc
        a = numpy.mean(fn)
        b = numpy.std(fn)
        index = numpy.where((fn >= a - 3 * b) & (fn <= a + 3 * b))[0]
        ws = ws[index]
        fs = fs[index]

        if index.shape[0] == 0:
            break

    return ws,numpy.polyval(F,ws)


def choose_point(wavelength:numpy.ndarray
                 ,flux:numpy.ndarray
                 ,mean_filter_size:int
                 ,c:float):
    # wavelength = wavelength.copy()
    # flux = flux.copy()
    m = median_filter(flux,size=mean_filter_size)
    snr = compute_SNR(flux,m)
    U = compute_Ulimit(snr,c) * 1e-2 # the uints is `%`
    L = compute_Llimit(snr,c) * 1e-2 # the uints is `%`
    # print(U,L)
    index = range(len(wavelength))
    index = sorted(index,key=lambda i:flux[i])
    
    flux = flux[index]
    wavelength = wavelength[index]

    index_start = int(L * len(flux))
    index_end = int(U * len(flux))

    flux = flux[index_start:index_end+1]
    wavelength = wavelength[index_start:index_end+1]

    return wavelength,flux