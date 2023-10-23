# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: araumi
# Email: 532990165@qq.com
# DateTime: 2023/8/25 上午12:32

from abc import ABCMeta
from typing import Optional

from .error_info import ErrorInfo
from .kline import Kline
from .property import PlaceHolder


class IData(metaclass=ABCMeta):
    symbol: str = PlaceHolder()
    timeframe: str = PlaceHolder()
    limit: int = PlaceHolder()

    def __init__(self):
        self.succeed: bool = False
        self.error: Optional[ErrorInfo] = None
        self.klines: Optional[list[Kline]] = []

    def set_error(self, type_: str, message: str, traceback: str):
        self.succeed = False
        self.error = ErrorInfo(type=type_, message=message, traceback=traceback)

    def set_klines(self, klines: list[Kline]):
        self.succeed = True
        self.klines = klines

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(" \
               f"symbol={self.symbol!r}, " \
               f"timeframe={self.timeframe!r}, " \
               f"limit={self.limit!r}, " \
               f"succeed={self.succeed!r}, " \
               f"error={self.error!r}, " \
               f"klines={len(self.klines)})"


class BinanceData(IData):

    def __init__(self):
        super().__init__()
        self.url_done_dict: dict[str, bool] = {}

    def set_url(self, url: str):
        self.url_done_dict[url] = False

    def set_url_done(self, url: str):
        self.url_done_dict[url] = True


class BinanceFuturesUMData(BinanceData):
    pass



if __name__ == "__main__":
    pass
