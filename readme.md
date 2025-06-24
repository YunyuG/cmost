# CMOST 一个针对于LAMOST的fits文件处理工具
![Static Badge](https://img.shields.io/badge/python-3.10%7C3.11%7C3.12%7C3.13-brightgreen?style=flat&logo=python&logoColor=%23009385&labelColor=white&color=%23009385)
[![PyPI Version](https://img.shields.io/pypi/v/cmost?color=blue)](https://pypi.org/project/cmost/)

CMOST 是一个专门用于处理LAMOST天文望远镜观测数据FITS文件的Python工具包，本质是对`astropy`的二次封装，提供高效便捷的数据解析、和基础分析功能。

## 主要功能
- 🚀 提供简单api接口`read_fits`,像使用`pandas`读取`excel`一样轻松快捷
- 🔍 提供统计窗拟合、线指数计算和模板匹配算法
- 📊 提供基本光谱预处理方法
- 🌐 提供ftp下载LAMOST官方fits文件的api,且添加了异步支持

## 安装
```bash
pip install cmost
```

## 快速开始
```python
from cmost import read_fits
data = read_fits("path/to/your/fits/file.fits")
