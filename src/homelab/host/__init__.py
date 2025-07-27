import pulumi_docker as docker
import pulumi_docker_build as docker_build
from homelab_docker.config import DockerConfig
from homelab_docker.config.service import ServiceConfigBase
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource.file import FileVolumeProxy
from homelab_extra_service import ExtraService
from homelab_extra_service.config import ExtraConfig
from homelab_network.resource.network import NetworkResource
from pulumi import ComponentResource, ResourceOptions
from pydantic.alias_generators import to_snake

from ..docker import Docker


class HostBase[T: ServiceConfigBase](ComponentResource):
    def __init__(
        self,
        config: DockerConfig[T],
        *,
        opts: ResourceOptions | None,
        project_prefix: str,
        network_resource: NetworkResource,
    ) -> None:
        super().__init__(
            self.name(),
            self.name(),
            None,
            ResourceOptions.merge(
                opts,
                ResourceOptions(
                    providers={
                        "docker": docker.Provider(self.name(), host=config.host.ssh),
                        "docker-build": docker_build.Provider(
                            self.name(), host=config.host.ssh
                        ),
                    }
                ),
            ),
        )
        self.child_opts = ResourceOptions(parent=self)

        self.config = config
        self.project_prefix = project_prefix
        self.network = network_resource

        self.docker = Docker(
            self.config,
            opts=self.child_opts,
            project_prefix=self.project_prefix,
            hostnames=self.network.hostnames,
        )
        FileVolumeProxy.pull_image(config.host.ssh)

    def build_extra_services(self) -> None:
        self.extra_services = {
            service: type(
                "{}Service".format(service.capitalize()), (ExtraService,), {}
            )(
                model,
                opts=self.child_opts,
                docker_resource_args=self.docker.resource_args,
            ).build()
            for service, model in ExtraService.sort_depends_on(
                self.docker.services_config.extra(ServiceWithConfigModel[ExtraConfig])
            ).items()
        }

    @classmethod
    def name(cls) -> str:
        return to_snake(cls.__name__.removesuffix("Host")).replace("_", "-")
