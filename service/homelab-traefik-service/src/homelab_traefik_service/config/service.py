from __future__ import annotations

import typing
from typing import Self

from homelab_docker.resource.service import ServiceResourceBase
from homelab_pydantic import HomelabRootModel
from pulumi import ResourceOptions
from pydantic import model_validator

from ..model.dynamic.http import TraefikDynamicHttpModel
from ..model.dynamic.middleware import TraefikDynamicMiddlewareFullModel

if typing.TYPE_CHECKING:
    from .. import TraefikService
    from ..resource.dynamic import TraefikDynamicConfigResource


class TraefikServiceConfig(
    HomelabRootModel[
        dict[str | None, TraefikDynamicHttpModel | TraefikDynamicMiddlewareFullModel]
    ]
):
    @model_validator(mode="after")
    def set_none_key(self) -> Self:
        from .. import TraefikService

        return self.model_construct(
            root={
                TraefikService.get_key(name): model for name, model in self.root.items()
            }
        )

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
