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

def make_url(
        obsid:int
        ,dr_number:int
        ,*
        ,TOKEN:str
        ,is_med:bool
    )->str:
    """
    The construction of the download link refers to the official LAMOST tool `pylamost`.
        https://github.com/fandongwei/pylamost

    """
    if dr_number >= 6:
        root_url = f"https://www.lamost.org/dr{dr_number}/{'med' if is_med else ''}spectrum/fits"
    else:
        root_url = f"http://dr{dr_number}.lamost.org/{'med' if is_med else ''}spectrum/fits"

    url = "{0}/{1}{2}".format(root_url,obsid,f"?token={TOKEN}" if TOKEN else "")
    return url

    

async def download_single_fits(
        download_url:str
        ,session:aiohttp.ClientSession
        ,semaphore:asyncio.Semaphore
        ,max_retrys:int
        ,save_dir:str
    )->None:
        
        for retry in range(max_retrys):
            try:
                async with semaphore:
                    async with session.get(download_url) as response:
                        # get filename from response header
                        fits_name = response.headers["Content-Disposition"].split("=")[1]
                        # make save path
                        fits_path = Path(save_dir).joinpath(fits_name)
                        # async download
                        async with aiofiles.open(fits_path,"wb+") as f:
                            await f.write(await response.read())

                        # print(f"{fits_name} has dowloaded")
                        return fits_name
            except (aiohttp.ClientError,asyncio.TimeoutError) as e:
                await asyncio.sleep(1 + 0.5 * retry)
            
            except Exception as e:
                raise e
        raise aiohttp.http_exceptions.HttpProcessingError(code=500,message="Download failed") from e

def asyncio_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        if loop and loop.is_running():
            return asyncio.create_task(func(*args, **kwargs))
        else:
            return asyncio.run(func(*args, **kwargs))
    return wrapper

@asyncio_decorator
async def download_fits(
        obsid_list:list | int
        ,dr_number:int
        ,*
        ,TOKEN:str = None
        ,is_med:bool = False
        ,max_retrys:int = 3
        ,save_dir:str = None
        ,sem_number:int = 5
):
    if isinstance(obsid_list,int):
            obsid_list = [obsid_list]

    if save_dir is None:
        save_dir = f"./dr{dr_number}"
        Path(save_dir).mkdir(exist_ok=True)
    elif save_dir=="./":
        pass
    else:
        Path(save_dir).mkdir(exist_ok=True)

    async with aiohttp.ClientSession() as session:
        iter =gen_asynciter(obsid_list
                            ,dr_number
                            ,TOKEN=TOKEN
                            ,is_med=is_med
                            ,max_retrys=max_retrys
                            ,save_dir=save_dir
                            ,sem_number=sem_number)
        async for fits_name in iter:
            print(f"{fits_name} has dowloaded")
        

async def gen_asynciter(
        obsid_list:list
        ,dr_number:int
        ,*
        ,TOKEN:str = None
        ,is_med:bool = False
        ,max_retrys:int = 3
        ,save_dir:str = None
        ,sem_number:int = 5
): 
    
    sem = asyncio.Semaphore(sem_number)
    tasks = []
    async with aiohttp.ClientSession() as session:
        for obsid in obsid_list:
            download_url = make_url(obsid,dr_number,TOKEN=TOKEN,is_med=is_med)
            task = download_single_fits(download_url=download_url
                                    ,session=session,semaphore=sem
                                ,max_retrys=max_retrys,save_dir=save_dir)
            tasks.append(task)
        
        for future in asyncio.as_completed(tasks):
            fits_name = await future
            yield fits_name