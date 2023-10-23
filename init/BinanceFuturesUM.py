# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: araumi
# Email: 532990165@qq.com
# DateTime: 2023/10/23 下午9:14

import asyncio
import random

from ..config import BinanceFuturesUMConfig
from ..instance.data import BinanceFuturesUMData
from ..instance.semaphore import MySemaphore
from ..instance.session import AiohttpClientSession
from ..logger import LoggerFactory
from ..service.connector import AsyncPgConnector, AsyncPgPoolConnector
from ..service.main import BinanceFuturesUMService
from ..updater.BinanceFuturesUM.kline import BinanceFuturesUMKlineUpdater
from ..updater.BinanceFuturesUM.symbol_list import BinanceFuturesUMSymbolListUpdater


class BinanceFuturesUMInit(object):
    limit: dict[str, int] = {
        "1M": 900,
        "30M": 900,
        "1H": 900,
        "4H": 900,
        "1D": 900
    }

    async def _init_symbol(self):
        """
        初始化symbol表
        """
        config = BinanceFuturesUMConfig()
        logger = LoggerFactory(config=config).create_logger()

        connector = AsyncPgConnector(config=config)
        service = BinanceFuturesUMService(connector=connector, logger=logger)

        # 初始化symbol表
        symbols: list[str] = await BinanceFuturesUMSymbolListUpdater(
            config=config,
            logger=logger
        )()
        await service.insert_symbol_many(symbols=symbols)
        await connector.release()

    async def _init_kline(self):
        config = BinanceFuturesUMConfig()
        connector = AsyncPgPoolConnector(config=config)
        logger = LoggerFactory(config=config).create_logger()
        service = BinanceFuturesUMService(connector=connector, logger=logger)

        timeframe_list: list[str] = ["1M", "30M", "1H", "4H", "1D"]
        data_list: list[BinanceFuturesUMData] = []
        for timeframe in timeframe_list:
            for symbol in await service.select_symbol(is_deleted=False):
                data: BinanceFuturesUMData = BinanceFuturesUMData()
                data.symbol = symbol
                data.timeframe = timeframe
                data.limit = self.limit.get(timeframe, 0)
                data_list.append(data)

        # 这里需要手动控制并发数
        semaphore = MySemaphore(20, config.semaphore_sleep_seconds)

        async def update(
                _updater: BinanceFuturesUMKlineUpdater,
                _data: BinanceFuturesUMData,
                _service: BinanceFuturesUMService
        ):
            async with semaphore:
                _data = await _updater(data=_data)
                await service.insert_kline_many(symbol=_data.symbol, timeframe=_data.timeframe, klines=_data.klines)
                logger.success(f"Init {_data} Success")

        async with AiohttpClientSession() as session:
            updater = BinanceFuturesUMKlineUpdater(
                config=config,
                logger=logger,
                session=session
            )
            await asyncio.gather(
                *[
                    update(
                        _updater=updater,
                        _data=data,
                        _service=service
                    )
                    for data in data_list
                ]
            )

        await connector.release()

    async def _init_assert(self):
        config = BinanceFuturesUMConfig()
        logger = LoggerFactory(config=config).create_logger()

        connector = AsyncPgConnector(config=config)
        service = BinanceFuturesUMService(connector=connector, logger=logger)

        # 读取symbol表
        symbols: list[str] = await service.select_symbol()

        # 随机查询symbol，主要是检查是否插入成功，能读出来
        for item in random.choices(symbols, k=3):
            print(item)
            for obj in item:
                print(obj, type(obj))

        # 随机查询kline，主要是检查是否插入成功，读出来长度和init的时候一致（接口数据不足的情况下会不一致）
        timeframe_list = ["1M", "30M", "1H", "4H", "1D"]
        for symbol in random.choices(symbols, k=3):
            timeframe = random.choice(timeframe_list)
            limit = random.randint(1, 100)
            klines = await service.select_kline(symbol=symbol, timeframe=timeframe, limit=limit)
            print(f"Test select {symbol}-{timeframe}-{limit}")
            print(klines[:5])
            recent_kline = klines[-1]
            print(recent_kline)
            print(recent_kline.open_time, type(recent_kline.open_time))
            print(recent_kline.open, type(recent_kline.open))
            print("=" * 50)

        await connector.release()

    def init_symbol(self):
        asyncio.run(self._init_symbol())

    def init_kline(self):
        asyncio.run(self._init_kline())

    def init_assert(self):
        asyncio.run(self._init_assert())


if __name__ == "__main__":
    pass
