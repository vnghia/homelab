from __future__ import annotations

import pulumi_docker as docker
import pulumi_docker_build as docker_build
from homelab_global import GlobalArgs
from homelab_network.resource.network import NetworkResource
from pulumi import ComponentResource, ResourceOptions
from pydantic.alias_generators import to_snake

from ..config.host import HostServiceModelConfig
from ..extract import ExtractorArgs
from ..resource.docker import DockerResource
from ..resource.file import FileVolumeProxy
from ..resource.service import ServiceResourceBase


class HostResourceBase(ComponentResource):
    _host_name: str | None = None

    HOSTS: dict[str, HostResourceBase] = {}

    def __init__(
        self,
        *,
        opts: ResourceOptions | None,
        global_args: GlobalArgs,
        network_resource: NetworkResource,
        config: HostServiceModelConfig,
    ) -> None:
        self.model = config[self.name()]

        super().__init__(
            self.name(),
            self.name(),
            None,
            ResourceOptions.merge(
                opts,
                ResourceOptions(
                    providers={
                        "docker": docker.Provider(
                            self.name(), host=self.model.access.ssh
                        ),
                        "docker-build": docker_build.Provider(
                            self.name(), host=self.model.access.ssh
                        ),
                    }
                ),
            ),
        )
        self.child_opts = ResourceOptions(parent=self)

        self.network = network_resource

        self.extractor_args = ExtractorArgs.from_host(
            global_args, network_resource.hostnames, config, self
        )
        self.docker = DockerResource(
            self.name(),
            opts=self.child_opts,
            extractor_args=self.extractor_args,
        )

        self.services: dict[str, ServiceResourceBase] = {}

        FileVolumeProxy.pull_image(self.model.access.ssh)

        self.HOSTS[self.name()] = self

    def __str__(self) -> str:
        return self.name()

    @classmethod
    def name(cls) -> str:
        if cls._host_name is None:
            cls._host_name = to_snake(cls.__name__.removesuffix("Host")).replace(
                "_", "-"
            )
        return cls._host_name
