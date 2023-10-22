# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: araumi
# Email: 532990165@qq.com
# DateTime: 2023/6/22 上午2:19

import json
import os
from pathlib import Path

from tools.collection import FrozenJSON


class Config(object):
    root_path = Path(os.path.dirname(__file__))
    config_path = root_path / "config.json"

    def load_config(self) -> FrozenJSON:
        with open(self.config_path, "r") as f:
            raw: dict = json.load(f)
            return FrozenJSON(raw)

    def to_dict(self) -> dict:
        return self.config.to_dict()

    def __init__(self):
        self.config: FrozenJSON = self.load_config()

        # -----------------------------------------
        # logger
        # -----------------------------------------
        self.stream_level: str = str(self.config.logger.stream_level).upper()
        self.file_level: str = str(self.config.logger.file_level).upper()

        # -----------------------------------------
        # spider
        # -----------------------------------------
        self.proxy: str = str(self.config.spider.proxy)
        self.request_timeout_seconds: int = int(self.config.spider.request_timeout_seconds)
        self.max_tries: int = int(self.config.spider.max_tries)
        self.retry_sleep_seconds: int = int(self.config.spider.retry_sleep_seconds)

        self.semaphore_limit: int = int(self.config.spider.semaphore_limit)
        self.semaphore_sleep_seconds: int = int(self.config.spider.semaphore_sleep_seconds)

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


if __name__ == "__main__":
    pass
