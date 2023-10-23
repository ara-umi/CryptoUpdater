# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: araumi
# Email: 532990165@qq.com
# DateTime: 2023/10/23 下午6:41

import asyncio
from multiprocessing import Queue

from aiohttp import ClientSession

from ..worker import IWorkerProcess
from ...config import BinanceFuturesUMConfig
from ...instance.data import BinanceFuturesUMData
from ...instance.semaphore import MySemaphore
from ...instance.session import AiohttpClientSession
from ...logger import LoggerFactory
from ...updater.BinanceFuturesUM.kline import BinanceFuturesUMKlineUpdater


class BinanceFuturesUMWorkerProcess(IWorkerProcess):

    def __init__(
            self,
            job_queue: Queue,
            result_queue: Queue,
            *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.config = BinanceFuturesUMConfig()
        self.logger = LoggerFactory(config=self.config).create_logger()

        self.job_queue = job_queue
        self.result_queue = result_queue

    def run(self) -> None:
        asyncio.new_event_loop().run_until_complete(self.main())

    async def update(self, data: BinanceFuturesUMData, semaphore: asyncio.Semaphore, session: ClientSession):
        updater = BinanceFuturesUMKlineUpdater(
            config=self.config,
            logger=self.logger,
            session=session
        )
        async with semaphore:
            data = await updater(data=data)
            self.result_queue.put(data)

    async def main(self):
        semaphore = MySemaphore(self.config.semaphore_limit, self.config.semaphore_sleep_seconds)
        session = AiohttpClientSession.create_session()

        # try:
        while True:
            if self.job_queue.empty():
                await asyncio.sleep(0.1)
            else:
                data = self.job_queue.get()
                asyncio.create_task(self.update(data=data, semaphore=semaphore, session=session))

            # data = await asyncio.to_thread(self.job_queue.get)
            # asyncio.create_task(self.update(data=data, semaphore=semaphore, updater_factory=updater_factory))

        # except KeyboardInterrupt:
        #     await AiohttpClientSession.release_session(session)
        #     print("close session")
        #     pass


if __name__ == "__main__":
    pass
