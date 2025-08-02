import pulumi_docker as docker
import pulumi_docker_build as docker_build
from homelab_network.resource.network import NetworkResource
from pulumi import ComponentResource, ResourceOptions
from pydantic.alias_generators import to_snake

from ..config import DockerNoServiceConfig
from ..resource.file import FileVolumeProxy
from ..resource.service import ServiceResourceBase


class HostResourceBase(ComponentResource):
    def __init__(
        self,
        config: DockerNoServiceConfig,
        *,
        opts: ResourceOptions | None,
        project_prefix: str,
        network_resource: NetworkResource,
    ) -> None:
        self.config = config

        super().__init__(
            self.name(),
            self.name(),
            None,
            ResourceOptions.merge(
                opts,
                ResourceOptions(
                    providers={
                        "docker": docker.Provider(
                            self.name(), host=self.config.host.ssh
                        ),
                        "docker-build": docker_build.Provider(
                            self.name(), host=self.config.host.ssh
                        ),
                    }
                ),
            ),
        )
        self.child_opts = ResourceOptions(parent=self)

        self.project_prefix = project_prefix
        self.network = network_resource
        self.hostname = "{}-{}".format(self.project_prefix, self.name())
        self.services: dict[str, ServiceResourceBase] = {}

        FileVolumeProxy.pull_image(self.config.host.ssh)

    def __str__(self) -> str:
        return self.name()

    @classmethod
    def name(cls) -> str:
        return to_snake(cls.__name__.removesuffix("Host")).replace("_", "-")
