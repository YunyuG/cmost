import unittest
import aiohttp.http_exceptions
import numpy
from pathlib import Path
import asyncio
import aiohttp
import cmost as cst

class Test_download(unittest.TestCase):
    def test_download_file(self):
        obsid_list = [1247301001, 1247301004, 1247301005]
        with self.assertRaises(aiohttp.http_exceptions.HttpProcessingError):
            cst.download_fits(obsids_lists=obsid_list
                              ,dr_number=13
                              ,save_dir='./tests')
            
if __name__ == '__main__':
    unittest.main()