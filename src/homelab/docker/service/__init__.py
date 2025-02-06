from homelab_config import constant
from homelab_docker.model.container import ContainerModelGlobalArgs
from homelab_docker.model.service import ServiceModel
from homelab_docker.resource.global_ import GlobalResource
from pulumi import ComponentResource, ResourceOptions
from pydantic import BaseModel
from pydantic_extra_types.timezone_name import TimeZoneName

from .dozzle import Dozzle
from .tailscale import Tailscale
from .traefik import TraefikConfig


class ServiceConfig(BaseModel):
    tailscale: ServiceModel[None]
    traefik: ServiceModel[TraefikConfig]
    dozzle: ServiceModel[None]


class Service(ComponentResource):
    RESOURCE_NAME = "service"

    def __init__(
        self,
        config: ServiceConfig,
        *,
        timezone: TimeZoneName,
        global_resource: GlobalResource,
        opts: ResourceOptions | None,
    ) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.container_model_global_args = ContainerModelGlobalArgs(
            timezone=timezone,
            global_resource=global_resource,
            project_labels=constant.PROJECT_LABELS,
        )

        self.tailscale = Tailscale(
            config.tailscale,
            opts=self.child_opts,
            container_model_global_args=self.container_model_global_args,
        )
        self.dozzle = Dozzle(
            config.dozzle,
            opts=self.child_opts,
            container_model_global_args=self.container_model_global_args,
        )
