import asyncio
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


from functools import wraps

from .mtypes import array_like


def to_ndarray(data:array_like)->np.ndarray:
    """
    将数据类型转换为ndarray

    :param data: 待处理的数据
    :return: 处理后的ndarray数据
    """
    if isinstance(data,list):
        # 如果是list，通过`np.asarray`转换为ndarray
        data_ = np.asarray(data)

    elif isinstance(data,pd.Series | pd.DataFrame):
        # 如果是Series，通过`values`属性转换为ndarray
        data_ = data.values

    elif isinstance(data,np.ndarray):
        # 如果是ndarray，直接返回
        data_ = data
        
    else:
        raise ValueError("unknown type,please check it")
    
    return data_

def asyncio_decorator(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        if loop and loop.is_running():
            loop.create_task(func(*args,**kwargs))
        else:
            asyncio.run(func(*args,**kwargs))
    return wrapper

def plot_spectrum(data:pd.DataFrame
                ,ax:plt.axes = None
                ,is_show:bool = False):
    rc_s = {
        "font.family":"Arial"
        ,"font.size": 14
        ,"xtick.labelsize":14
        ,"ytick.labelsize":14
        ,"mathtext.fontset": "cm"
        }
    
    with sns.axes_style("ticks",rc=rc_s):
        if ax:
            sns.lineplot(data=data,x='Wavelength',y='Flux',ax=ax)
        else:
            sns.lineplot(data=data,x='Wavelength',y='Flux')

    if is_show:
        plt.xlabel(r"Wavelength($\AA$)")
        plt.ylabel("Flux")
        plt.show()