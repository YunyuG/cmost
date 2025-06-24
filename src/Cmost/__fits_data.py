# !/usr/bin/env python3
# Copyright (C) 2025  YunyuG

from __future__ import annotations

import numpy
import seaborn
import matplotlib.pyplot

from .__processing import minmax_function,align_wavelength,remove_redshift
        

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
        Z = self.header['Z']
        self.flux = remove_redshift(self.wavelength
                                    ,self.flux,Z)
        return self
    
    
    def visualize(self,ax=None):
        if ax:
            plot_spectrum(self.wavelength,self.flux,ax,is_show=False)
        else:
            plot_spectrum(self.wavelength,self.flux,is_show=True)
    
    def __repr__(self):
        return f"FitsData(filename={self.header['FILENAME']})"


def plot_spectrum(wavelength:numpy.ndarray
                  ,flux:numpy.ndarray
                ,ax:matplotlib.pyplot.Axes = None
                ,is_show:bool = False):
    rc_s = {
        "font.family":"Arial"
        ,"font.size": 14
        ,"xtick.labelsize":14
        ,"ytick.labelsize":14
        ,"mathtext.fontset": "cm"
        }
    
    with seaborn.axes_style("ticks",rc=rc_s):
        if ax:
            seaborn.lineplot(x=wavelength,y=flux,ax=ax)
        else:
            seaborn.lineplot(x=wavelength,y=flux)

    if is_show:
        matplotlib.pyplot.xlabel(r"Wavelength($\AA$)")
        matplotlib.pyplot.ylabel("Flux")
        matplotlib.pyplot.show()