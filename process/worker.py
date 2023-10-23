# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: araumi
# Email: 532990165@qq.com
# DateTime: 2023/8/25 下午10:45

import asyncio
from abc import abstractmethod, ABCMeta
from multiprocessing import Process
from multiprocessing import Queue

from ..config import IConfig
from ..instance.data import IData
from ..logger import LoggerFactory


class IWorkerProcess(Process, metaclass=ABCMeta):

    @abstractmethod
    def __init__(
            self,
            job_queue: Queue,
            result_queue: Queue,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.config = IConfig()
        self.logger = LoggerFactory(config=self.config).create_logger()

        self.job_queue = job_queue
        self.result_queue = result_queue

    def run(self) -> None:
        asyncio.new_event_loop().run_until_complete(self.main())

    @abstractmethod
    async def update(self, *args, **kwargs):
        """
        使用KlineUpdater获取结果处理后的Data对象
        并放入result_queue
        """
        ...

    async def queue_get(self, queue: Queue) -> IData:
        if queue.empty():
            await asyncio.sleep(0.1)
        else:
            return queue.get()

    @abstractmethod
    async def main(self):
        """
        循环从job_queue中获取Data对象
        并交给update方法处理
        """
        ...


if __name__ == "__main__":
    pass
