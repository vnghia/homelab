from __future__ import annotations

import typing

import pulumi_docker as docker
from homelab_pydantic import HomelabBaseModel
from pydantic import PositiveInt

from ...extract import GlobalExtract

if typing.TYPE_CHECKING:
    from ...resource.service import ServiceResourceBase
    from . import ContainerModel


class ContainerHealthCheckConfig(HomelabBaseModel):
    tests: list[GlobalExtract]
    interval: str | None = None
    retries: PositiveInt | None = None
    start_period: str | None = None
    timeout: str | None = None

    def to_args(
        self, main_service: ServiceResourceBase, model: ContainerModel
    ) -> docker.ContainerHealthcheckArgs:
        return docker.ContainerHealthcheckArgs(
            tests=[test.extract_str(main_service, model) for test in self.tests],
            interval=self.interval,
            retries=self.retries,
            start_period=self.start_period,
            timeout=self.timeout,
        )
