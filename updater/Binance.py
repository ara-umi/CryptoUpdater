# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: araumi
# Email: 532990165@qq.com
# DateTime: 2023/8/25 上午1:16

import asyncio
import itertools
import traceback
import warnings
from abc import abstractmethod
from functools import wraps
from typing import TypeVar, Generic

import aiohttp

from .exception import StatusError, MaxTriesError
from .interface import IKlineUpdater
from ..config import IConfig
from ..instance.data import BinanceData
from ..instance.kline import Kline
from ..logger import LoggerType
from ..tools.dt import timestamp_ms_to_datetime_utc

DataType = TypeVar("DataType", bound=BinanceData)
ConfigType = TypeVar("ConfigType", bound=IConfig)


class CatchWrapper(Generic[DataType]):

    def __call__(self, function):
        @wraps(function)
        async def async_wrapped(obj_self, data: DataType):
            try:
                return await function(obj_self, data=data)

            except (MaxTriesError, StatusError) as e:
                obj_self.logger.error(f"{str(e)}")
                data.set_error(
                    type_=e.__class__.__name__,
                    message=str(e),
                    traceback=traceback.format_exc()
                )
                return data

            except Exception as e:
                warnings.warn(repr(e))
                raise e

        return async_wrapped


class TimeoutWrapper(Generic[DataType]):

    def __call__(self, function):
        @wraps(function)
        async def async_wrapped(obj_self, *args, **kwargs):
            return await asyncio.wait_for(
                function(obj_self, *args, **kwargs),
                timeout=obj_self.config.request_timeout_seconds
            )

        return async_wrapped


class RetryWrapper(Generic[DataType]):
    def __call__(self, function):
        @wraps(function)
        async def async_wrapped(obj_self, data: DataType, url: str):
            tries = 1
            while tries <= obj_self.config.max_tries:
                try:
                    return await function(obj_self, data=data, url=url)
                except aiohttp.ClientError as e:
                    # 网络异常
                    obj_self.logger.debug(f"ClientError: {url}, Raw: {str(e)}, Tries: {tries}")
                except asyncio.exceptions.TimeoutError as e:
                    # 网络超时
                    obj_self.logger.debug(f"TimeoutError: {url}, Tries: {tries}")
                finally:
                    tries += 1
                    await asyncio.sleep(obj_self.config.retry_sleep_seconds)
            else:
                raise MaxTriesError(f"MaxTriesError: {url}")

        return async_wrapped


class BinanceKlineUpdater(IKlineUpdater, Generic[DataType, ConfigType]):
    single_request_limit: int = 499

    def __init__(
            self,
            config: ConfigType,
            logger: LoggerType,
            session: aiohttp.ClientSession = None
    ):
        self.config = config
        self.logger = logger
        self.session = session

    @abstractmethod
    def get_urls(self, data: DataType) -> DataType:
        """
        接受一个data对象
        生成需要爬虫的url，并把它们全部添加进data.url_done_dict中当key
        """

        """
        eg.
        
        symbol = data.symbol
        timeframe = data.timeframe
        limit = data.limit

        request_timeframe = binance_timeframe_request_dict[timeframe]
        delta_ms = timeframe_timestamp_ms_dict[timeframe]
        url = "https://fapi.binance.com/fapi/v1/klines" \
              "?symbol={symbol}&interval={request_timeframe}&endTime={end_time}&limit={this_limit}"

        end_time = int(time.time() * 1e3)
        while limit > 0:
            this_limit = self.single_request_limit if limit > self.single_request_limit else limit
            url_tmp = url.format(
                symbol=symbol,
                request_timeframe=request_timeframe,
                end_time=end_time,
                this_limit=this_limit
            )
            data.set_url(url=url_tmp)
            limit -= this_limit
            end_time -= this_limit * delta_ms
        """

        return data

    @CatchWrapper[DataType]()  # 捕获MaxTriesError/StatusError，并设置给data
    async def get_klines(self, data: DataType) -> DataType:
        # get raw
        raw: list[list[int, float, ...]] = []
        for url in data.url_done_dict.keys():
            raw_tmp = await self._request(
                data=data,
                url=url
            )
            raw.extend(raw_tmp)
            data.set_url_done(url=url)

        # 排序
        raw.sort(key=lambda x: x[0])

        # 去重
        raw_dropna = []
        for k, g in itertools.groupby(raw, key=lambda x: x[0]):
            raw_dropna.append(list(g)[0])

        # process raw
        klines: list[Kline] = self._process_raw(raw=raw_dropna)

        # set klines
        data.set_klines(klines=klines)

        return data

    async def _process_response(self, url: str, response: aiohttp.ClientResponse) -> list:
        """检查response的状态码/构造json"""

        status = response.status
        if status != 200:
            raise StatusError(f"StatusError: {url}, Status: {status}")
        else:
            content = await response.json(encoding="utf-8")
            self.logger.debug(f"Fetch Success: {url}")
            return content

    @RetryWrapper[DataType]()  # 捕获ClientError并重试；抛出MaxTriesError，由catch捕获
    @TimeoutWrapper[DataType]()  # 抛出TimeoutError，由_with_retries捕获
    async def _request(self, data: DataType, url: str):
        """
        一般情况下，url出错会直接无法连接
        也有可能是404
        标的名称出错，返回是400
        """
        if self.session:
            async with self.session.get(url=url, proxy=self.config.proxy) as response:
                # 抛出StatusError，由catch捕获；可能抛出ClientError，由_with_retries捕获
                # 还不能做成装饰器，因为with语句在退出后会自动关系connection
                raw_tmp = await self._process_response(url=url, response=response)

        else:
            async with aiohttp.request(method="GET", url=url, proxy=self.config.proxy) as response:
                raw_tmp = await self._process_response(url=url, response=response)

        return raw_tmp

    def _process_raw(self, raw: list[list[int, float, ...]]) -> list[Kline]:
        # sort
        raw.sort(key=lambda x: x[0])

        kline_list: list[Kline] = [
            Kline(
                open_time=timestamp_ms_to_datetime_utc(row[0]),  # 这个返回的就是int
                open=float(row[1]),
                high=float(row[2]),
                low=float(row[3]),
                close=float(row[4]),
                volume=float(row[5])
            )
            for row in raw
        ]
        return kline_list

    async def __call__(self, data: DataType) -> DataType:
        data = self.get_urls(data=data)
        data = await self.get_klines(data=data)
        return data


if __name__ == "__main__":
    pass
