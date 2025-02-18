from __future__ import annotations

import typing
from typing import Any

from homelab_pydantic import HomelabBaseModel, HomelabRootModel
from pulumi import ResourceOptions

if typing.TYPE_CHECKING:
    from ... import TraefikService
    from ..dynamic import TraefikDynamicConfigResource


class TraefikDynamicMiddlewareFullConfig(HomelabBaseModel):
    name: str
    data: Any

    def to_data(self, _traefik_service: TraefikService) -> dict[str, Any]:
        return {"http": {"middlewares": {self.name: self.data}}}

    def build_resource(
        self,
        resource_name: str | None,
        *,
        opts: ResourceOptions | None,
        traefik_service: TraefikService,
    ) -> TraefikDynamicConfigResource:
        from homelab_traefik_service.config.dynamic import TraefikDynamicConfigResource

        return TraefikDynamicConfigResource(
            resource_name, self, opts=opts, traefik_service=traefik_service
        )


class TraefikDynamicMiddlewareConfig(
    HomelabRootModel[str | TraefikDynamicMiddlewareFullConfig]
):
    @property
    def name(self) -> str:
        root = self.root
        return (
            root.name if isinstance(root, TraefikDynamicMiddlewareFullConfig) else root
        )

    @property
    def data(self) -> Any:
        root = self.root
        return (
            root.data if isinstance(root, TraefikDynamicMiddlewareFullConfig) else None
        )
