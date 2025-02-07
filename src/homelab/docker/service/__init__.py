from homelab_config import Config
from homelab_docker.config.database import DatabaseConfig
from homelab_docker.config.service import ServiceConfigBase
from homelab_docker.model.container.model import ContainerModelGlobalArgs
from homelab_docker.model.service import ServiceModel
from homelab_docker.resource.docker import DockerResource
from homelab_tailscale_service import TailscaleService
from pulumi import ComponentResource, ResourceOptions
from pydantic_extra_types.timezone_name import TimeZoneName

from homelab.docker.service.nghe import NgheService

from .dozzle import DozzleService
from .nghe.config import NgheConfig
from .traefik import TraefikService
from .traefik.config import TraefikConfig


class ServiceConfig(ServiceConfigBase):
    tailscale: ServiceModel[None]
    traefik: ServiceModel[TraefikConfig]
    dozzle: ServiceModel[None]
    nghe: ServiceModel[NgheConfig]

    @property
    def databases(self) -> dict[str, DatabaseConfig]:
        return {
            field: service.databases
            for field, service in self
            if isinstance(service, ServiceModel) and service.databases
        }


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
            hostname=Config.get_name(None, project=True, stack=True),
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
            container_model_global_args=self.container_model_global_args,
            traefik_static_config=self.traefik.static,
        )
        self.nghe = NgheService(
            self.services_config.nghe,
            opts=self.child_opts,
            s3_integration_config=config.integration.s3,
            container_model_global_args=self.container_model_global_args,
            traefik_static_config=self.traefik.static,
        )
