import typing

from homelab_docker.model.file.config import ConfigFileModel
from homelab_docker.resource.file.config import ConfigFileResource, TomlDumper
from pulumi import ResourceOptions

from homelab_traefik_service.config.dynamic.middleware import (
    TraefikDynamicMiddlewareFullConfig,
)

from . import schema
from .http import TraefikHttpDynamicConfig

if typing.TYPE_CHECKING:
    from ... import TraefikService


class TraefikDynamicConfigResource(
    ConfigFileResource[schema.Model], module="traefik", name="DynamicConfig"
):
    validator = schema.Model
    dumper = TomlDumper[schema.Model]

    def __init__(
        self,
        config: TraefikHttpDynamicConfig | TraefikDynamicMiddlewareFullConfig,
        resource_name: str | None,
        *,
        opts: ResourceOptions | None,
        traefik_service: "TraefikService",
    ):
        self.name = config.name
        super().__init__(
            ConfigFileModel(
                traefik_service.get_dynamic_config_container_volume_path(self.name),
                config.to_data(traefik_service),
            ),
            resource_name or self.name,
            opts=opts,
            volume_resource=traefik_service.docker_resource_args.volume,
        )
