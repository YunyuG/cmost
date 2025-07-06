import unittest
import aiohttp.http_exceptions
import numpy
from pathlib import Path
import asyncio
import aiohttp
import cmost as cst

class Test_download(unittest.TestCase):
    def test_download_file(self):
        obsids_list = [101001, 101002, 101005]
        # with self.assertRaises(aiohttp.http_exceptions.HttpProcessingError):
        cst.download_fits(obsids_list=obsids_list
                            ,dr_version="9"
                            ,sub_version="2.0"
                            ,save_dir='./tests'
                            ,TOKEN="Fb925bed8c2")
            
    # def test_download_MidFits_file(self):
    #     obsids_list = [588902005,588902003]
    #     cst.download_fits(obsids_list=obsids_list
    #                       ,dr_version=13
    #                       ,sub_version=0
    #                       ,save_dir='./tests'
    #                       ,TOKEN="Fb925bed8c2"
    #                       ,is_med=True)
            
if __name__ == '__main__':
    unittest.main()