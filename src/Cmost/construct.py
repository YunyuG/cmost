import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from .mtypes import array_like
from .processing import (
    minmax_function
    ,align_wavelength
    ,remove_redshift
)

class FitsData:
    def __init__(self
                 ,header: pd.Series
                 ,data: pd.DataFrame
            )->None:
        self.__header = header
        self.__data = data


    def minmax(self):
        spectrum_data = minmax_function(self.__data.copy())
        return FitsData(self.__header
                        ,spectrum_data)
    
    def del_redshift(self):
        spectrum_data = remove_redshift(self.__data.copy()
                                       ,self.redshift)
        return FitsData(self.__header
                       ,spectrum_data)
    
    def align_wavelength(self,aligned_wavelength:array_like):
        spectrum_data = align_wavelength(self.__data.copy()
                                       ,aligned_wavelength)
        return FitsData(self.__header
                      ,spectrum_data)
    def __repr__(self):
        return f"FitsData(filename={self.file_name},obsid={self.obsid},data_v=LAMOST DR{self.dr_number})"

    @property
    def spectrum_data(self):
        return self.__data
        
    @property
    def subclass(self):
        return self.__header['SUBCLASS']  

    @property
    def obsid(self):
        return self.__header['OBSID']
    
    @property
    def class_(self):
        return self.__header['CLASS']
    
    @property
    def redshift(self):
        return self.__header['Z']

    @property
    def file_name(self):
        return self.__header['FILENAME']
    
    @property
    def header(self):
        header_ = pd.Series(self.__header,dtype=str)
        return header_
    
    @property
    def dr_number(self):
        match = re.search(r'DR(\d{1,2})', self.__header['DATA_V'])
        if match:
            return int(match.group(1))
        else:
            raise ValueError("DR number not found in DATA_V")
        
    @staticmethod
    def __plot(data,ax:plt.axes = None
             ,is_show:bool = True):
        rc_s = {
            "font.size": 14
            }
        
        with sns.axes_style("ticks",rc=rc_s):
            if ax:
                sns.lineplot(data=data,x='Wavelength',y='Flux',ax=ax)
            else:
                sns.lineplot(data=data,x='Wavelength',y='Flux')

        if is_show:
            plt.show()
        
    def plot(self,ax:plt.axes = None
             ,is_show:bool = True):
        self.__plot(self.__data,ax,is_show)