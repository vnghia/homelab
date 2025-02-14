import typing

from homelab_docker.model.file.config import ConfigFileModel
from homelab_docker.resource.file.config import ConfigFileResource
from pulumi import ResourceOptions
from pydantic import HttpUrl

from homelab_traefik_service.config.dynamic.middleware import (
    TraefikDynamicMiddlewareFullConfig,
)

from .http import TraefikHttpDynamicConfig

if typing.TYPE_CHECKING:
    from ... import TraefikService


class TraefikDynamicConfigResource(
    ConfigFileResource, module="traefik", name="DynamicConfig"
):
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
                traefik_service.get_dynamic_container_volume_path(self.name),
                config.to_data(traefik_service),
                schema_url=HttpUrl(
                    "https://json.schemastore.org/traefik-v3-file-provider.json"
                ),
            ),
            resource_name or self.name,
            opts=opts,
            volume_resource=traefik_service.docker_resource_args.volume,
        )
