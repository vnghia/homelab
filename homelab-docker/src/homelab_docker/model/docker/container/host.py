from __future__ import annotations

import typing
from enum import StrEnum, auto
from typing import ClassVar, Self

import pulumi_docker as docker
from homelab_extract import GlobalExtract
from homelab_extract.host import HostExtract, HostExtractSource
from homelab_extract.host.network import HostExtractNetworkSource, HostNetworkInfoSource
from homelab_pydantic import HomelabBaseModel, HomelabRootModel

if typing.TYPE_CHECKING:
    from ....extract import ExtractorArgs


class HostMode(StrEnum):
    LOCALHOST = auto()


class ContainerHostFullConfig(HomelabBaseModel):
    host: GlobalExtract
    ip: GlobalExtract

    def to_full(self, extractor_args: ExtractorArgs) -> Self:
        return self

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
    host: str | None = None
    hostname: GlobalExtract | None = None

    @classmethod
    def get_host_ip(
        cls, host: str | None, extractor_args: ExtractorArgs
    ) -> GlobalExtract:
        host_model = extractor_args.get_host_model(host)
        return GlobalExtract.from_simple(
            str(host_model.ip.get_ip(extractor_args.host.name))
        )

    def to_full(self, extractor_args: ExtractorArgs) -> ContainerHostFullConfig:
        host_model = extractor_args.get_host_model(self.host)
        if self.host:
            ip = self.get_host_ip(self.host, extractor_args)
        else:
            ip = GlobalExtract(
                HostExtract(
                    HostExtractSource(
                        HostExtractNetworkSource(
                            network=extractor_args.service.name(),
                            info=HostNetworkInfoSource.PROXY4,
                        )
                    )
                )
            )
        return ContainerHostFullConfig(
            host=self.hostname
            if self.hostname
            else GlobalExtract.from_simple(host_model.access.address),
            ip=ip,
        )

    def with_service(self, service: str, force: bool) -> ContainerHostHostConfig:
        return self.__replace__(
            hostname=GlobalExtract.with_service_nullable(self.hostname, service, force),
        )


class ContainerHostModeConfig(HomelabBaseModel):
    LOCALHOST_HOST: ClassVar[str] = "host.docker.internal"
    LOCALHOST_IP: ClassVar[str] = "host-gateway"

    mode: HostMode

    def to_full(self, extractor_args: ExtractorArgs) -> ContainerHostFullConfig:
        match self.mode:
            case HostMode.LOCALHOST:
                return ContainerHostFullConfig(
                    host=GlobalExtract.from_simple(self.LOCALHOST_HOST),
                    ip=GlobalExtract.from_simple(self.LOCALHOST_IP),
                )

    def with_service(self, service: str, force: bool) -> ContainerHostModeConfig:
        return self


class ContainerHostConfig(
    HomelabRootModel[
        GlobalExtract
        | ContainerHostHostConfig
        | ContainerHostModeConfig
        | ContainerHostFullConfig
    ]
):
    def to_full(self, extractor_args: ExtractorArgs) -> ContainerHostFullConfig:
        root = self.root
        if isinstance(root, GlobalExtract):
            return ContainerHostHostConfig(hostname=root).to_full(extractor_args)
        return root.to_full(extractor_args)

    def to_args(self, extractor_args: ExtractorArgs) -> docker.ContainerHostArgs:
        return self.to_full(extractor_args).to_args(extractor_args)

    def with_service(self, service: str, force: bool) -> ContainerHostConfig:
        return ContainerHostConfig(self.root.with_service(service, force))
