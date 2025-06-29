# !/usr/bin/env python3
# Copyright (C) 2025  YunyuG

from __future__ import annotations

__all__ = ["read_fits","read_header"]

import re
import numpy
import warnings

from astropy.io import fits

from .__fits_data import FitsData


class DataUnusalWarning(Warning):
    ...

def read_fits(
        fits_path:str
        ,*
        ,ignore_mask_1:bool = False
        ,ignore_unusual_z:bool = False
    )->FitsData:
    """Read a FITS file and return a structured data object.
    
    :param fp: Path to the FITS file
    :param ignore_mask_1: Whether to ignore bad pixels, defaults to False
    :param ignore_unusual_z: Whether to ignore unusual redshift values, defaults to False
    :return: A FitsData object containing wavelength, flux, and header information
    """
        
    with fits.open(fits_path) as hdu:
        header = hdu[0].header
        DATA_V = header["DATA_V"]
        match = re.search(r'DR(\d{1,2})', DATA_V)
        dr_number = int(match.group(1))

        data = hdu[0].data if dr_number<8 else hdu[1].data.item()
        wavelength = numpy.asarray(data[2],dtype=float)
        flux = numpy.asarray(data[0],dtype=float)

        if ignore_mask_1:
            andmask = numpy.asarray(data[3],dtype=int)
            orimask = numpy.asarray(data[4],dtype=int)
            if numpy.sum(orimask)>0 or numpy.sum(andmask)>0:
                warnings.warn("exists bad points in spectrum"
                              "if you want to ignore them, set `ignore_mask_1=True`"
                              ,DataUnusalWarning)

        if ignore_unusual_z:
            z = float(hdu[0].header["Z"])
            if abs(z)>=1:
                warnings.warn("unusual redshift"
                              "if you want to ignore it, set `ignore_unusual_z=True`"
                              ,DataUnusalWarning)

        return FitsData(wavelength,flux,hdu[0].header)

def read_header(fits_path:str,key:str = None)->dict | str:
    with fits.open(fits_path) as hdu:
        header = hdu[0].header
    if key is None:
        return header
    else:
        return header[key]