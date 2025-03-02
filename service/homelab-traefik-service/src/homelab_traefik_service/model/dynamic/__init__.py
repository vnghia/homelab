from __future__ import annotations

import typing

from homelab_docker.resource.service import ServiceResourceBase
from homelab_pydantic import HomelabRootModel
from homelab_traefik_config.model.dynamic import TraefikDynamicModel
from homelab_traefik_config.model.dynamic.http import TraefikDynamicHttpModel
from pulumi import ResourceOptions

from .http import TraefikDynamicHttpModelBuilder
from .middleware import TraefikDynamicMiddlewareFullModelBuilder

if typing.TYPE_CHECKING:
    from ... import TraefikService
    from ...resource.dynamic import TraefikDynamicConfigResource


class TraefikDynamicModelBuilder(HomelabRootModel[TraefikDynamicModel]):
    def build_resource(
        self,
        resource_name: str | None,
        *,
        opts: ResourceOptions | None,
        main_service: ServiceResourceBase,
        traefik_service: TraefikService,
    ) -> TraefikDynamicConfigResource:
        from ...resource.dynamic import TraefikDynamicConfigResource

        root = self.root.root

        return TraefikDynamicConfigResource(
            resource_name,
            TraefikDynamicHttpModelBuilder(root)
            if isinstance(root, TraefikDynamicHttpModel)
            else TraefikDynamicMiddlewareFullModelBuilder(root),
            opts=opts,
            main_service=main_service,
            traefik_service=traefik_service,
        )
