from __future__ import annotations

import typing
from enum import StrEnum, auto
from typing import ClassVar

import pulumi_docker as docker
from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel, HomelabRootModel

if typing.TYPE_CHECKING:
    from ....extract import ExtractorArgs


class HostMode(StrEnum):
    LOCALHOST = auto()


class ContainerHostFullConfig(HomelabBaseModel):
    host: GlobalExtract
    ip: GlobalExtract

    def to_args(self, extractor_args: ExtractorArgs) -> docker.ContainerHostArgs:
        from ....extract.global_ import GlobalExtractor

        return docker.ContainerHostArgs(
            host=GlobalExtractor(self.host).extract_str(extractor_args),
            ip=GlobalExtractor(self.ip).extract_str(extractor_args),
        )

    def with_service(self, service: str, force: bool) -> ContainerHostFullConfig:
        return self.__replace__(
            host=self.host.with_service(service, force),
            ip=self.ip.with_service(service, force),
        )


class ContainerHostHostConfig(HomelabBaseModel):
    host: str
    internal: bool
    hostname: GlobalExtract | None = None

    def to_args(self, extractor_args: ExtractorArgs) -> docker.ContainerHostArgs:
        host_model = extractor_args.get_host_model(self.host)
        return ContainerHostFullConfig(
            host=self.hostname
            if self.hostname
            else GlobalExtract.from_simple(host_model.access.address),
            ip=GlobalExtract.from_simple(
                str(
                    host_model.ip.internal_
                    if self.internal
                    else host_model.ip.external_
                )
            ),
        ).to_args(extractor_args)

    def with_service(self, service: str, force: bool) -> ContainerHostHostConfig:
        return self.__replace__(
            hostname=GlobalExtract.with_service_nullable(self.hostname, service, force),
        )


class ContainerHostModeConfig(HomelabBaseModel):
    LOCALHOST_HOST: ClassVar[str] = "host.docker.internal"
    LOCALHOST_IP: ClassVar[str] = "host-gateway"

    mode: HostMode

    def to_args(self, extractor_args: ExtractorArgs) -> docker.ContainerHostArgs:
        match self.mode:
            case HostMode.LOCALHOST:
                return ContainerHostFullConfig(
                    host=GlobalExtract.from_simple(self.LOCALHOST_HOST),
                    ip=GlobalExtract.from_simple(self.LOCALHOST_IP),
                ).to_args(extractor_args)

    def with_service(self, service: str, force: bool) -> ContainerHostModeConfig:
        return self


class ContainerHostConfig(
    HomelabRootModel[
        ContainerHostHostConfig | ContainerHostModeConfig | ContainerHostFullConfig
    ]
):
    def to_args(self, extractor_args: ExtractorArgs) -> docker.ContainerHostArgs:
        return self.root.to_args(extractor_args)

    def with_service(self, service: str, force: bool) -> ContainerHostConfig:
        return ContainerHostConfig(self.root.with_service(service, force))
