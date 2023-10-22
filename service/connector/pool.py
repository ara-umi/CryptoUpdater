# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: araumi
# Email: 532990165@qq.com
# DateTime: 2023/6/27 上午3:42

from typing import Any, Optional

import asyncpg
import psycopg2
import psycopg2.pool
from psycopg2.extensions import connection as pg_connection
from psycopg2.extensions import cursor as pg_cursor

from .interface import IConnector
from ...config import IConfig


class AsyncPgPoolConnector(IConnector):
    def __init__(self, config: IConfig):
        self.config = config
        self._pool: Optional[asyncpg.Pool] = None

    async def create_pool(self) -> asyncpg.Pool:
        return await asyncpg.create_pool(
            database=self.config.pg_database,
            user=self.config.pg_user,
            password=self.config.pg_password,
            host=self.config.pg_host,
            port=self.config.pg_port,
            min_size=self.config.pg_min_size,
            max_size=self.config.pg_max_size,
            max_inactive_connection_lifetime=60
        )

    async def get_pool(self) -> asyncpg.Pool:
        if self._pool is None:
            self._pool = await self.create_pool()
        return self._pool

    async def release(self):
        if self._pool:
            await self._pool.close()

    async def execute(self, query: str):
        pool = await self.get_pool()
        conn: asyncpg.Connection = await pool.acquire()  # 连接失效我不知道是不是这一步报错的
        try:
            async with conn.transaction():  # transaction用上下文管理器做异常处理
                await conn.execute(query)
        except asyncpg.PostgresError as e:
            # warnings.warn(repr(e))
            raise e
        finally:
            await pool.release(conn)

    async def fetch(self, query: str):
        pool = await self.get_pool()
        conn: asyncpg.Connection = await pool.acquire()  # 连接失效我不知道是不是这一步报错的
        try:
            async with conn.transaction():  # transaction用上下文管理器做异常处理
                return await conn.fetch(query)
        except asyncpg.PostgresError as e:
            # warnings.warn(repr(e))
            raise e
        finally:
            await pool.release(conn)


class PgPoolConnector(IConnector):
    """
    连接池的很难实现重连，我就只限在PgConnector里面实现重连
    """

    def __init__(self, config: IConfig):
        self.config = config
        self._pool = psycopg2.pool.SimpleConnectionPool(
            minconn=config.pg_min_size,
            maxconn=config.pg_max_size,
            database=config.pg_database,
            user=config.pg_user,
            password=config.pg_password,
            host=config.pg_host,
            port=config.pg_port
        )

    def get_conn(self) -> pg_connection:
        return self._pool.getconn()

    def get_cursor(self, conn: pg_connection) -> pg_cursor:
        return conn.cursor()

    def put_conn(self, conn: pg_connection):
        self._pool.putconn(conn)

    def release(self):
        self._pool.closeall()

    def execute(self, query: str, _vars: Any = None):
        conn = self.get_conn()  # 这一步很难出错，如果出错，比如连接池不够用，最后finally可能需要if conn: conn.close()
        cursor = self.get_cursor(conn)
        try:
            conn.autocommit = False  # 也不用恢复True了，反正所有代码默认都是False，关闭自动提交
            cursor.execute(query=query, vars=_vars)
            conn.commit()
        except Exception as e:
            print(query)
            conn.rollback()
            raise e  # 如果不做接口，就不用包装exception了
        finally:
            self.put_conn(conn)

    def fetch(self, query: str, _vars: Any = None):
        """
        默认是做fetchall的，本质上等于execute+fetchall
        这个库垃圾就垃圾在这里，它的fetch是没有输入的
        而且executemany是拿不到它的returning的，所以executemany我统一不用，自己拼
        """
        conn = self.get_conn()  # 这一步很难出错，如果出错，比如连接池不够用，最后finally可能需要if conn: conn.close()
        cursor = self.get_cursor(conn)
        try:
            conn.autocommit = False  # 也不用恢复True了，反正所有代码默认都是False，关闭自动提交
            cursor.execute(query=query, vars=_vars)
            res = cursor.fetchall()
            conn.commit()
            return res
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self.put_conn(conn)


if __name__ == "__main__":
    pass
