# !/usr/bin/env python3
# Copyright (C) 2025 YunyuG

from __future__ import annotations

import asyncio
import aiofiles
import aiohttp
import aiohttp.http_exceptions

from pathlib import Path
from functools import wraps

__all__ = ['download_fits']

import asyncio
from functools import wraps

def asyncio_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        
        if loop and loop.is_running():
            # create_task() in the running loop
            return loop.create_task(func(*args, **kwargs))
        else:
            # run_until_complete() outside the running loop
            return asyncio.run(func(*args, **kwargs))
    
    return wrapper


class FitsDownloader:
    def __init__(self,dr_number:int
                    ,*
                    ,TOKEN:str
                    ,is_med:bool
                    ,sem_number:int
                    ,max_retrys:int
                    ,save_dir:str):
        
        self.dr_number = dr_number
        self.TOKEN = TOKEN
        self.is_med = is_med
        self.max_retrys = max_retrys
        self.save_dir = save_dir
        self.sem = asyncio.Semaphore(sem_number)
        self.band()

    
    def band(self):
        self.task_completed = 0
        self.task_total = 0


    def make_url(self,
            obsid:int
        )->str:
        """
        The construction of the download link refers to the official LAMOST tool `pylamost`.
            https://github.com/fandongwei/pylamost

        """
        if self.dr_number >= 6:
            root_url = f"https://www.lamost.org/dr{self.dr_number}/{'med' if self.is_med else ''}spectrum/fits"
        else:
            root_url = f"http://dr{self.dr_number}.lamost.org/{'med' if self.is_med else ''}spectrum/fits"

        url = "{0}/{1}{2}".format(root_url,obsid,f"?token={self.TOKEN}" if self.TOKEN else "")
        return url

    

    async def download_single_fits(self,
            download_url:str
            ,session:aiohttp.ClientSession
        )->None:
            
            for retry in range(self.max_retrys):
                try:
                    async with self.sem:
                        async with session.get(download_url) as response:
                            fits_name = response.headers["Content-Disposition"].split("=")[1]
                            fits_path = Path(self.save_dir).joinpath(fits_name)
                            async with aiofiles.open(fits_path,"wb+") as f:
                                await f.write(await response.read())
                            
                            self.task_completed += 1
                            print(f"<{fits_name} has dowloaded,current progress:{self.task_completed}/{self.task_total}>")
                            return
                        
                except Exception as e:
                    await asyncio.sleep(1 + 0.5 * retry)
                    if retry == self.max_retrys - 1:
                         raise aiohttp.http_exceptions.HttpProcessingError(code=500
                                                                           ,message="Download failed") from e
           
    
    @asyncio_decorator
    async def async_download_fits(self,
            obsid_list:list | int
    ):       
        tasks = []
        async with aiohttp.ClientSession() as session:
            for obsid in obsid_list:
                download_url = self.make_url(obsid)
                task = self.download_single_fits(download_url=download_url
                                        ,session=session)
                tasks.append(task)
            self.task_total = len(tasks)
            
            for future in asyncio.as_completed(tasks):
                await future



def download_fits(obsids_lists:list | int
                  ,dr_number:int
                  ,TOKEN:str = None
                  ,is_med:bool = False
                  ,sem_number:int = 5
                  ,max_retrys:int = 3
                  ,save_dir:str = None):
    
    if save_dir is None:
        save_dir = f"./dr{dr_number}"
        Path(save_dir).mkdir(exist_ok=True)
    else:
        save_dir = save_dir
        if save_dir=="./":
            pass
        else:
            Path(save_dir).mkdir(exist_ok=True)
    
    fits_downloader = FitsDownloader(dr_number=dr_number
                                     ,TOKEN=TOKEN
                                     ,is_med=is_med
                                     ,sem_number=sem_number
                                     ,max_retrys=max_retrys
                                     ,save_dir=save_dir)
    
    fits_downloader.async_download_fits(obsid_list=obsids_lists)