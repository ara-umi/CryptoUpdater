# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: araumi
# Email: 532990165@qq.com
# DateTime: 2023/10/23 上午3:54

from abc import ABCMeta, abstractmethod
from multiprocessing import Process
from multiprocessing import Queue

from ..config import IConfig
from ..logger import LoggerFactory
from ..scheduler.main import IScheduler


class IStarterProcess(Process, metaclass=ABCMeta):

    @abstractmethod
    def __init__(
            self,
            job_queue: Queue,
            *args,
            **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.config = IConfig()
        self.logger = LoggerFactory(config=self.config).create_logger()
        self.job_queue = job_queue
        self.scheduler = IScheduler(*args, **kwargs)

    def run(self) -> None:
        self.main()

    def main(self):
        while True:
            try:
                self.scheduler()
            except Exception as e:
                self.scheduler.shutdown()
                self.logger.critical(repr(e))
                self.logger.warn(f"{self.__class__.__name__} restart...")


if __name__ == "__main__":
    pass
