from __future__ import annotations

import typing
from typing import Any

from homelab_docker.extract import GlobalExtract
from homelab_docker.resource.service import ServiceResourceBase
from homelab_pydantic import HomelabRootModel
from homelab_traefik_config.model.dynamic.middleware import (
    TraefikDynamicMiddlewareFullModel,
    TraefikDynamicMiddlewareModel,
)
from pulumi import ResourceOptions

if typing.TYPE_CHECKING:
    from ... import TraefikService
    from ...resource.dynamic.middleware import TraefikDynamicMiddlwareConfigResource


class TraefikDynamicMiddlewareFullModelBuilder(
    HomelabRootModel[TraefikDynamicMiddlewareFullModel]
):
    def to_section(
        self, main_service: ServiceResourceBase, traefik_service: TraefikService
    ) -> dict[str, Any]:
        root = self.root

        name = main_service.add_service_name(root.name)
        section = GlobalExtract.extract_recursively(root.data, main_service)

        if root.plugin:
            traefik_service.config.plugins[root.plugin]
            return {name: {"plugin": {root.plugin: section}}}
        else:
            return {name: section}

    def to_data(
        self, main_service: ServiceResourceBase, traefik_service: TraefikService
    ) -> dict[str, Any]:
        return {"http": {"middlewares": self.to_section(main_service, traefik_service)}}

    def build_resource(
        self,
        resource_name: str | None,
        *,
        opts: ResourceOptions | None,
        main_service: ServiceResourceBase,
        traefik_service: TraefikService,
    ) -> TraefikDynamicMiddlwareConfigResource:
        from ...resource.dynamic.middleware import TraefikDynamicMiddlwareConfigResource

        return TraefikDynamicMiddlwareConfigResource(
            resource_name,
            self,
            opts=opts,
            main_service=main_service,
            traefik_service=traefik_service,
        )


class TraefikDynamicMiddlewareModelBuilder(
    HomelabRootModel[TraefikDynamicMiddlewareModel]
):
    def get_name(self, main_service: ServiceResourceBase) -> str:
        root = self.root.root

        return (
            main_service.add_service_name(root.name)
            if isinstance(root, TraefikDynamicMiddlewareFullModel)
            else root
        )

    def to_section(
        self, main_service: ServiceResourceBase, traefik_service: TraefikService
    ) -> dict[str, Any]:
        root = self.root.root

        return (
            TraefikDynamicMiddlewareFullModelBuilder(root).to_section(
                main_service, traefik_service
            )
            if isinstance(root, TraefikDynamicMiddlewareFullModel)
            else {}
        )
