# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: araumi
# Email: 532990165@qq.com
# DateTime: 2023/7/11 下午10:29

import asyncio
from abc import ABCMeta, abstractmethod

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from ..config import IConfig
from ..logger import LoggerFactory, LoggerType


class IScheduler(metaclass=ABCMeta):
    scheduler_type = AsyncIOScheduler
    tz = pytz.timezone("Asia/Shanghai")
    scheduler_settings = {
        "timezone": tz
    }

    # executor = ThreadPoolExecutor(3)

    @abstractmethod
    def __init__(
            self,
            config: IConfig,
            logger: LoggerType
    ):
        self.config = config
        self.logger = logger
        self.scheduler = self.scheduler_type(**self.scheduler_settings)

    def add_job(self, job: dict):
        self.scheduler.add_job(**job)
        self.logger.success(f"Add Job: {job.get('name')}")

    def shutdown(self):
        self.scheduler.remove_all_jobs()
        self.scheduler.shutdown()
        self.logger.success(f"Scheduler ShutDown")

    @abstractmethod
    def main(self):
        ...

    @abstractmethod
    def main_test(self):
        ...

    def __call__(self, *args, **kwargs):
        self.main()
        self.scheduler.start()
        self.logger.success(f"Scheduler Start")
        asyncio.get_event_loop().run_forever()

    def test(self):
        self.main_test()
        self.scheduler.start()
        self.logger.success(f"Scheduler Test Start")
        asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
    pass
