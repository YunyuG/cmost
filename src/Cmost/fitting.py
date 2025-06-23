import numpy

from scipy.ndimage import median_filter

def Heaviside_function(s,c):
    return 0.5 * (1 + 2 / numpy.pi * numpy.arctan(s - c))

def compute_Ulimit(s,c):
    # c=5
    U = 55 + (Heaviside_function(s,c) - Heaviside_function(0, c)) / 50 * \
            (Heaviside_function(100,c)-Heaviside_function(0,c))
    return U

def compute_Llimit(s,c):
    # c=5
    L = 45 + (Heaviside_function(s,c) - Heaviside_function(0, c)) / 50 * \
            (Heaviside_function(100,c)-Heaviside_function(0,c))
    return L

def compute_SNR(f:numpy.ndarray,m:numpy.ndarray):
    snr = numpy.sum(numpy.abs(f - m)) / numpy.sum(m)
    return snr

