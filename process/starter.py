# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: araumi
# Email: 532990165@qq.com
# DateTime: 2023/10/23 上午3:54

from abc import ABCMeta, abstractmethod
from multiprocessing import Process


class IStarterProcess(Process, metaclass=ABCMeta):

    def run(self) -> None:
        self.main()

    @abstractmethod
    def main(self):
        ...

        # while True:
        #     try:
        #         self.scheduler()
        #     except Exception as e:
        #         self.scheduler.shutdown()
        #         self.logger.critical(repr(e))
        #         self.logger.warning(f"{self.__class__.__name__} restart...")


if __name__ == "__main__":
    pass
