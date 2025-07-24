
<img src="ico.png" width="90" height="90" align="left" />

# CMOST: A Python Toolkit for LAMOST Astronomical Data
![Static Badge](https://img.shields.io/badge/python-3.9%7C3.10%7C3.11%7C3.12%7C3.13-brightgreen?style=flat&logo=python&logoColor=%23009385&labelColor=white&color=%23009385)
[![PyPI Version](https://img.shields.io/pypi/v/cmost?color=blue)](https://pypi.org/project/cmost/)

CMOST is a Python toolkit specifically designed for processing FITS files from LAMOST astronomical telescope observations. At its core, it's a secondary encapsulation of `astropy`, offering efficient and user-friendly data parsing and basic analysis capabilities.

### Key Features
- 🚀 Simple API interface `read_fits`, making FITS file handling as effortless as using `pandas` to read Excel files.
- 🔍 Statistical window fitting, line index calculation algorithms.
- 📊 Basic spectral preprocessing methods.
- 🌐 FTP API for downloading official LAMOST FITS files with asynchronous support.

Additionally, we offer a GUI application built on CMOST, enabling end-to-end spectral preprocessing without writing any code,it called `CMOST-GUI`.(Coming soon)

We do not guarantee that the calculation results are 100% correct. If you find any defects or issues, please contact us. We would greatly appreciate it.

## Installation

CMOST is available on PyPI and can be installed using pip:

```
pip3 install cmost
```

## Usage
### Reading FITS files
we provide a simple API interface `read_fits` to read FITS files. It returns a `FitsData` object, which contains the FITS header, wavelength, and flux data. Here's a simple example of how to use CMOST to read and access LAMOST FITS files:

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
we also provide some processing methods.For example, methods such as wavelength alignment, redshift removal, normalization, and median filtering. Here's an example of how to use these methods:

```python
import numpy as np
import cmost as cst
import matplotlib.pyplot as plt

aligned_wavelength = np.arange(3900,9100,2)
# Read FITS file
data = cst.read_fits('path/to/file.fits')

data2 = data.minmax() # min-max normalization
data2 = data2.remove_redshift() # remove redshift
data2 = data2.align_wavelength(aligned_wavelength) # align 
data2 = data2.median_filter(kernel_size=10) # median filter
fig, ax = plt.subplots(1,2)
data.visualize(ax=ax[0])
data2.visualize(ax=ax[1])
plt.show()
```

### Downloading LAMOST FITS files
if you want to download LAMOST FITS files from the official FTP server, you can use the `download_fits` function:
```python
import cmost as cst

obsids_list = [101001, 101002, 101005]
cst.download_fits(obsids_list=obsids_list
                    ,dr_version="9"
                    ,sub_version="2.0" # notice :`.0` is required
                    ,save_dir='./dr9_v2.0'
                    ,TOKEN="******")
```
In this module,In this module, we have referred to some URL construction methods of the `pylamost` tool.

### Lick indices
CMOST provides a simple function to calculate Lick indices:
```python
import cmost as cst

# Read FITS file
data = cst.read_fits('path/to/file.fits')

# Calculate Lick indices
lick_indices = cst.lick.compute_lick_indices(data)
print(lick_indices)
```
The default Lick index table in the package is as follows, which is derived from a paper published by Guy Worthy et al. in 1994.
| Index band       | blue continuum     | red continuum      | Units | name      |
|------------------|--------------------|--------------------|-------|-----------|
| 4142.125 4177.125 | 4080.125 4117.625  | 4244.125 4284.125  | 1     | CN_1      |
| 4142.125 4177.125 | 4083.875 4096.375  | 4244.125 4284.125  | 1     | CN_2      |
| 4222.250 4234.750 | 4211.000 4219.750  | 4241.000 4251.000  | 0     | Ca4227    |
| 4281.375 4316.375 | 4266.375 4282.625  | 4318.875 4335.125  | 0     | G4300     |
| 4369.125 4420.375 | 4359.125 4370.375  | 4442.875 4455.375  | 0     | Fe4383    |
| 4452.125 4474.625 | 4445.875 4454.625  | 4477.125 4492.125  | 0     | Ca4455    |
| 4514.250 4559.250 | 4504.250 4514.250  | 4560.500 4579.250  | 0     | Fe4531    |
| 4634.000 4720.250 | 4611.500 4630.250  | 4742.750 4756.500  | 0     | Fe4668    |
| 4847.875 4876.625 | 4827.875 4847.875  | 4876.625 4891.625  | 0     | H_beta    |
| 4977.750 5054.000 | 4946.500 4977.750  | 5054.000 5065.250  | 0     | Fe5015    |
| 5069.125 5134.125 | 4895.125 4957.625  | 5301.125 5366.125  | 1     | Mg_1      |
| 5154.125 5196.625 | 4895.125 4957.625  | 5301.125 5366.125  | 1     | Mg_2      |
| 5160.125 5192.625 | 5142.625 5161.375  | 5191.375 5206.375  | 0     | Mg_b      |
| 5245.650 5285.650 | 5233.150 5248.150  | 5285.650 5318.150  | 0     | Fe5270    |
| 5312.125 5352.125 | 5304.625 5315.875  | 5353.375 5363.375  | 0     | Fe5335    |
| 5387.500 5415.000 | 5376.250 5387.500  | 5415.000 5425.000  | 0     | Fe5406    |
| 5696.625 5720.375 | 5672.875 5696.625  | 5722.875 5736.625  | 0     | Fe5709    |
| 5776.625 5796.625 | 5765.375 5775.375  | 5797.875 5811.625  | 0     | Fe5782    |
| 5876.875 5909.375 | 5860.625 5875.625  | 5922.125 5948.125  | 0     | Na_D      |
| 5936.625 5994.125 | 5816.625 5849.125  | 6038.625 6103.625  | 1     | TiO_1     |
| 6189.625 6272.125 | 6066.625 6141.625  | 6372.625 6415.125  | 1     | TiO_2     |
| 4084.750 4123.500 | 4042.850 4081.000  | 4129.750 4162.250  | 0     | Hdelta_A  |
| 4321.000 4364.750 | 4284.750 4321.000  | 4368.500 4421.000  | 0     | Hgamma_A  |
| 4092.250 4113.500 | 4058.500 4089.750  | 4116.000 4138.500  | 0     | Hdelta_F  |
| 4332.500 4353.500 | 4284.750 4321.000  | 4356.000 4386.000  | 0     | Hgamma_F  |

### Continuous spectrum fitting based on statistical window
CMOST provides a simple function to fit a continuous spectrum based on statistical window:
```python
import cmost as cst
import numpy as np
import matplotlib.pyplot as plt

# Read FITS file
data = cst.read_fits('path/to/file.fits')

aliged_wavelength = np.arange(3700,9100,2)

data2 = data.minmax().remove_redshift().align(aliged_wavelength) # you must align the wavelength before fitting

sw_model = cst.fitting.SwFitting5d(data2)
data3 = sw_model(data2)

# Plot the result
fig, ax = plt.subplots()
data2.visualize(ax)
data3.visualize(ax)
plt.show()
```
# References
>1. Worthey G，Faber S M，Gonzalez J Jesus，et al. The Astrophysical Journal Supplement Series，94(2)：687.
> 2. Pan, J. C., Wang, X. X., Wei, P., & et al. (2012). An Automatic Fitting Method for Stellar Continuum Based on Statistical Window [J]. Spectroscopy and Spectral Analysis, 32(08), 2260 - 2263.
