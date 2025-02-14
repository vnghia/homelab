import typing
from typing import Any

from homelab_docker.resource.volume import VolumeResource
from pulumi import ResourceOptions
from pydantic import BaseModel, RootModel

if typing.TYPE_CHECKING:
    from ... import TraefikService
    from ..dynamic import TraefikDynamicConfigResource


class TraefikDynamicMiddlewareFullConfig(BaseModel):
    name: str
    data: Any

    def to_data(self, _traefik_service: "TraefikService") -> dict[str, Any]:
        return {"http": {"middlewares": {self.name: self.data}}}

    def build_resource(
        self,
        resource_name: str | None,
        *,
        opts: ResourceOptions | None,
        traefik_service: "TraefikService",
        volume_resource: VolumeResource,
    ) -> "TraefikDynamicConfigResource":
        from homelab_traefik_service.config.dynamic import TraefikDynamicConfigResource

        return TraefikDynamicConfigResource(
            self,
            resource_name,
            opts=opts,
            traefik_service=traefik_service,
            volume_resource=volume_resource,
        )


class TraefikDynamicMiddlewareConfig(
    RootModel[str | TraefikDynamicMiddlewareFullConfig]
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
