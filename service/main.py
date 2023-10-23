# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: araumi
# Email: 532990165@qq.com
# DateTime: 2023/8/11 下午9:39

from abc import ABCMeta

from asyncpg import Record

from .base import BaseService
from .connector import IConnector
from ..instance.kline import Kline
from ..instance.mapping import timeframe_interval_dict
from ..logger import LoggerType


class IService(metaclass=ABCMeta):
    """
    使用组合
    其他实现方式还可以通过继承或者适配器
    """

    def __init__(self, connector: IConnector, logger: LoggerType):
        self.service = BaseService(connector=connector)
        self.logger = logger

    async def insert_symbol_many(self, symbols: list[str]):
        returning = await self.service.insert_symbol_many(symbols=symbols)
        self.logger.info(f"Insert {len(returning)} symbols")
        return returning

    async def select_symbol(
            self,
            is_deleted: bool = False
    ) -> list[str]:
        records: list[Record] = await self.service.select_symbols(is_deleted=is_deleted)
        return [record["name"] for record in records]

    async def delete_symbol(self, symbol: str):
        res = await self.service.delete_symbol(symbol=symbol)
        self.logger.info(f"Delete {symbol} from \"symbol\"")
        return res

    async def insert_kline_many(self, symbol: str, timeframe: str, klines: list[Kline]):
        interval = timeframe_interval_dict[timeframe]
        res = await self.service.insert_kline_many(symbol=symbol, interval=interval, klines=klines)
        self.logger.info(f"Insert kline: {symbol}-{timeframe} length: {len(klines)}")
        return res

    async def select_kline(self, symbol: str, timeframe: str, limit: int = None) -> list[Kline]:
        interval = timeframe_interval_dict[timeframe]
        records: list[Record] = await self.service.select_kline(symbol=symbol, interval=interval, limit=limit)
        records.reverse()  # 倒序

        klines: list[Kline] = [
            Kline(
                open_time=record["open_time"],  # 查出来也是datetime，自带本地时区
                open=float(record["open"]),  # 查出来是decimal，做一下类型转换
                high=float(record["high"]),
                low=float(record["low"]),
                close=float(record["close"]),
                volume=float(record["volume"])
            )
            for record in records
        ]

        return klines


class BinanceFuturesUMService(IService):
    pass


if __name__ == "__main__":
    pass
