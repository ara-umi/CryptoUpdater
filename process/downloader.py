# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: araumi
# Email: 532990165@qq.com
# DateTime: 2023/10/23 下午7:02

import asyncio
from abc import abstractmethod, ABCMeta
from multiprocessing import Process
from multiprocessing import Queue

from ..instance.data import IData
from ..logger import LoggerFactory


class IDownloaderProcess(Process, metaclass=ABCMeta):

    def run(self) -> None:
        asyncio.new_event_loop().run_until_complete(self.main())

    @abstractmethod
    async def download(self, data: IData):
        ...

    @abstractmethod
    async def main(self):
        ...


class TestDownloaderProcess(IDownloaderProcess):

    def __init__(
            self,
            result_queue: Queue
    ):
        super().__init__()

        from ..config import BinanceFuturesUMConfig
        self.config = BinanceFuturesUMConfig()
        self.logger = LoggerFactory(config=self.config).create_logger()
        self.result_queue = result_queue

    async def download(self, data: IData):
        print(data)
        return data

    async def main(self):
        while True:
            if self.result_queue.empty():
                await asyncio.sleep(0.1)
            else:
                data = self.result_queue.get()
                asyncio.create_task(self.download(data=data))


if __name__ == "__main__":
    pass
