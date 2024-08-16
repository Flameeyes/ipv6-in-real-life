# SPDX-FileCopyrightText: 2023 Diego Elio Pettenò
#
# SPDX-License-Identifier: 0BSD

import enum
import pathlib
import time
from typing import Optional

import aiodns
import prometheus_client
import pycares


class LoadStatus(enum.Enum):
    NOT_STARTED = "not_started"
    COMPLETED = "completed"
    FAILED = "failed"


def _exception_to_error(exception: aiodns.error.DNSError) -> str:
    (code, *_) = exception.args

    return pycares.errno.errorcode[code]


class Metrics:
    _SINGLETON: Optional["Metrics"] = None

    @classmethod
    def get(cls) -> "Metrics":
        if cls._SINGLETON is None:
            cls._SINGLETON = Metrics()

        return cls._SINGLETON

    def __init__(self):
        self._registry = prometheus_client.CollectorRegistry()

        self._run_timestamp = prometheus_client.Gauge(
            "last_run_timestamp",
            "Unix Timestamp of the last generation.",
            unit="seconds",
            registry=self._registry,
        )
        self._run_timestamp.set(time.time())

        self._source_loaded = prometheus_client.Enum(
            "source_load_status",
            "Status of the loading of data source.",
            registry=self._registry,
            states=[e.value for e in LoadStatus],
        )
        self.set_source_loaded(LoadStatus.NOT_STARTED)

        self._ipv4_resolution_successes = prometheus_client.Counter(
            "ipv4_resolution_successes",
            "Number of resolution successes when resolving A records",
            registry=self._registry,
        )

        self._ipv4_resolution_failures = prometheus_client.Counter(
            "ipv4_resolution_failures",
            "Number of resolution failures when resolving A records",
            ["error"],
            registry=self._registry,
        )

        self._ipv6_resolution_successes = prometheus_client.Counter(
            "ipv6_resolution_successes",
            "Number of resolution successes when resolving AAAA records",
            registry=self._registry,
        )

        self._ipv6_resolution_failures = prometheus_client.Counter(
            "ipv6_resolution_failures",
            "Number of resolution failures when resolving AAAA records",
            ["error"],
            registry=self._registry,
        )

    def set_source_loaded(self, state: LoadStatus) -> None:
        self._source_loaded.state(state.value)

    def count_ipv4_resolution_success(self) -> None:
        self._ipv4_resolution_successes.inc()

    def count_ipv4_resolution_failure(
        self, exception: aiodns.error.DNSError
    ) -> None:
        self._ipv4_resolution_failures.labels(
            _exception_to_error(exception)
        ).inc()

    def count_ipv6_resolution_success(self) -> None:
        self._ipv6_resolution_successes.inc()

    def count_ipv6_resolution_failure(
        self, exception: aiodns.error.DNSError
    ) -> None:
        self._ipv6_resolution_failures.labels(
            _exception_to_error(exception)
        ).inc()

    def write_out(self, output: pathlib.Path) -> None:
        prometheus_client.write_to_textfile(str(output), self._registry)
