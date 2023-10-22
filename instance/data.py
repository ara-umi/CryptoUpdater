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

    succeed: bool = False
    error: Optional[ErrorInfo] = None
    klines: Optional[list[Kline]] = []

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
    url_done_dict: dict[str, bool] = {}

    def set_url(self, url: str):
        self.url_done_dict[url] = False

    def set_url_done(self, url: str):
        self.url_done_dict[url] = True


class BinanceFuturesUMData(BinanceData):
    pass


class DataFactory(object):
    """
    for update
    """

    limit_dict = {
        "binance": {
            "futures_um": {
                "1M": 120,
                "30M": 5,
                "1H": 5,
                "4H": 5,
                "1D": 5
            },
            "spot": {
            }
        },
        "okex": {}
    }

    @classmethod
    def create_data(
            cls,
            symbol: str,
            exchange: str,
            type_: str,
            timeframe: str
    ) -> IData:
        try:
            limit = cls.limit_dict[exchange][type_][timeframe]  # 看需不需要做异常处理
        except KeyError:
            raise ValueError(f"Cannot find update limit, invalid input: {exchange}-{type_}-{timeframe}")

        match (exchange, type_):
            case ("binance", "futures_um"):
                return BinanceData(
                    symbol=symbol,
                    timeframe=timeframe,
                    exchange=exchange,
                    type=type_,
                    limit=limit
                )
            case _:
                raise ValueError(f"Invalid exchange: {exchange} or type: {type_}")


class DataInitFactory(DataFactory):
    limit_dict = {
        "binance": {
            "futures_um": {
                "1M": 900,
                "30M": 900,
                "1H": 900,
                "4H": 900,
                "1D": 900
            },
            "spot": {
            }
        },
        "okex": {}
    }


if __name__ == "__main__":
    pass
