from homelab_docker.config import DockerConfig
from homelab_docker.config.service import ServiceConfigBase
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource.host import HostResourceBase
from homelab_extra_service import ExtraService
from homelab_extra_service.config import ExtraConfig
from homelab_network.resource.network import NetworkResource
from pulumi import ResourceOptions
from pydantic.alias_generators import to_snake

from ..docker import Docker


class HostBase[T: ServiceConfigBase](HostResourceBase):
    def __init__(
        self,
        config: DockerConfig[T],
        *,
        opts: ResourceOptions | None,
        project_prefix: str,
        network_resource: NetworkResource,
    ) -> None:
        super().__init__(
            config,
            opts=opts,
            project_prefix=project_prefix,
            network_resource=network_resource,
        )

        self.docker = Docker(
            config,
            opts=self.child_opts,
            project_prefix=self.project_prefix,
            host=self.name(),
            hostnames=self.network.hostnames,
        )

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
