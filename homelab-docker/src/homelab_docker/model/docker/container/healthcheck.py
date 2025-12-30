from __future__ import annotations

import typing
from typing import ClassVar

import pulumi_docker as docker
from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel
from pulumi import Output
from pydantic import PositiveInt

from ....extract.global_ import GlobalExtractor

if typing.TYPE_CHECKING:
    from ....extract import ExtractorArgs


class ContainerHealthCheckConfig(HomelabBaseModel):
    SECONDS_IN_MINUTE: ClassVar[PositiveInt] = 60
    BINARY_HTTP_REQUEST: ClassVar[set[str]] = {"wget", "curl"}

    # TODO: set the default value to None after https://github.com/kreuzwerker/terraform-provider-docker/pull/834
    tests: list[GlobalExtract] = []
    interval: PositiveInt = 120
    timeout: PositiveInt = 5
    start_period: PositiveInt = 60
    start_interval: PositiveInt = 5
    retries: PositiveInt = 5

    # We have to transform the exit code because Docker only accept status code 1
    # https://docs.docker.com/reference/dockerfile/#healthcheck
    @classmethod
    def transform_tests(cls, tests: list[str]) -> list[str]:
        test_type = tests[0]
        if test_type == "CMD-SHELL":
            return tests
        if test_type == "CMD":
            binary = tests[1]
            if binary in cls.BINARY_HTTP_REQUEST:
                return ["CMD-SHELL", " ".join(tests[1:]) + " || exit 1"]
            return tests
        raise ValueError(
            "Healthcheck test must start with either CMD or CMD-SHELL, got {}".format(
                test_type
            )
        )

    @classmethod
    def to_second(cls, count: PositiveInt) -> str:
        if count < cls.SECONDS_IN_MINUTE:
            return "{}s".format(count)
        return "{}m{}s".format(
            count // cls.SECONDS_IN_MINUTE, count % cls.SECONDS_IN_MINUTE
        )

    def to_args(self, extractor_args: ExtractorArgs) -> docker.ContainerHealthcheckArgs:
        tests = [
            GlobalExtractor(test).extract_str(extractor_args) for test in self.tests
        ]

        return docker.ContainerHealthcheckArgs(
            tests=Output.all(*tests).apply(self.transform_tests) if tests else tests,
            interval=self.to_second(self.interval),
            timeout=self.to_second(self.timeout),
            start_period=self.to_second(self.start_period),
            start_interval=self.to_second(self.start_interval),
            retries=self.retries,
        )
