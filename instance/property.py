# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: araumi
# Email: 532990165@qq.com
# DateTime: 2023/9/20 下午10:53

class PlaceHolder(object):
    """
    属性占位符，用于在定义类时，先定义属性，后赋值
    本质是个非覆盖型描述符
    """

    def __set_name__(self, owner, name):
        self.storage_name = name

    def __get__(self, instance, value):
        try:
            return instance.__dict__[self.storage_name]
        except KeyError:
            raise AttributeError(f"{self.storage_name} not set yet")


if __name__ == "__main__":
    pass
