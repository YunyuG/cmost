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
    def __init__(self,dr_version:str
                    ,sub_version:str
                    ,*
                    ,is_dev:bool
                    ,TOKEN:str
                    ,is_med:bool
                    ,sem_number:int
                    ,max_retrys:int
                    ,save_dir:str):
        
        self.dr_version = dr_version
        self.sub_version = sub_version
        self.is_dev = is_dev
        self.TOKEN = TOKEN if TOKEN else ""
        self.is_med = is_med
        self.max_retrys = max_retrys
        self.save_dir = save_dir
        self.sem = asyncio.Semaphore(sem_number)
        self.band()

    
    def band(self):
        self.task_completed = 0
        self.task_total = 0
        """
        The construction of the download link refers to the official LAMOST tool `pylamost`.
            https://github.com/fandongwei/pylamost

        """
        resolution = 'mrs' if self.is_med else 'lrs'
        base_url = 'https://www2.lamost.org/openapi' if self.is_dev else "https://www.lamost.org/openapi"
        url = f"{base_url}/{self.dr_version}/{self.sub_version}/{resolution}/spectrum/fits"
        self.url = url
    

    async def download_single_fits(self,
            obsid:int
            ,session:aiohttp.ClientSession
        )->None:
            
            for retry in range(self.max_retrys):
                try:
                    async with self.sem:
                        async with session.get(self.url,params={"obsid":obsid,"token":self.TOKEN}) as response:
                            fits_name = response.headers["Content-Disposition"].split("=")[1]
                            fits_path = Path(self.save_dir).joinpath(fits_name)
                            async with aiofiles.open(fits_path,"wb+") as f:
                                # 8192 is the default chunk size
                                async for chunk in response.content.iter_chunked(8192):
                                    if chunk:
                                        await f.write(chunk)
                            
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
            obsids_list:list[str]
    ):       
        tasks = []
        async with aiohttp.ClientSession() as session:
            for obsid in obsids_list:
                obsid = str(obsid)
                task = self.download_single_fits(obsid=obsid
                                            ,session=session)
                tasks.append(task)
            self.task_total = len(tasks)
            
            for future in asyncio.as_completed(tasks):
                await future



def download_fits(obsids_list:list[str]
                  ,dr_version:str
                  ,sub_version:str
                  ,is_dev:bool = False
                  ,TOKEN:str = None
                  ,is_med:bool = False
                  ,sem_number:int = 5
                  ,max_retrys:int = 3
                  ,save_dir:str = None):
    
    dr_version = f"dr{dr_version}" if "dr" not in dr_version else dr_version
    sub_version = f"v{sub_version}" if "v" not in sub_version else sub_version
    
    if save_dir is None:
        save_dir = f"./{dr_version}_{sub_version}"
        Path(save_dir).mkdir(exist_ok=True)
    else:
        save_dir = save_dir
        if save_dir=="./":
            pass
        else:
            Path(save_dir).mkdir(exist_ok=True)
    
    fits_downloader = FitsDownloader(dr_version=dr_version
                                     ,sub_version=sub_version
                                     ,is_dev=is_dev
                                     ,TOKEN=TOKEN
                                     ,is_med=is_med
                                     ,sem_number=sem_number
                                     ,max_retrys=max_retrys
                                     ,save_dir=save_dir)
    
    fits_downloader.async_download_fits(obsids_list=obsids_list)