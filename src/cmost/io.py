# !/usr/bin/env python3
# Copyright (C) 2025  YunyuG

from __future__ import annotations

__all__ = ["read_fits","read_header"]

import re
import numpy

from astropy.io import fits
from .processing import minmax_function,align_wavelength,remove_redshift,median_filter

class FitsData:
    def __init__(self,wavelength:numpy.ndarray
                    ,flux:numpy.ndarray,header = None):
        
        self.wavelength = wavelength
        self.flux = flux
        self.header = header

    
    def __getitem__(self,key):
        if key=='Wavelength':
            return self.wavelength
        elif key=='Flux':
            return self.flux
        else:
            return self.header[key]
    

    def minmax(self,range_:tuple = (0,1))->FitsData:
        self.flux = minmax_function(self.flux,range_)
        return self
    
    
    def align(self,aligned_wavelength:numpy.ndarray)->FitsData: 
        self.flux = align_wavelength(self.wavelength
                                    ,self.flux,aligned_wavelength)
        self.wavelength = aligned_wavelength
        return self
    

    def remove_redshift(self)->FitsData:
        Z = self.header['z']
        self.flux = remove_redshift(self.wavelength
                                    ,self.flux,Z)
        return self
    
    def median_filter(self,size:int=7)->FitsData:
        self.flux = median_filter(self.flux,size)
        return self
    
    def visualize(self,ax=None):
        if ax:
            plot_spectrum(self.wavelength,self.flux,ax,is_show=False)
        else:
            plot_spectrum(self.wavelength,self.flux,is_show=True)
    
    @classmethod
    def from_hdu(cls,hdu):
        header = Header.from_hdu(hdu)
        match = re.search(r'DR(\d{1,2})', header["data_v"])
        dr_version = int(match.group(1))

        data = hdu[0].data if dr_version<8 else hdu[1].data[0]

        if dr_version<8:
            # This part refers to the `read_lrs_fits` function in the `LAMOST` class of the `pylamost`` library
            # Specifically, see:
            #   https://github.com/fandongwei/pylamost
            coeff0 = header['coeff0']
            coeff1 = header['coeff1']
            pixel_num = header['naxis1']
            wavelength = 10 ** (coeff0+numpy.arange(pixel_num)*coeff1)
        else:
            wavelength = numpy.asarray(data[2],dtype=float)

        flux = numpy.asarray(data[0],dtype=float)
        andmask = numpy.asarray(data[3],dtype=int)
        orimask = numpy.asarray(data[4],dtype=int)

        if numpy.sum(orimask)>0 or numpy.sum(andmask)>0:
            header["exists_bad_points"] = 1
        else:
            header["exists_bad_points"] = 0
        
        if abs(float(header["z"]))>=1:
            header["unusual_redshift"] = 1
        else:
            header["unusual_redshift"] = 0

        return cls(wavelength,flux,header)

        
    def __repr__(self):
        return f"FitsData(filename={self.header['filename']})"
    
    
class Header(dict):
    def __init__(self,keys,values):
        super().__init__(zip(keys,values))
    
    def __setitem__(self,key,value):
        super().__setitem__(key,value)
    
    def __getitem__(self,key):
        return super().__getitem__(key)
    
    def __repr__(self):
        return f"Header({super().__repr__()})"
    
    @classmethod
    def from_hdu(cls,hdu):
        keys = []
        values = []
        for key,value in zip(hdu[0].header.keys()
                             ,hdu[0].header.values()):
            if "COMMENT" in key or len(key)<1:
                continue
            keys.append(key.lower())
            values.append(value)
        return cls(keys,values)
    

def plot_spectrum(wavelength:numpy.ndarray
                  ,flux:numpy.ndarray
                ,ax = None
                ,is_show:bool = False):
    rc_s = {
        "font.family":"Arial"
        ,"font.size": 14
        ,"xtick.labelsize":14
        ,"ytick.labelsize":14
        ,"mathtext.fontset": "cm"
        }
    import matplotlib.pyplot # lazy load
    matplotlib.pyplot.rcParams.update(rc_s)
    if ax:
        ax.plot(wavelength,flux)
    else:
        matplotlib.pyplot.plot(wavelength,flux)

    if is_show:
        matplotlib.pyplot.xlabel(r"Wavelength($\AA$)")
        matplotlib.pyplot.ylabel("Flux")
        matplotlib.pyplot.show()

    
def read_fits(fits_path:str)->FitsData:
    with fits.open(fits_path) as hdu:
        return FitsData.from_hdu(hdu)
    
    
def read_header(fits_path:str)->Header:
    with fits.open(fits_path) as hdu:
        return Header.from_hdu(hdu)