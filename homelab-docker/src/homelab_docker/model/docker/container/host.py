from __future__ import annotations

import typing
from enum import StrEnum, auto
from typing import ClassVar

import pulumi_docker as docker
from homelab_pydantic import HomelabBaseModel, HomelabRootModel
from pydantic import IPvAnyAddress

if typing.TYPE_CHECKING:
    from ....extract import ExtractorArgs


class HostMode(StrEnum):
    LOCALHOST = auto()


class ContainerHostFullConfig(HomelabBaseModel):
    host: str
    ip: IPvAnyAddress | str

    def to_args(self, extractor_args: ExtractorArgs) -> docker.ContainerHostArgs:
        return docker.ContainerHostArgs(host=self.host, ip=str(self.ip))


class ContainerHostHostConfig(HomelabBaseModel):
    host: str
    internal: bool

    def to_args(self, extractor_args: ExtractorArgs) -> docker.ContainerHostArgs:
        host_model = extractor_args.get_host_model(self.host)
        return ContainerHostFullConfig(
            host=host_model.access.address,
            ip=host_model.ip.internal_ if self.internal else host_model.ip.external_,
        ).to_args(extractor_args)


class ContainerHostModeConfig(HomelabBaseModel):
    LOCALHOST_HOST: ClassVar[str] = "host.docker.internal"
    LOCALHOST_IP: ClassVar[str] = "host-gateway"

    mode: HostMode

    def to_args(self, extractor_args: ExtractorArgs) -> docker.ContainerHostArgs:
        match self.mode:
            case HostMode.LOCALHOST:
                return ContainerHostFullConfig(
                    host=self.LOCALHOST_HOST, ip=self.LOCALHOST_IP
                ).to_args(extractor_args)


class ContainerHostConfig(
    HomelabRootModel[
        ContainerHostHostConfig | ContainerHostModeConfig | ContainerHostFullConfig
    ]
):
    def to_args(self, extractor_args: ExtractorArgs) -> docker.ContainerHostArgs:
        return self.root.to_args(extractor_args)
