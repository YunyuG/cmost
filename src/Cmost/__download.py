import asyncio
import aiofiles
import aiohttp
import aiohttp.http_exceptions
from pathlib import Path
from .utils import asyncio_decorator

__all__ = ['download_fits']

def make_url(
        obsid:int
        ,dr_number:int
        ,version:int
        ,*
        ,TOKEN:str
        ,is_mid:bool
    )->str:
    if dr_number >= 6:
        root_url = f"https://www.lamost.org/dr{dr_number}/{'mid' if is_mid else ''}spectrum/fits"
    else:
        root_url = f"http://dr{dr_number}.lamost.org/{'mid' if is_mid else ''}spectrum/fits"
    
    if version:
        root_url = f"{root_url}/v{version}"

    return f"{root_url}/{obsid}{f"?token={TOKEN}" if TOKEN else ""}"

    

async def download_single_fits(
        obsid:int
        ,dr_number:int
        ,version:int
        ,*
        ,TOKEN:str
        ,is_mid:bool
        ,max_retrys:int
        ,save_dir:str
        ,sem
    )->None:
        """
        The construction of the download link refers to the official LAMOST tool `pylamost`.
            https://github.com/fandongwei/pylamost

        """
        download_url = make_url(
                        obsid=obsid
                        ,dr_number=dr_number
                        ,version=version
                        ,TOKEN=TOKEN
                        ,is_mid=is_mid
        )
        retry_ = 0
        while retry_ <= max_retrys:
            try:
                async with sem:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(download_url) as response:
                            # get filename from response header
                            fits_name = response.headers["Content-Disposition"].split("=")[1]
                            # make save path
                            fits_path = Path(save_dir).joinpath(fits_name)
                            # async download
                            async with aiofiles.open(fits_path,"wb+") as f:
                                await f.write(await response.read())

                            print(f"{fits_name} has dowloaded")
                            return None
            except Exception as e:
                retry_ += 1
            
            finally:
                if max_retrys == retry_:
                    raise aiohttp.http_exceptions.HttpBadRequest(f"download {obsid} failed,please check your obsid or TOKEN or internet,if all is ready,please wait for a moment")


@asyncio_decorator
async def download_fits(
        obsid_list:list | int
        ,dr_number:int
        ,version:int = None
        ,*
        ,TOKEN:str = None
        ,is_mid:bool = False
        ,max_retrys:int = 3
        ,save_dir:str = None
        ,sem_number:int = 5
)->None:
    """
    Asynchronous download of the FITS files.

    :param obsid_list: `OBSID` of the target FITS file.
    :param dr_number: LAMOST DR number.
    :param version: Datasets version. Defaults to None.
    :param TOKEN: The download key provided by the LAMOST Information Center (required only for non-open data; as of June 2025, required for DR11+). Defaults to None.
    :param is_mid: Indicates whether to download medium-resolution spectra (downloads low-resolution spectra by default). Defaults to False.
    :param max_retrys: The maximum number of attempts (throws an exception if exceeded). Defaults to 3.
    :param save_dir: Saved directories. Defaults to `./dr{dr_number}`.
    :param sem_number: The maximum number of concurrent throttling. Defaults to 5.

    **examples**
    >>> import Cmost as cst
    >>> obsid_lists = [1247301001,1247301004,1247301005,1247301006] # target obsid
    >>> TOKEN = '********' # your token
    >>> DR_NUMBER = 13
    >>> cst.download_fits(obsid_lists,dr_number=DR_NUMBER,TOKEN=TOKEN)
    """
    # 构建任务列表
    if isinstance(obsid_list,int):
        obsid_list = [obsid_list]

    if save_dir is None:
        save_dir = f"./dr{dr_number}"
        Path(save_dir).mkdir(exist_ok=True)
    elif save_dir=="./":
        pass
    else:
        Path(save_dir).mkdir(exist_ok=True)

    # 构建信号量
    sem = asyncio.Semaphore(sem_number)
    tasks = asyncio.gather(*[download_single_fits(obsid
                                                   ,dr_number
                                                   ,version
                                                   ,TOKEN=TOKEN
                                                   ,is_mid=is_mid
                                                   ,max_retrys=max_retrys
                                                   ,save_dir=save_dir
                                                   ,sem=sem) for obsid in obsid_list])
    await tasks