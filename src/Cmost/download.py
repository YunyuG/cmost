import asyncio
import aiofiles
import aiohttp
from pathlib import Path
from .utils import asyncio_decorator

__all__ = ['download_fits']

def __make_url(
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

    return f"{root_url}/{obsid}?{"token={TOKEN}" if TOKEN else ""}"

    

async def __download_single_fits(
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
        下载单个fits文件
        :param obsid: 目标obsid
        :param dataset_number: 数据集编号
        :param TOKEN: lamost数据库访问密钥

        下载链接的构建参考于Lamost官方光谱处理工具`pylamost`,链接如下：
            https://github.com/fandongwei/pylamost

        """
        download_url = __make_url(
                        obsid=obsid
                        ,dr_number=dr_number
                        ,version=version
                        ,TOKEN=TOKEN
                        ,is_mid=is_mid
        )
        
        # 异步请求
        # 设置重试次数
        retry_ = 0
        while retry_ <= max_retrys:
            try:
                async with sem:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(download_url) as response:
                            # 从响应头中获取文件名
                            fits_name = response.headers["Content-Disposition"].split("=")[1]
                            # 构造文件路径
                            fits_path = Path(save_dir).joinpath(fits_name)
                            # 异步下载
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
    # 构建任务列表
    if isinstance(obsid_list,int):
        obsid_list = [obsid_list]

    if save_dir is None:
        save_dir = f"./dr{dr_number}"
        Path(save_dir).mkdir(exist_ok=True)

    # 构建信号量
    sem = asyncio.Semaphore(sem_number)
    tasks = asyncio.gather(*[__download_single_fits(obsid
                                                   ,dr_number
                                                   ,version
                                                   ,TOKEN=TOKEN
                                                   ,is_mid=is_mid
                                                   ,max_retrys=max_retrys
                                                   ,save_dir=save_dir
                                                   ,sem=sem) for obsid in obsid_list])
    await tasks