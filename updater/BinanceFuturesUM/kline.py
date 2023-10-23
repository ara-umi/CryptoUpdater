# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: araumi
# Email: 532990165@qq.com
# DateTime: 2023/8/25 上午1:16

import time

from ..Binance import BinanceKlineUpdater
from ...config import BinanceFuturesUMConfig
from ...instance.data import BinanceFuturesUMData
from ...instance.mapping import binance_timeframe_request_dict, timeframe_timestamp_ms_dict


class BinanceFuturesUMKlineUpdater(BinanceKlineUpdater[BinanceFuturesUMData, BinanceFuturesUMConfig]):

    def get_urls(self, data: BinanceFuturesUMData) -> BinanceFuturesUMData:
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

        return data


if __name__ == "__main__":
    pass
