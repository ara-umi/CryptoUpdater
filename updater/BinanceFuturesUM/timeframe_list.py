# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: araumi
# Email: 532990165@qq.com
# DateTime: 2023/8/25 上午3:15

from ...config import BinanceFuturesUMConfig
from ...logger import LoggerType


class BinanceFuturesUMTimeframeListUpdater(object):
    """就写死在代码里"""

    def __init__(self, config: BinanceFuturesUMConfig, logger: LoggerType):
        self.config = config
        self.logger = logger

    async def _request(self) -> list[str]:
        return [
            "1M",
            "30M",
            "1H",
            "4H",
            "1D"
        ]

    async def __call__(self) -> list[str]:
        self.logger.info(f"Request Binance Futures UM Timeframe List")
        timeframe_list = await self._request()
        self.logger.success(f"Request Binance Futures UM Timeframe List: {timeframe_list}")
        return timeframe_list


if __name__ == "__main__":
    pass
