from __future__ import annotations

import typing

from homelab_docker.resource.service import ServiceResourceBase
from homelab_pydantic import HomelabServiceConfigDict
from pulumi import ResourceOptions

from .. import TraefikService
from ..model.dynamic.http import TraefikDynamicHttpModel
from ..model.dynamic.middleware import TraefikDynamicMiddlewareFullModel

if typing.TYPE_CHECKING:
    from ..resource.dynamic import TraefikDynamicConfigResource


class TraefikServiceConfig(
    HomelabServiceConfigDict[
        TraefikDynamicHttpModel | TraefikDynamicMiddlewareFullModel
    ]
):
    NONE_KEY = TraefikService.name()

    def build_resources(
        self,
        *,
        opts: ResourceOptions | None,
        main_service: ServiceResourceBase,
        traefik_service: TraefikService,
    ) -> dict[str | None, TraefikDynamicConfigResource]:
        return {
            name: model.build_resource(
                name,
                opts=opts,
                main_service=main_service,
                traefik_service=traefik_service,
            )
            for name, model in self.root.items()
        }
