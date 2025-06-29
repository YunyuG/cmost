import pytest
import numpy
from pathlib import Path
import asyncio
import cmost as cst

class Test_download:



    def test_download_fits(self):
        try:
            asyncio.run(self.download_fits_async())
            cst.download_fits([101001,101002,101005,101007],dr_number=9,save_dir="./")
        except Exception as e:
            pytest.fail(f"download_fits failed: {e}")
        # assert Path("./tests/cache/dr9").exists(),"download_fits failed"
        # assert len(list(Path("./tests/cache/dr9").iterdir()))==4
        
    
    async def download_fits_async(self):
        try:
            await cst.download_fits([101001],dr_number=5,save_dir="./")
        except Exception as e:
            pytest.fail(f"download_fits_async failed: {e}")

        # assert Path("./tests/cache/dr5").exists(),"download_fits failed"
        # assert len(list(Path("./tests/cache/dr5").iterdir()))==1

# @pytest.mark.skip
class Test_read_fits:
    def test_read_fits(self):
        try:
            fits_data1 = cst.read_fits("tests/spec-55859-F5902_sp01-005.fits.gz")
            fits_data2 = cst.read_fits("tests/spec-55859-F5902_sp01-012.fits.gz")
            print(fits_data1)
            header = cst.read_header("tests/spec-55859-F5902_sp01-012.fits.gz")
            fits_data1.minmax()
            fits_data1.align(numpy.arange(3700,9100,2))
            fits_data1.remove_redshift()
            fits_data1.visualize()
            print(fits_data2['Wavelength'])
            print(fits_data2['Flux'])
            print(cst.lick.compute_LickLineIndices(fits_data1))
            model = cst.fitting.SwFitting5d()
            model.fit(fits_data1)
            print(model.transform(fits_data1['Wavelength']))
        except Exception as e:
            pytest.fail(f"read_fits failed: {e}")