# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: araumi
# Email: 532990165@qq.com
# DateTime: 2023/8/25 上午12:31

from typing import runtime_checkable, Protocol


@runtime_checkable
class SupportsDict(Protocol):
    def to_dict(self) -> dict: ...


if __name__ == "__main__":
    pass
