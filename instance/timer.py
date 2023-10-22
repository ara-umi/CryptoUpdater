# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: araumi
# Email: 532990165@qq.com
# DateTime: 2023/8/25 上午3:32

import time


class Timer(object):

    def __enter__(self):
        self.start = time.process_time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end = time.process_time()
        self.elapsed = self.end - self.start
        print(f"Elapsed: {self.elapsed:.2f}s.")


if __name__ == "__main__":
    pass
