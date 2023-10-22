# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: araumi
# Email: 532990165@qq.com
# DateTime: 2023/8/11 下午10:22

from asyncpg import Record

from .interface import IService
from ..instance.kline import Kline
from ..tools.dt import datetime_to_pg_timestamp_with_time_zone
from ..tools.pg_query_builder import process_literal


class BaseService(IService):
    async def insert_symbol_many(self, symbols: list[str]):
        query = """INSERT INTO "symbol" ("name")
VALUES {VALUES}
ON CONFLICT DO NOTHING
RETURNING "id";"""

        value_list: list[str] = [
            f"({process_literal(symbol)})"
            for symbol in symbols
        ]
        values: str = ', '.join(value_list)
        query = query.format(VALUES=values)
        returning = await self.connector.fetch(query=query)
        return returning

    async def select_symbols(
            self,
            is_deleted: bool = False
    ) -> list[Record]:
        query = """SELECT "name"
FROM "symbol"
WHERE 1=1{WHERE};"""
        where: str = ""

        if is_deleted:
            where += f"\nAND \"is_deleted\" = {process_literal(is_deleted)}"

        query = query.format(WHERE=where)
        res = await self.connector.fetch(query=query)

        return res

    async def delete_symbol(self, symbol: str):
        query = """DELETE FROM "symbol"
WHERE 1=1
AND "name" = {symbol};"""

        symbol = process_literal(symbol)
        query = query.format(symbol=symbol)
        await self.connector.execute(query=query)

    async def insert_kline_many(self, symbol: str, interval: int, klines: list[Kline]):

        query = """INSERT INTO "kline" ("symbol", "interval", "open_time", "open", "high", "low", "close", "volume")
VALUES 
{VALUES}
ON CONFLICT ON CONSTRAINT "kline_uk" DO UPDATE 
SET 
"open" = EXCLUDED."open",
"high" = EXCLUDED."high",
"low" = EXCLUDED."low",
"close" = EXCLUDED."close",
"volume" = EXCLUDED."volume";"""

        value_list = [
            f"({process_literal(symbol)}, {process_literal(interval)}, {process_literal(datetime_to_pg_timestamp_with_time_zone(kline.open_time))}, {kline.open}, {kline.high}, {kline.low}, {kline.close}, {kline.volume})"
            for kline in klines
        ]
        values: str = ',\n'.join(value_list)
        query = query.format(VALUES=values)
        await self.connector.execute(query=query)

    async def select_kline(self, symbol: str, interval: int, limit: int = None) -> list[Record]:

        query = """SELECT "open_time", "open", "high", "low", "close", "volume"
FROM "kline"
WHERE 1=1
AND
"symbol" = {symbol}
AND
"interval" = {interval}
ORDER BY "open_time" DESC{limit};"""

        symbol = process_literal(symbol)
        interval = process_literal(interval)
        if limit:
            assert limit > 0, f"Limit must be positive (got {limit})"
            limit = "\nLIMIT {limit}".format(limit=process_literal(limit))
        else:
            limit = ""

        query = query.format(
            symbol=symbol,
            interval=interval,
            limit=limit
        )

        res = await self.connector.fetch(query=query)

        return res


if __name__ == "__main__":
    pass
