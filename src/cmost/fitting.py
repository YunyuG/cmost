# !/usr/bin/env python3
# Copyright (C) 2025 YunyuG

from __future__ import annotations

import numpy

from scipy.ndimage import median_filter
from .io import FitsData


class SwFitting5d:

    def __init__(self
                ,fits_data:FitsData = None
                ,*
                ,wavelength:numpy.ndarray = None
                ,flux:numpy.ndarray = None
                ,window_num:int = 10
                ,mean_filter_size:int = 50
                ,c:int = 5
                ,max_iterate_nums:int = 10):
        
        if (wavelength is None or flux is None) and fits_data is None:
            raise ValueError("must provide either `wavelength` and `flux` or `fits_data`")
        
        if fits_data is not None and (wavelength is not None or flux is not None):
            raise ValueError("must provide either `wavelength` and `flux` or `fits_data`")
        
        if fits_data is not None:
            self.wavelength = numpy.asarray(fits_data.wavelength)
            self.flux = numpy.asarray(fits_data.flux)
        else:
            self.wavelength = numpy.asarray(wavelength)
            self.flux = numpy.asarray(flux)
        
        self.window_num = window_num
        self.mean_filter_size = mean_filter_size
        self.c = c
        self.max_iterate_nums = max_iterate_nums

        self.band()
    
    
    def band(self):

        try:
            wavelength_set = numpy.reshape(self.wavelength,(self.window_num,-1))
            flux_set = numpy.reshape(self.flux,(self.window_num,-1))
        except Exception as e:
            raise ValueError("the length of `wavelength` or `flux` "
                            f"{len(self.wavelength)} div `window_num` {self.window_num} is not Integer") from e
        # print(wavelength_set.shape,flux_set.shape)
        
        ws,fs = [],[]
        for i in range(self.window_num):
            w,f = choose_point(wavelength_set[i]
                               ,flux_set[i],self.mean_filter_size,self.c)
            ws.append(w)
            fs.append(f)
        
        ws = numpy.concatenate(ws,axis=0)
        fs = numpy.concatenate(fs,axis=0)
        index = numpy.argsort(ws)
        # index = range(len(ws))
        # index = sorted(index,key=lambda i:ws[i])
        ws = ws[index]
        fs = fs[index]

        for _ in range(self.max_iterate_nums):
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
        # self.wavelength = ws
        self.coef = F
        # return self
    
    def __call__(self
                 ,fits_data:FitsData
                 ,*
                 , wavelength:numpy.ndarray = None)->numpy.ndarray:
        

        if wavelength is None and fits_data is None:
            raise ValueError("must provide either `wavelength` or `fits_data`")
        
        if fits_data is not None and wavelength is not None:
            raise ValueError("must provide either `wavelength` or `fits_data`")
        
        if fits_data is not None:
            wavelength = numpy.asarray(fits_data.wavelength)
        else:
            wavelength = numpy.asarray(wavelength)
        
        return numpy.polyval(self.coef,wavelength)



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
    return snr


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
    # index = range(len(wavelength))
    # index = sorted(index,key=lambda i:flux[i])

    index = numpy.argsort(flux)
    flux = flux[index]
    wavelength = wavelength[index]

    index_start = int(L * len(flux))
    index_end = int(U * len(flux))
    flux = flux[index_start:index_end+1]
    wavelength = wavelength[index_start:index_end+1]

    return wavelength,flux