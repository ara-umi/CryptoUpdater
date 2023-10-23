# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: araumi
# Email: 532990165@qq.com
# DateTime: 2023/10/23 下午7:05

import asyncio
from multiprocessing import Queue

from ..downloader import IDownloaderProcess
from ...config import BinanceFuturesUMConfig
from ...instance.data import BinanceFuturesUMData
from ...logger import LoggerFactory
from ...service.connector import AsyncPgConnector
from ...service.main import BinanceFuturesUMService


class BinanceFuturesUMDownloaderProcess(IDownloaderProcess):

    def __init__(
            self,
            result_queue: Queue,
    ):
        super().__init__()

        self.config = BinanceFuturesUMConfig()
        self.logger = LoggerFactory(config=self.config).create_logger()

        self.result_queue = result_queue

    async def download(self, data: BinanceFuturesUMData):
        """
        展示的逻辑也嵌套在这里
        """
        if data.succeed:
            connector = AsyncPgConnector(config=self.config)
            service = BinanceFuturesUMService(connector=connector, logger=self.logger)

            await service.insert_kline_many(
                symbol=data.symbol,
                timeframe=data.timeframe,
                klines=data.klines
            )

            await connector.release()
        else:
            # 可以做展示或记录
            pass

    async def main(self):
        while True:
            if self.result_queue.empty():
                await asyncio.sleep(0.1)
            else:
                data = self.result_queue.get()
                asyncio.create_task(self.download(data=data))


if __name__ == "__main__":
    pass
