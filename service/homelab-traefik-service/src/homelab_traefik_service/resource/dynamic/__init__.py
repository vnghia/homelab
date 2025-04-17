from __future__ import annotations

import typing

from homelab_docker.resource.file.config import ConfigFileResource, TomlDumper
from homelab_docker.resource.service import ServiceResourceBase
from pulumi import ResourceOptions

from ...model.dynamic.http import TraefikDynamicHttpModelBuilder
from ...model.dynamic.middleware import TraefikDynamicMiddlewareBuildModelBuilder
from . import schema

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
        model: TraefikDynamicHttpModelBuilder
        | TraefikDynamicMiddlewareBuildModelBuilder,
        *,
        opts: ResourceOptions | None,
        main_service: ServiceResourceBase,
        traefik_service: TraefikService,
    ) -> None:
        self.name = main_service.add_service_name(model.root.name)
        super().__init__(
            resource_name or self.name,
            opts=opts,
            volume_path=traefik_service.get_dynamic_config_volume_path(self.name),
            data=model.to_data(main_service, traefik_service),
            volume_resource=traefik_service.docker_resource_args.volume,
        )
