# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: araumi
# Email: 532990165@qq.com
# DateTime: 2023/10/23 下午7:02

import asyncio
from abc import abstractmethod, ABCMeta
from multiprocessing import Process
from multiprocessing import Queue

from ..config import IConfig
from ..instance.data import IData
from ..logger import LoggerFactory


class IDownloaderProcess(Process, metaclass=ABCMeta):

    @abstractmethod
    def __init__(
            self,
            result_queue: Queue,
            *args,
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.config = IConfig()
        self.logger = LoggerFactory(config=self.config).create_logger()

        self.result_queue = result_queue

    def run(self) -> None:
        asyncio.new_event_loop().run_until_complete(self.main())

    @abstractmethod
    async def download(self, data: IData):
        ...

    async def main(self):
        while True:
            if self.result_queue.empty():
                await asyncio.sleep(0.1)
            else:
                data = self.result_queue.get()
                asyncio.create_task(self.download(data=data))


class TestUpdateDownloaderProcess(IDownloaderProcess):

    def __init__(
            self,
            result_queue: Queue,
            *args,
            **kwargs
    ):
        super().__init__(result_queue=result_queue, *args, **kwargs)

    async def download(self, data: IData):
        return data


if __name__ == "__main__":
    pass
