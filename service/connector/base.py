# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: araumi
# Email: 532990165@qq.com
# DateTime: 2023/7/21 下午2:36

from typing import Any, Optional

import asyncpg
import psycopg2
from psycopg2.extensions import connection as pg_connection
from psycopg2.extensions import cursor as pg_cursor

from .interface import IConnector
from ...config import IConfig


class AsyncPgConnector(IConnector):
    """
    这个其实没什么用意义，因为asyncpg的异步就是通过连接池实现的
    一个连接在异步等待的时候，是不能用它再发送query的
    会报错：asyncpg.exceptions.InterfaceError: cannot perform operation: another operation is in progress
    所以如果你不想用连接池，那么就不能有self._conn，而是每次都conn都自己新建并管理
    """

    def __init__(self, config: IConfig):
        self.config = config
        self._conn: Optional[asyncpg.Connection] = None

    async def create_conn(self) -> asyncpg.Connection:
        return await asyncpg.connect(
            database=self.config.pg_database,
            user=self.config.pg_user,
            password=self.config.pg_password,
            host=self.config.pg_host,
            port=self.config.pg_port
        )

    async def get_conn(self) -> asyncpg.Connection:
        if self._conn is None or self._conn.is_closed():
            self._conn = await self.create_conn()
        return self._conn

    async def release(self):
        if self._conn and not self._conn.is_closed():
            await self._conn.close()

    async def execute(self, query: str):
        conn = await self.get_conn()
        async with conn.transaction():
            await conn.execute(query)

    async def fetch(self, query: str):
        conn = await self.get_conn()
        async with conn.transaction():
            return await conn.fetch(query)


class PgConnector(IConnector):
    def __init__(self, config: IConfig):
        self.config = config
        self._conn = self.create_conn()

    def create_conn(self) -> pg_connection:
        return psycopg2.connect(
            database=self.config.pg_database,
            user=self.config.pg_user,
            password=self.config.pg_password,
            host=self.config.pg_host,
            port=self.config.pg_port
        )

    def get_conn(self) -> pg_connection:
        if self._conn.closed:
            self.release()  # 我不知道释放一个已经关闭的连接会不会报错，也不知道有没有意义
            self._conn = self.create_conn()
        return self._conn

    def get_cursor(self) -> pg_cursor:
        return self.get_conn().cursor()

    def release(self):
        self._conn.close()

    def execute(self, query: str, _vars: Any = None):
        cursor = self.get_cursor()
        try:
            self._conn.autocommit = False  # 关闭自动提交
            cursor.execute(query=query, vars=_vars)
            self._conn.commit()
        except Exception as e:
            self._conn.rollback()
            raise e
        finally:
            cursor.close()

    def fetch(self, query: str, _vars: Any = None):
        cursor = self.get_cursor()
        try:
            self._conn.autocommit = False  # 关闭自动提交
            cursor.execute(query=query, vars=_vars)
            res = cursor.fetchall()
            self._conn.commit()
            return res
        except Exception as e:
            self._conn.rollback()
            raise e
        finally:
            cursor.close()


if __name__ == "__main__":
    pass
