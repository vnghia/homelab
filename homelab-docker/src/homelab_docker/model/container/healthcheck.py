from __future__ import annotations

import typing

import pulumi_docker as docker
from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel
from pydantic import PositiveInt

from ...extract.global_ import GlobalExtractor

if typing.TYPE_CHECKING:
    from ...extract import ExtractorArgs


class ContainerHealthCheckConfig(HomelabBaseModel):
    tests: list[GlobalExtract]
    interval: str | None = None
    retries: PositiveInt | None = None
    start_interval: str | None = None
    start_period: str | None = None
    timeout: str | None = None

    def to_args(self, extractor_args: ExtractorArgs) -> docker.ContainerHealthcheckArgs:
        return docker.ContainerHealthcheckArgs(
            tests=[
                GlobalExtractor(test).extract_str(extractor_args) for test in self.tests
            ],
            interval=self.interval,
            retries=self.retries,
            start_interval=self.start_interval,
            start_period=self.start_period,
            timeout=self.timeout,
        )
