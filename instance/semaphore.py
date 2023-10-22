# !/usr/bin/python3
# -*- coding: utf-8 -*-
# Author: ara_umi
# Email: 532990165@qq.com
# DateTime: 2023/4/13 21:47

import asyncio
import time


class MySemaphore(asyncio.Semaphore):
    def __init__(self, limit, sleep_second):
        super(MySemaphore, self).__init__(value=limit)
        self.sleep_second = sleep_second

    def _wake_up_next(self):
        res = super(MySemaphore, self)._wake_up_next()
        time.sleep(self.sleep_second)
        return res


if __name__ == "__main__":
    pass
