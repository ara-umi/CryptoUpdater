# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: araumi
# Email: 532990165@qq.com
# DateTime: 2023/10/23 下午7:05

from multiprocessing import Queue

from ..downloader import IDownloaderProcess
from ...config import BinanceFuturesUMConfig
from ...instance.data import BinanceFuturesUMData
from ...logger import LoggerFactory
from ...service.connector import AsyncPgPoolConnector
from ...service.main import BinanceFuturesUMService


class BinanceFuturesUMDownloaderProcess(IDownloaderProcess):

    def __init__(
            self,
            result_queue: Queue,
    ):
        self.config = BinanceFuturesUMConfig()
        self.logger = LoggerFactory(config=self.config).create_logger()
        self.connector = AsyncPgPoolConnector(config=self.config)
        self.service = BinanceFuturesUMService(connector=self.connector, logger=self.logger)

        self.result_queue = result_queue

    async def download(self, data: BinanceFuturesUMData):
        """
        展示的逻辑也嵌套在这里
        """
        if data.succeed:
            await self.service.insert_kline_many(
                symbol=data.symbol,
                timeframe=data.timeframe,
                klines=data.klines
            )
        else:
            pass


if __name__ == "__main__":
    pass
