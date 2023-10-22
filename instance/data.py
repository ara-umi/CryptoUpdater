# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: araumi
# Email: 532990165@qq.com
# DateTime: 2023/8/25 上午12:32

from collections import OrderedDict
from typing import Optional

from attrs import define, field

from .error_info import ErrorInfo
from .kline import Kline


@define
class Data(object):
    symbol = field(type=str, repr=True)
    timeframe = field(type=str, repr=True)
    exchange = field(type=str, repr=True)
    type = field(type=str, repr=True)
    limit = field(type=int, repr=True)

    succeed = field(type=bool, repr=True, default=False)
    error = field(type=Optional[ErrorInfo], repr=True, default=None)
    klines = field(type=Optional[list[Kline]], repr=False, factory=list)

    @symbol.validator
    def validate_symbol(self, attribute, value):
        if value != value.upper():
            raise ValueError("Invalid symbol. Must be in uppercase.")

    @timeframe.validator
    def validate_timeframe(self, attribute, value):
        valid_timeframes = ["1M", "5M", "15M", "30M", "1H", "2H", "4H", "1D", "1W"]
        if value not in valid_timeframes:
            raise ValueError(f"Invalid timeframe. Must be one of {valid_timeframes}.")

    @exchange.validator
    def validate_exchange(self, attribute, value):
        valid_exchanges = ["binance", "okex"]
        if value not in valid_exchanges:
            raise ValueError(f"Invalid exchange. Must be one of {valid_exchanges}.")

    @type.validator
    def validate_type(self, attribute, value):
        valid_types = ["spot", "futures_um", "futures_cm"]
        if value not in valid_types:
            raise ValueError(f"Invalid type. Must be one of {valid_types}.")

    @limit.validator
    def validate_limit(self, attribute, value):
        if value <= 0:
            raise ValueError(f"Invalid limit. Must be greater than 0.")

    def set_error(self, type_: str, message: str, traceback: str):
        self.succeed = False
        self.error = ErrorInfo(type=type_, message=message, traceback=traceback)

    def set_klines(self, klines: list[Kline]):
        self.succeed = True
        self.klines = klines


@define
class BinanceData(Data):
    """
    在考虑是不是需要分开做，做BinanceData和OkexData
    """

    url_done_dict = field(type=dict, repr=False, factory=OrderedDict)

    def set_url(self, url: str):
        self.url_done_dict[url] = False

    def set_url_done(self, url: str):
        """
        这里就不用异常处理了
        """
        self.url_done_dict[url] = True


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
    ) -> Data:
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
