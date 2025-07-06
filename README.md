# CMOST a Python Toolkit for LAMOST Astronomical Data
![Static Badge](https://img.shields.io/badge/python-3.9%7C3.10%7C3.11%7C3.12%7C3.13-brightgreen?style=flat&logo=python&logoColor=%23009385&labelColor=white&color=%23009385)
[![PyPI Version](https://img.shields.io/pypi/v/cmost?color=blue)](https://pypi.org/project/cmost/)

CMOST is a Python toolkit specifically designed for processing FITS files from LAMOST astronomical telescope observations. At its core, it's a secondary encapsulation of `astropy`, offering efficient and user-friendly data parsing and basic analysis capabilities.

### Key Features
- 🚀 Simple API interface `read_fits`, making FITS file handling as effortless as using `pandas` to read Excel files.
- 🔍 Statistical window fitting, line index calculation algorithms.
- 📊 Basic spectral preprocessing methods.
- 🌐 FTP API for downloading official LAMOST FITS files with asynchronous support.

Additionally, we offer a GUI application built on CMOST, enabling end-to-end spectral preprocessing without writing any code,it called `CMOST-GUI`.

We do not guarantee that the calculation results are 100% correct. If you find any defects or issues, please contact us. We would greatly appreciate it.

## Installation

CMOST is available on PyPI and can be installed using pip:

```
pip3 install cmost
```

## Usage
To use CMOST, simply import the `read_fits` function from the `cmost` module and pass the path to the FITS file as an argument:

```python
import cmost as cst

# Read FITS file
data = cst.read_fits('path/to/file.fits')

# Access data
print(data.header) # FITS header
print(data.wavelength) # wavelength
print(data.flux) # flux

data.visualize() # Plot the spectrum
```
