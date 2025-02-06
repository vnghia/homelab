from homelab_config import Config
from homelab_docker.model.container.model import ContainerModelGlobalArgs
from homelab_docker.model.service import ServiceModel
from homelab_docker.resource.docker import DockerResource
from pulumi import ComponentResource, ResourceOptions
from pydantic import BaseModel
from pydantic_extra_types.timezone_name import TimeZoneName

from .dozzle import DozzleService
from .tailscale import TailscaleService
from .traefik import TraefikService
from .traefik.config import TraefikConfig


class ServiceConfig(BaseModel):
    tailscale: ServiceModel[None]
    traefik: ServiceModel[TraefikConfig]
    dozzle: ServiceModel[None]


class Service(ComponentResource):
    RESOURCE_NAME = "service"

    def __init__(
        self,
        config: Config[ServiceConfig],
        *,
        timezone: TimeZoneName,
        docker_resource: DockerResource,
        opts: ResourceOptions | None,
    ) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.services_config = config.docker.services
        self.container_model_global_args = ContainerModelGlobalArgs(
            timezone=timezone,
            docker_resource=docker_resource,
            project_labels=Config.PROJECT_LABELS,
        )

        self.tailscale = TailscaleService(
            self.services_config.tailscale,
            opts=self.child_opts,
            container_model_global_args=self.container_model_global_args,
        )
        self.traefik = TraefikService(
            self.services_config.traefik,
            opts=self.child_opts,
            network_config=config.network,
            container_model_global_args=self.container_model_global_args,
            tailscale_service=self.tailscale,
        )
        self.dozzle = DozzleService(
            self.services_config.dozzle,
            opts=self.child_opts,
            network_config=config.network,
            container_model_global_args=self.container_model_global_args,
            traefik_static_config=self.traefik.static,
        )
