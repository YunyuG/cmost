# !/usr/bin/env python3
# Copyright (C) 2025 YunyuG

from __future__ import annotations

import numpy
from scipy import interpolate
        
def minmax_function(flux,range_:tuple)->numpy.ndarray:
    flux = range_[0] + (range_[1] - range_[0]) * (flux - numpy.min(flux)) \
        / (numpy.max(flux) - numpy.min(flux))
    return flux


def align_wavelength(wavelength:numpy.ndarray
                     ,flux:numpy.ndarray
                     ,aligned_wavelength:numpy.ndarray
                     ,**kwargs)->tuple[numpy.ndarray]:
    kind = kwargs.get("kind","linear")
    F = interpolate.interp1d(wavelength,flux,kind=kind
                            ,bounds_error=False
                            ,fill_value=(flux[0],flux[-1]))

    return F(aligned_wavelength)


def remove_redshift(wavelength_obs:numpy.ndarray
                     ,flux_rest:numpy.ndarray
                    ,Z:float
                    ,**kwargs)->tuple[numpy.ndarray]:
    kind = kwargs.get("kind","linear")
    wavelength_rest = wavelength_obs / (1 + Z)
    F = interpolate.interp1d(wavelength_rest,flux_rest,kind=kind
                        ,bounds_error=False,fill_value=(flux_rest[0],flux_rest[-1]))
    return F(wavelength_obs)