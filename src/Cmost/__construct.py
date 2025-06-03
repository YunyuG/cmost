import re
import pandas as pd
import matplotlib.pyplot as plt
from .utils import plot_spectrum
from .mtypes import array_like
from .processing import (
    minmax_function
    ,align_wavelength
    ,remove_redshift
)

__all__ = [
    "FitsData"
]

class RedshiftIsUnusal(Exception):
    def __init__(self,redshift:float,filename:str,redshift_threshold:float):
        self.message = (f"The redshift value is {redshift}, exceeding our restricted threshold of {redshift_threshold}."
                        ,f" We consider this spectrum abnormal and recommend deleting the spectrum in `{filename}`."
                        ,"If you still wish to proceed with reading, we do **not recommend** using the `del_redshift` method to remove the redshift,"
                        ," as this will cause anomalies in the final data.")
        super().__init__(*self.message)

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
        # to developer: if you want to change the redshift threshold
        # please change the value of RED_SHIFT_THRESHOLD
        RED_SHIFTT_THRESHOLD = 2
        if abs(self.redshift)>=RED_SHIFTT_THRESHOLD:
            raise RedshiftIsUnusal(self.redshift,self.file_name,RED_SHIFTT_THRESHOLD)
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
    
        
    def visualize(self
                  ,ax:plt.axes = None
                  ,is_show:bool = False):
        plot_spectrum(self.__data,ax=ax,is_show=is_show)