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


class FitsDownloader:
    def __init__(self,dr_number:int
                    ,*
                    ,TOKEN:str
                    ,is_med:bool
                    ,sem_number:int = 5
                    ,max_retrys:int = 3
                    ,save_dir:str = None):
        
        self.dr_number = dr_number
        self.TOKEN = TOKEN
        self.is_med = is_med
        self.max_retrys = max_retrys
        self.sem = asyncio.Semaphore(sem_number)


        if save_dir is None:
            self.save_dir = f"./dr{self.dr_number}"
            Path(self.save_dir).mkdir(exist_ok=True)
        else:
            self.save_dir = save_dir
            if save_dir=="./":
                pass
            else:
                Path(self.save_dir).mkdir(exist_ok=True)


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

                            # print(f"{fits_name} has dowloaded")
                            return fits_name
                except (aiohttp.ClientError,asyncio.TimeoutError) as e:
                    await asyncio.sleep(1 + 0.5 * retry)
                
                except Exception as e:
                    raise e
            raise aiohttp.http_exceptions.HttpProcessingError(code=500,message="Download failed") from e
    
    
    async def async_download_fits(self,
            obsid_list:list | int
    ):
        if isinstance(obsid_list,int):
                obsid_list = [obsid_list]
            
        tasks = []
        async with aiohttp.ClientSession() as session:
            for obsid in obsid_list:
                download_url = self.make_url(obsid)
                task = self.download_single_fits(download_url=download_url
                                        ,session=session)
                tasks.append(task)
            
            for future in asyncio.as_completed(tasks):
                fits_name = await future
                yield fits_name