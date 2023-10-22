# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: araumi
# Email: 532990165@qq.com
# DateTime: 2023/8/25 上午1:14

import aiohttp


class AiohttpClientSession(object):

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    @staticmethod
    def create_session() -> aiohttp.ClientSession:
        return aiohttp.ClientSession()

    @staticmethod
    async def release_session(session: aiohttp.ClientSession) -> None:
        await session.close()


if __name__ == "__main__":
    pass
