from __future__ import annotations

import typing
from typing import Any

from homelab_docker.model.service.extract import ServiceExtract
from homelab_docker.resource.service import ServiceResourceBase
from homelab_pydantic import HomelabBaseModel, HomelabRootModel
from pulumi import ResourceOptions

if typing.TYPE_CHECKING:
    from ... import TraefikService
    from ...resource.dynamic import TraefikDynamicConfigResource


class TraefikDynamicMiddlewareFullModel(HomelabBaseModel):
    name: str
    data: Any

    def to_section(self, main_service: ServiceResourceBase) -> dict[str, Any]:
        return {
            main_service.add_service_name(
                self.name
            ): ServiceExtract.extract_recursively(self.data, main_service)
        }

    def to_data(
        self, main_service: ServiceResourceBase, _traefik_service: TraefikService
    ) -> dict[str, Any]:
        return {"http": {"middlewares": self.to_section(main_service)}}

    def build_resource(
        self,
        resource_name: str | None,
        *,
        opts: ResourceOptions | None,
        main_service: ServiceResourceBase,
        traefik_service: TraefikService,
    ) -> TraefikDynamicConfigResource:
        from ...resource.dynamic import TraefikDynamicConfigResource

        return TraefikDynamicConfigResource(
            resource_name,
            self,
            opts=opts,
            main_service=main_service,
            traefik_service=traefik_service,
        )


class TraefikDynamicMiddlewareModel(
    HomelabRootModel[str | TraefikDynamicMiddlewareFullModel]
):
    def get_name(self, main_service: ServiceResourceBase) -> str:
        root = self.root
        return (
            main_service.add_service_name(root.name)
            if isinstance(root, TraefikDynamicMiddlewareFullModel)
            else root
        )

    def to_section(self, main_service: ServiceResourceBase) -> dict[str, Any]:
        root = self.root
        return (
            root.to_section(main_service)
            if isinstance(root, TraefikDynamicMiddlewareFullModel)
            else {}
        )
