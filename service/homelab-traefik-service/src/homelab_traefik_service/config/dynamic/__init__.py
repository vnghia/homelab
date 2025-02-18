from __future__ import annotations

import typing

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
        resource_name: str | None,
        config: TraefikHttpDynamicConfig | TraefikDynamicMiddlewareFullConfig,
        *,
        opts: ResourceOptions | None,
        traefik_service: TraefikService,
    ):
        self.name = config.name
        super().__init__(
            resource_name or self.name,
            opts=opts,
            container_volume_path=traefik_service.get_dynamic_config_container_volume_path(
                self.name
            ),
            data=config.to_data(traefik_service),
            volume_resource=traefik_service.docker_resource_args.volume,
        )
