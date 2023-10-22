# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: araumi
# Email: 532990165@qq.com
# DateTime: 2023/6/27 上午3:44

from abc import ABCMeta, abstractmethod

from asyncpg import Record

from .connector.interface import IConnector
from ..instance.kline import Kline


class IService(metaclass=ABCMeta):

    def __init__(self, connector: IConnector):
        self.connector = connector

    @abstractmethod
    async def insert_symbol_many(self, symbols: list[str]):
        """
        插入symbol表
        支持同类型批量插入
        """
        ...

    @abstractmethod
    async def select_symbols(
            self,
            is_deleted: bool = False
    ) -> list[Record]:
        """
        查询symbol表
        """
        ...

    @abstractmethod
    async def delete_symbol(self, symbol: str):
        """
        币种下架会调用，删除symbol表中的symbol
        目前不使用任何外键，所以不需要级联删除
        """
        ...

    @abstractmethod
    async def insert_kline_many(self, symbol: str, interval: int, klines: list[Kline]):
        """
        插入kline表
        支持批量插入
        """
        ...

    @abstractmethod
    async def select_kline(self, symbol: str, interval: int, limit: int = None) -> list[Record]:
        """
        查询kline表
        """
        ...


if __name__ == "__main__":
    pass
