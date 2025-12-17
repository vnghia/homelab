from __future__ import annotations

import pulumi_docker as docker
import pulumi_docker_build as docker_build
from homelab_global.resource import GlobalResource
from homelab_network.resource.network import NetworkResource
from pulumi import ComponentResource, ResourceOptions
from pydantic.alias_generators import to_snake

from ..client import DockerClient
from ..config.host import HostServiceModelConfig
from ..extract import ExtractorArgs
from ..resource.docker import DockerResource
from ..resource.service import ServiceResourceBase


class HostResourceBase(ComponentResource):
    _host_name: str | None = None

    HOSTS: dict[str, HostResourceBase] = {}

    def __init__(
        self,
        name: str,
        *,
        opts: ResourceOptions | None,
        global_resource: GlobalResource,
        network_resource: NetworkResource,
        config: HostServiceModelConfig,
    ) -> None:
        self.model = config[name]

        self.docker_host = self.model.access.ssh
        self.docker_client = DockerClient(self.docker_host)
        self.docker_client.pull_utility_image()

        self.service_users = {
            service_name: service_model.user.model(self.model.users)
            for service_name, service_model in self.model.services.items()
        }

        super().__init__(
            self.name,
            self.name,
            None,
            ResourceOptions.merge(
                opts,
                ResourceOptions(
                    providers={
                        "docker": docker.Provider(self.name, host=self.docker_host),
                        "docker-build": docker_build.Provider(
                            self.name, host=self.docker_host
                        ),
                    }
                ),
            ),
        )
        self.child_opts = ResourceOptions(parent=self)

        self.network = network_resource

        self.extractor_args = ExtractorArgs.from_host(global_resource, config, self)
        self.docker = DockerResource(
            self.name,
            opts=self.child_opts,
            extractor_args=self.extractor_args,
        )

        self.services: dict[str, ServiceResourceBase] = {}

        self.HOSTS[self.name] = self

    @property
    def name(self) -> str:
        return self.model.name

    @classmethod
    def instance_name(cls) -> str:
        if cls._host_name is None:
            cls._host_name = to_snake(cls.__name__.removesuffix("Host")).replace(
                "_", "-"
            )
        return cls._host_name
