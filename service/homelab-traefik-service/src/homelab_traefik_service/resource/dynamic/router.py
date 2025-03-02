from __future__ import annotations

import typing

from homelab_docker.resource.service import ServiceResourceBase
from pulumi import ResourceOptions

from ...model.dynamic.http import TraefikDynamicHttpModelBuilder
from . import TraefikDynamicConfigResource

if typing.TYPE_CHECKING:
    from ... import TraefikService


class TraefikDynamicRouterConfigResource(
    TraefikDynamicConfigResource, module="traefik", name="DynamicConfig"
):
    def __init__(
        self,
        resource_name: str | None,
        model: TraefikDynamicHttpModelBuilder,
        *,
        opts: ResourceOptions | None,
        main_service: ServiceResourceBase,
        traefik_service: TraefikService,
    ):
        super().__init__(
            resource_name,
            model,
            opts=opts,
            main_service=main_service,
            traefik_service=traefik_service,
        )
