# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: araumi
# Email: 532990165@qq.com
# DateTime: 2023/6/27 上午3:39

from abc import ABCMeta, abstractmethod


class IConnector(metaclass=ABCMeta):

    @abstractmethod
    async def execute(self, *args, **kwargs):
        ...

    @abstractmethod
    async def fetch(self, *args, **kwargs):
        ...


if __name__ == "__main__":
    pass
