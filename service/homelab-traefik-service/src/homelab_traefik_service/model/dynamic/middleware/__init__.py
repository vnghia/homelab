from __future__ import annotations

import typing
from typing import Any

from homelab_docker.extract import ExtractorArgs
from homelab_docker.extract.global_ import GlobalExtractor
from homelab_pydantic import HomelabRootModel
from homelab_traefik_config.model.dynamic.middleware import (
    TraefikDynamicMiddlewareBuildModel,
    TraefikDynamicMiddlewareModel,
)
from homelab_traefik_config.model.dynamic.type import TraefikDynamicType
from pulumi import ResourceOptions

if typing.TYPE_CHECKING:
    from .... import TraefikService
    from ....resource.dynamic.middleware import TraefikDynamicMiddlwareConfigResource


class TraefikDynamicMiddlewareBuildModelBuilder(
    HomelabRootModel[TraefikDynamicMiddlewareBuildModel]
):
    def to_section(
        self, traefik_service: TraefikService, extractor_args: ExtractorArgs
    ) -> dict[str, Any]:
        root = self.root

        name = extractor_args.service.add_service_name(root.name)
        section = GlobalExtractor.extract_recursively(root.data, extractor_args)

        if root.plugin:
            traefik_service.config.plugins[root.plugin]
            return {name: {"plugin": {root.plugin: section}}}
        return {name: section}

    def to_data(
        self, traefik_service: TraefikService, extractor_args: ExtractorArgs
    ) -> dict[str, Any]:
        return {
            self.root.type: {
                "middlewares": self.to_section(traefik_service, extractor_args)
            }
        }

    def build_resource(
        self,
        resource_name: str | None,
        *,
        opts: ResourceOptions,
        traefik_service: TraefikService,
        extractor_args: ExtractorArgs,
    ) -> TraefikDynamicMiddlwareConfigResource:
        from ....resource.dynamic.middleware import (
            TraefikDynamicMiddlwareConfigResource,
        )

        resource = TraefikDynamicMiddlwareConfigResource(
            resource_name,
            self,
            opts=opts,
            traefik_service=traefik_service,
            extractor_args=extractor_args,
        )
        traefik_service.middlewares[extractor_args.service.name()][self.root.type][
            resource_name
        ] = resource
        return resource


class TraefikDynamicMiddlewareModelBuilder(
    HomelabRootModel[TraefikDynamicMiddlewareModel]
):
    def get_name(
        self,
        traefik_service: TraefikService,
        extractor_args: ExtractorArgs,
        type: TraefikDynamicType,
    ) -> str:
        root = self.root.root
        service = extractor_args.service

        return (
            service.add_service_name(root.name)
            if isinstance(root, TraefikDynamicMiddlewareBuildModel)
            else traefik_service.middlewares[root.service or service.name()][type][
                root.name
            ].name
        )

    def to_section(
        self, traefik_service: TraefikService, extractor_args: ExtractorArgs
    ) -> dict[str, Any]:
        root = self.root.root

        return (
            TraefikDynamicMiddlewareBuildModelBuilder(root).to_section(
                traefik_service, extractor_args
            )
            if isinstance(root, TraefikDynamicMiddlewareBuildModel)
            else {}
        )
