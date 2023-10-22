# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: araumi
# Email: 532990165@qq.com
# DateTime: 2023/8/25 上午1:22

import os
import pathlib
import sys

import loguru

from .config import IConfig

LoggerType = type[loguru.logger]


class LoggerFactory(object):
    """
    现在没分那么细
    但按理说以后涉及到多个交易所
    进程肯定是分开的，service也是分开的，log日志也要分开，至少log文件的名字要分开，不然会混淆
    就要单独bind不同的logger
    """

    root = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))

    def __init__(self, config: IConfig):
        self.config = config

    def create_logger(self):
        logger = loguru.logger
        logger.remove(handler_id=None)
        # stream
        logger.add(
            sink=sys.stdout,
            filter=lambda record: record["level"] not in ("ERROR", "CRITICAL"),
            level=self.config.stream_level
        )
        logger.add(
            sink=sys.stderr,
            filter=lambda record: record["level"] in ("ERROR", "CRITICAL"),
            level="ERROR"
        )
        # file
        log_path = self.root / "log" / "CryptoUpdater"  # fixed
        logger.add(
            sink=log_path,
            level=self.config.file_level,
            rotation="1 week",
            encoding="utf-8",
            retention="1 month"
        )
        return logger


if __name__ == "__main__":
    pass
