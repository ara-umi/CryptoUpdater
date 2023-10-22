# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: araumi
# Email: 532990165@qq.com
# DateTime: 2023/6/22 上午2:19

import json
import os
import pathlib
from abc import ABCMeta, abstractmethod
from pathlib import Path

from .tools.collection import FrozenJSON


class IConfig(metaclass=ABCMeta):
    root_path = Path(os.path.dirname(__file__))

    @property
    @abstractmethod
    def config_path(self) -> pathlib.Path:
        return ...

    def load_config(self) -> FrozenJSON:
        with open(self.config_path, "r") as f:
            raw: dict = json.load(f)
            return FrozenJSON(raw)

    def to_dict(self) -> dict:
        return self.config.to_dict()

    @abstractmethod
    def __init__(self):
        """
        这里就统一config格式
        不然IConfig属性都没有，根本没办法用
        """

        self.config: FrozenJSON = self.load_config()

        # -----------------------------------------
        # logger
        # -----------------------------------------
        self.stream_level: str = str(self.config.logger.stream_level).upper()
        self.file_level: str = str(self.config.logger.file_level).upper()

        # -----------------------------------------
        # updater
        # -----------------------------------------
        self.proxy: str = str(self.config.updater.proxy)
        self.request_timeout_seconds: int = int(self.config.updater.request_timeout_seconds)
        self.max_tries: int = int(self.config.updater.max_tries)
        self.retry_sleep_seconds: int = int(self.config.updater.retry_sleep_seconds)

        self.semaphore_limit: int = int(self.config.updater.semaphore_limit)
        self.semaphore_sleep_seconds: int = int(self.config.updater.semaphore_sleep_seconds)

        self.limit: dict = self.config.updater.limit.to_dict()

        # -----------------------------------------
        # service
        # -----------------------------------------

        self.pg_host: str = str(self.config.service.postgres.host)
        self.pg_port: int = int(self.config.service.postgres.port)
        self.pg_user: str = str(self.config.service.postgres.user)
        self.pg_password: str = str(self.config.service.postgres.password)
        self.pg_database: str = str(self.config.service.postgres.database)

        self.pg_min_size: int = int(self.config.service.postgres.min_size)
        self.pg_max_size: int = int(self.config.service.postgres.max_size)


class BinanceFuturesUMConfig(IConfig):

    @property
    def config_path(self) -> pathlib.Path:
        return self.root_path / "config_binance_futures_um.json"

    def __init__(self):
        super().__init__()


if __name__ == "__main__":
    pass
