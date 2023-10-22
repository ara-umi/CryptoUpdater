# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: araumi
# Email: 532990165@qq.com
# DateTime: 2023/10/23 上午3:25

from abc import ABCMeta, abstractmethod

from ..instance.data import IData


class IKlineUpdater(metaclass=ABCMeta):
    @abstractmethod
    async def __call__(self, data: IData) -> IData:
        ...


if __name__ == "__main__":
    pass
