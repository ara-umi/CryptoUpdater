# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: araumi
# Email: 532990165@qq.com
# DateTime: 2023/6/22 上午2:37

import asyncio
import datetime
import re
from functools import wraps

import aiohttp
import pytz

from ...config import BinanceFuturesUMConfig
from ...logger import LoggerType


class TimeoutWrapper(object):
    def __init__(self, timeout_second: float = 3):
        self.timeout_second = timeout_second

    def __call__(self, function):
        @wraps(function)
        async def async_wrapped(obj_self, *args, **kwargs):
            return await asyncio.wait_for(function(obj_self, *args, **kwargs), timeout=self.timeout_second)

        return async_wrapped


class RetryWrapper(object):
    def __init__(self, max_tries: int = 99, retry_sleep_second: float = 1):
        self.max_tries = max_tries
        self.retry_sleep_second = retry_sleep_second

    def __call__(self, function):

        @wraps(function)
        async def async_wrapped(obj_self, *args, **kwargs):
            tries = 1
            while tries <= self.max_tries:
                try:
                    return await function(obj_self, *args, **kwargs)
                except aiohttp.ClientError as e:
                    # 网络异常
                    obj_self.logger.debug(f"ClientError: {str(e)}, Tries: {tries}")
                except asyncio.exceptions.TimeoutError as e:
                    # 网络超时
                    obj_self.logger.debug(f"TimeoutError: {str(e)}, Tries: {tries}")
                finally:
                    tries += 1
                    await asyncio.sleep(self.retry_sleep_second)
            else:
                obj_self.logger.critical("Reach Max Tries During Request Symbol List")
                raise TimeoutError("Reach Max Tries During Request Symbol List")

        return async_wrapped


class BinanceFuturesUMSymbolListUpdater(object):
    """
    这里其实有两种选择
    第一种就是选择exchangeInfo，从交易对里获取
    第二种就是选择price，从有现价的标的中获取
    偷懒都使用第二种，问题出现再说
    理论上有现价的标的是一定可以交易的
    """

    def __init__(self, config: BinanceFuturesUMConfig, logger: LoggerType):
        self.config = config
        self.logger = logger

    def check_time(self, timestamp_ms: int) -> bool:
        """
        需要最新价格的更新时间在30分钟内
        讲道理，还真有傻逼币已经下架了还出现在接口里的，比如COCOSUSDT
        binance的人是真够懒的
        """
        allowed_interval_ms = 30 * 60 * 1e3

        if timestamp_ms + allowed_interval_ms > int(datetime.datetime.now(tz=pytz.UTC).timestamp() * 1e3):
            return True
        else:
            return False

    def filter(self, symbol: str) -> bool:
        # 这里沿用的是回测中的正则，理论上只做USDT，且不做1000开头的垃圾币，不做掉期合约（掉期合约是结尾有数字）
        pattern = "^(?!1000)[0-9A-Z]+USDT$"
        obj = re.compile(pattern)
        return bool(obj.match(symbol))

    @RetryWrapper()
    @TimeoutWrapper()
    async def _request(self) -> list[str]:
        url = "https://fapi.binance.com/fapi/v1/ticker/price"
        symbol_list = []

        async with aiohttp.request(method="GET", url=url, proxy=self.config.proxy) as response:
            # 格式为：[{'symbol': 'BTCUSDT', 'price': '0.2394000', 'time': 1687374962157}, ...]
            price_dict = await response.json()

            for item in price_dict:
                symbol = item["symbol"]
                timestamp_ms = item["time"]

                if not self.filter(symbol=symbol):
                    continue

                if not self.check_time(timestamp_ms=timestamp_ms):
                    # self.logger.warning(f"Check time failed: Symbol: {symbol}\tTimestamp: {timestamp_ms}")
                    continue

                symbol_list.append(symbol)

        return symbol_list

    async def __call__(self) -> list[str]:
        self.logger.info(f"Request Binance Futures UM Symbol List")
        symbol_list = await self._request()
        self.logger.success(f"Request Binance Futures UM Symbol List, Length: {len(symbol_list)}")
        return symbol_list


if __name__ == "__main__":
    pass
