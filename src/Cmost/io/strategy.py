import pandas as pd
from ..mtypes import array_like

class BadPointExistsError(Exception):
    ...

def return_spectrum_le8(hdu,ignore_mask_1:bool)->pd.DataFrame:
    """
    返回光谱数据
    :param fp: fits文件路径
    :return: 光谱数据
    """
        
    col_name = ['Flux', 'Inverse', 'Wavelength', 'Andmask', 'Ormask']

    spectrum_data = pd.DataFrame(hdu[0].data.T
                            ,dtype=float
                            ,columns=col_name)
    if mask_is_one(spectrum_data["Andmask"],spectrum_data["Ormask"]) and not ignore_mask_1: # 检查Andmask是否全为1
        raise BadPointExistsError("exists bad points in spectrum")

    spectrum_data = spectrum_data.loc[:,["Wavelength","Flux"]] # 删除无关列
    return spectrum_data
    


def return_spectrum_ge8(hdu,ignore_mask_1:bool)->pd.DataFrame:
    """
    返回光谱数据和红移
    :param fp: fits文件路径
    :return: 光谱数据和红移
    """

    col_name = ['Flux', 'Inverse', 'Wavelength', 'Andmask', 'Ormask',"Normalization"]
    
    spectrum_data = pd.DataFrame(hdu[1].data.item()).T
    spectrum_data.columns = col_name

    if mask_is_one(spectrum_data["Andmask"],spectrum_data["Ormask"]) and not ignore_mask_1: # 检查Andmask是否全为1
        raise BadPointExistsError("exists bad points in spectrum")
    

    spectrum_data = spectrum_data.loc[:,["Wavelength","Flux"]] # 删除无关列

    return spectrum_data



def return_header_info(hdu)->str | float:
    """
    返回fits文件的header
    """
    return hdu[0].header


def mask_is_one(Ormask:array_like
                    ,Andmask:array_like)->bool:
    """
    判断Ormask和Andmask是否存在1
    :param Ormask: Ormask
    :param Andmask: Andmask
    :return: bool
    """
    if Ormask.sum()>0 or Andmask.sum()>0:
        return True
    else:
        return False