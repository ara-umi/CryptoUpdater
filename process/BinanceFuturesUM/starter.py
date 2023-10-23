# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: araumi
# Email: 532990165@qq.com
# DateTime: 2023/10/23 上午3:54

from multiprocessing import Queue

from ..starter import IStarterProcess
from ...config import BinanceFuturesUMConfig
from ...logger import LoggerFactory
from ...scheduler.main import BinanceFuturesUMStarterScheduler


class BinanceFuturesUMStarterProcess(IStarterProcess):

    def __init__(
            self,
            job_queue: Queue
    ):
        super().__init__()

        self.config = BinanceFuturesUMConfig()
        self.logger = LoggerFactory(config=self.config).create_logger()
        self.job_queue = job_queue
        self.scheduler = BinanceFuturesUMStarterScheduler(
            config=self.config,
            logger=self.logger,
            job_queue=self.job_queue
        )

    def main(self):
        while True:
            try:
                self.scheduler()
                # self.scheduler.test()
            except Exception as e:
                self.scheduler.shutdown()
                self.logger.critical(repr(e))
                self.logger.warning(f"{self.__class__.__name__} restart...")


if __name__ == "__main__":
    pass
