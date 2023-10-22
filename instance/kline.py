# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: araumi
# Email: 532990165@qq.com
# DateTime: 2023/8/25 上午2:07

import datetime
from typing import NamedTuple


class Kline(NamedTuple):
    """
    在考虑是不是需要分BinanceKline
    按理说各大交易所返回的数据都是一致的，都有ohlc和volume
    最多就是volume有出入
    """
    open_time: datetime.datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


if __name__ == "__main__":
    pass
