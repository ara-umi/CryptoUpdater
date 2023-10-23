# !/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: araumi
# Email: 532990165@qq.com
# DateTime: 2023/8/28 下午3:51

import datetime
from queue import Queue

import pytz
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger

from .base import IScheduler
from ..config import BinanceFuturesUMConfig
from ..instance.data import BinanceFuturesUMData
from ..logger import LoggerFactory, LoggerType
from ..service.connector import AsyncPgPoolConnector
from ..service.main import BinanceFuturesUMService


class BinanceFuturesUMStarterScheduler(IScheduler):
    coalesce = False
    misfire_grace_time = 10
    replace_existing = True
    max_instances = 1

    def __init__(
            self,
            config: BinanceFuturesUMConfig,
            logger: LoggerType,
            job_queue: Queue
    ):
        super().__init__(
            config=config,
            logger=logger
        )
        self.job_queue = job_queue

    def heartbeat(self):
        config = BinanceFuturesUMConfig()
        logger = LoggerFactory(config=config).create_logger()
        format_time = datetime.datetime.now(tz=pytz.UTC).isoformat(sep=" ")
        logger.success(f"Heartbeat: {format_time}")

    async def update_timeframe(
            self,
            timeframe: str,
            job_queue: Queue
    ):
        config = BinanceFuturesUMConfig()
        connector = AsyncPgPoolConnector(config=config)
        logger = LoggerFactory(config=config).create_logger()
        service = BinanceFuturesUMService(connector=connector, logger=logger)

        logger.success(f"Update triggered on timeframe: {timeframe}")

        for symbol in await service.select_symbol(is_deleted=False):
            try:
                data: BinanceFuturesUMData = BinanceFuturesUMData()
                data.symbol = symbol
                data.timeframe = timeframe
                data.limit = config.limit.get(timeframe, 0)
                job_queue.put(data)
            except Exception as e:
                logger.critical(repr(e))
                continue

        await connector.release()

    @property
    def job_heartbeat(self):
        return {
            "func": self.heartbeat,
            "coalesce": self.coalesce,
            "misfire_grace_time": self.misfire_grace_time,
            "replace_existing": self.replace_existing,
            "max_instances": self.max_instances,
            "trigger": CronTrigger.from_crontab("0-59/5 * * * *"),
            "args": [],
            "kwargs": {},
            "name": "heartbeat"
        }

    @property
    def job_update_1m(self):
        return {
            "func": self.update_timeframe,
            "coalesce": self.coalesce,
            "misfire_grace_time": self.misfire_grace_time,
            "replace_existing": self.replace_existing,
            "max_instances": self.max_instances,
            "trigger": CronTrigger(second=40, minute="29,59", hour="*"),
            "args": [],
            "kwargs": {
                "timeframe": "1M",
                "job_queue": self.job_queue
            },
            "name": "update_1m"
        }

    @property
    def job_update_30m(self):
        return {
            "func": self.update_timeframe,
            "coalesce": self.coalesce,
            "misfire_grace_time": self.misfire_grace_time,
            "replace_existing": self.replace_existing,
            "max_instances": self.max_instances,
            "trigger": CronTrigger(second=45, minute="29,59", hour="*"),
            "args": [],
            "kwargs": {
                "timeframe": "30M",
                "job_queue": self.job_queue
            },
            "name": "update_30m"
        }

    @property
    def job_update_1h(self):
        return {
            "func": self.update_timeframe,
            "coalesce": self.coalesce,
            "misfire_grace_time": self.misfire_grace_time,
            "replace_existing": self.replace_existing,
            "max_instances": self.max_instances,
            "trigger": CronTrigger(second=45, minute="59", hour="*"),
            "args": [],
            "kwargs": {
                "timeframe": "1H",
                "job_queue": self.job_queue
            },
            "name": "update_1h"
        }

    @property
    def job_update_4h(self):
        return {
            "func": self.update_timeframe,
            "coalesce": self.coalesce,
            "misfire_grace_time": self.misfire_grace_time,
            "replace_existing": self.replace_existing,
            "max_instances": self.max_instances,
            "trigger": CronTrigger(second=50, minute="59", hour="*/4"),
            "args": [],
            "kwargs": {
                "timeframe": "4H",
                "job_queue": self.job_queue
            },
            "name": "update_4h"
        }

    @property
    def job_update_1d(self):
        return {
            "func": self.update_timeframe,
            "coalesce": self.coalesce,
            "misfire_grace_time": self.misfire_grace_time,
            "replace_existing": self.replace_existing,
            "max_instances": self.max_instances,
            "trigger": CronTrigger(second=50, minute="59", hour="23"),
            "args": [],
            "kwargs": {
                "timeframe": "1D",
                "job_queue": self.job_queue
            },
            "name": "update_1d"
        }

    @property
    def job_update_1m_test(self):
        trigger_time = datetime.datetime.now(tz=self.tz) + datetime.timedelta(seconds=3)
        return {
            "func": self.update_timeframe,
            "coalesce": self.coalesce,
            "misfire_grace_time": self.misfire_grace_time,
            "replace_existing": self.replace_existing,
            "max_instances": self.max_instances,
            "trigger": DateTrigger(run_date=trigger_time),
            "args": [],
            "kwargs": {
                "timeframe": "1M",
                "job_queue": self.job_queue
            },
            "name": "update_1m_test "
        }

    @property
    def job_update_30m_test(self):
        trigger_time = datetime.datetime.now(tz=self.tz) + datetime.timedelta(seconds=8)
        return {
            "func": self.update_timeframe,
            "coalesce": self.coalesce,
            "misfire_grace_time": self.misfire_grace_time,
            "replace_existing": self.replace_existing,
            "max_instances": self.max_instances,
            "trigger": DateTrigger(run_date=trigger_time),
            "args": [],
            "kwargs": {
                "timeframe": "30M",
                "job_queue": self.job_queue
            },
            "name": "update_30m_test "
        }

    @property
    def job_update_1h_test(self):
        trigger_time = datetime.datetime.now(tz=self.tz) + datetime.timedelta(seconds=8)
        return {
            "func": self.update_timeframe,
            "coalesce": self.coalesce,
            "misfire_grace_time": self.misfire_grace_time,
            "replace_existing": self.replace_existing,
            "max_instances": self.max_instances,
            "trigger": DateTrigger(run_date=trigger_time),
            "args": [],
            "kwargs": {
                "timeframe": "1H",
                "job_queue": self.job_queue
            },
            "name": "update_1h_test "
        }

    def main(self):
        self.add_job(self.job_heartbeat)
        self.add_job(self.job_update_1m)
        self.add_job(self.job_update_30m)
        self.add_job(self.job_update_1h)
        self.add_job(self.job_update_4h)
        self.add_job(self.job_update_1d)

    def main_test(self):
        self.add_job(self.job_heartbeat)
        self.add_job(self.job_update_1m_test)
        self.add_job(self.job_update_30m_test)
        self.add_job(self.job_update_1h_test)


if __name__ == "__main__":
    pass
