import numpy as np
import pandas as pd
from scipy.ndimage import median_filter




def Heaviside_Function(s):
    """
    根据信噪比S自动选取符合条件的流量点，函数形式为Heaviside函数形式
    :param s: 信噪比
    :return:
    """
    c = 5 # 文献中c取5
    Hc = 1 / 2 * (1 + 2 / np.pi * np.arctan(s / c))
    return Hc

def compute_U_L(s):
    """
    计算筛选点的上下限
    :param s: 信噪比
    :return:
    """
    U = 55 + (Heaviside_Function(s) - Heaviside_Function(0))  \
        / 50 * (Heaviside_Function(100) - Heaviside_Function(0))
    L = 45 + (Heaviside_Function(s) - Heaviside_Function(0))  \
        / 50 * (Heaviside_Function(100) - Heaviside_Function(0))
    return U, L


def compute_S(origin_flux, filter_flux):
    """
    按照文献要求计算信噪比S
    :param origin_flux:原始波长
    :param filter_flux:中值滤波后的波长
    :return:
    """
    S_up_formula = np.sum(np.abs(origin_flux - filter_flux))
    S_down_formula = np.sum(filter_flux)
    return S_up_formula / S_down_formula


def catch_one_window(spectrum_data: pd.DataFrame
                    , window_start_point: int
                    , window_end_point: int
                    , kernel_size:int = 7):
    """
    :param fw: flux和wavelength
    :param window_start_point: 窗口起始点
    :param window_end_point: 窗口结束点
    :return:
    """
    spectrum_intercept_window = spectrum_data[(spectrum_data["Wavelength"] >= window_start_point)
                & (spectrum_data["Wavelength"] <= window_end_point)].copy()
    # print(window)
    # f = spectrum_intercept_window["flux"]
    # m = spectrum_intercept_window["m"]
    
    # 中值滤波
    flux = spectrum_intercept_window["Flux"]
    filter_flux = median_filter(flux, kernel_size)
    # 计算S
    S = compute_S(flux, filter_flux)
    U, L = compute_U_L(S)
    # 排序
    spectrum_intercept_window.sort_values(by="Flux", inplace=True)
    spectrum_intercept_window.reset_index(drop=True, inplace=True)
    # 这里注意U,L都仍是百分比为化为小数形式
    ub = int(U * 1e-2 * len(spectrum_intercept_window))
    lb = int(L * 1e-2 * len(spectrum_intercept_window))
    # print(ub,lb)
    # 删除不在该范围的点
    spectrum_intercept_window.drop(spectrum_intercept_window[(spectrum_intercept_window.index >= ub)
                    | (spectrum_intercept_window.index <=lb)].index, inplace=True, axis=0)
    return spectrum_intercept_window


def select_point(spectrum_data: pd.DataFrame
                 ,window_length:int = 100):
    """
    筛选每个窗口符合条件的点并汇总到一个命名为windows的dataframe中
    :param fw:flux和wavelength
    :param window_length:窗口大小
    :return:
    """

    wavelength_start_point = spectrum_data["Wavelength"].min()
    wavelength_end_point = spectrum_data["Wavelength"].max()
    windows = pd.DataFrame()
    for i in np.arange(wavelength_start_point + window_length
            , wavelength_end_point + window_length
            , window_length):
        window = catch_one_window(spectrum_data, i - window_length, i)
        windows = pd.concat([windows, window], axis=0)
    windows.sort_values(by="Wavelength", inplace=True)
    windows.reset_index(drop=True, inplace=True)
    return windows


def fit_by_window(spectrum_data:pd.DataFrame
                  ,include_coef:bool=False
                  ,iterate_nums:int=10):
    """
    五阶多项式拟合
    :param windows:
    :return:
    """
    windows = select_point(spectrum_data)
    fw_set = windows.copy()
    # print(fw_set)
    fw_set["removed"] = [False] * len(fw_set)

    for i in range(iterate_nums): # 文献中提到最多迭代10次，或者没有可去除的点就可以结束循环
        ws = fw_set.loc[fw_set['removed'] == False, "Wavelength"]
        fs = fw_set.loc[fw_set['removed'] == False, "Flux"]
        # 五阶多项式拟合
        v = np.polyfit(ws, fs, 5)
        fc = np.polyval(v, ws)

        fn = fs / fc # 计算归一化光谱fn
        a = fn.mean()  # 算fn的均值
        b = fn.std()  # 算fn的标准差
        removed_point = np.r_[ws[fn < a - 3 * b], ws[fn > a + 3 * b]]
        if len(removed_point) == 0:
            break
        else:
            for r in removed_point:
                fw_set.loc[fw_set["Wavelength"] == r, "removed"] = True
    fw_fit = pd.DataFrame(data={
        "Wavelength": ws,
        "Flux": fc
    })
    coef = v
    return fw_fit, coef
 