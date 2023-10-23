# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: araumi
# Email: 532990165@qq.com
# DateTime: 2023/8/30 下午8:21

import signal
import sys
import time
import warnings
from functools import wraps
from multiprocessing import Queue, Process
from typing import Callable

from .process.BinanceFuturesUM.downloader import BinanceFuturesUMDownloaderProcess
from .process.BinanceFuturesUM.starter import BinanceFuturesUMStarterProcess
from .process.BinanceFuturesUM.worker import BinanceFuturesUMWorkerProcess


class ExitWrapper(object):

    def signal_handler(
            self,
            sig,
            frame,
            procs: list[Process]
    ):
        warnings.warn("Exiting gracefully...")
        for proc in procs:
            proc.terminate()
        time.sleep(1)
        warnings.warn("Exited")
        sys.exit(0)

    def __call__(self, function: Callable):

        @wraps(function)
        def wrapped(obj_self, *args, **kwargs):
            try:
                function(obj_self, *args, **kwargs)
            except KeyboardInterrupt:
                self.signal_handler(
                    sig=signal.SIGINT,
                    frame=None,
                    procs=[
                        obj_self.starter_process,
                        obj_self.worker_process,
                        obj_self.downloader_process
                    ]
                )

        return wrapped


class BinanceFuturesUMUpdate(object):
    def __init__(self):
        self.JobQueue: Queue = Queue()
        self.ResultQueue: Queue = Queue()

        self.starter_process = BinanceFuturesUMStarterProcess(
            job_queue=self.JobQueue
        )
        self.worker_process = BinanceFuturesUMWorkerProcess(
            job_queue=self.JobQueue,
            result_queue=self.ResultQueue
        )
        self.downloader_process = BinanceFuturesUMDownloaderProcess(
            result_queue=self.ResultQueue
        )

    @ExitWrapper()
    def __call__(self):
        self.starter_process.start()
        self.worker_process.start()
        self.downloader_process.start()

        self.starter_process.join()
        self.worker_process.join()
        self.downloader_process.join()


if __name__ == "__main__":
    pass
