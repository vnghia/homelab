from __future__ import annotations

import typing

from homelab_docker.extract import ExtractorArgs
from homelab_pydantic import HomelabRootModel
from homelab_traefik_config.model.dynamic import TraefikDynamicModel
from homelab_traefik_config.model.dynamic.http import TraefikDynamicHttpModel
from pulumi import ResourceOptions

from .http import TraefikDynamicHttpModelBuilder
from .middleware import TraefikDynamicMiddlewareBuildModelBuilder

if typing.TYPE_CHECKING:
    from ... import TraefikService
    from ...resource.dynamic import TraefikDynamicConfigResource


class TraefikDynamicModelBuilder(HomelabRootModel[TraefikDynamicModel]):
    def build_resource(
        self,
        resource_name: str | None,
        *,
        opts: ResourceOptions,
        traefik_service: TraefikService,
        extractor_args: ExtractorArgs,
    ) -> TraefikDynamicConfigResource:
        root = self.root.root

        return (
            TraefikDynamicHttpModelBuilder(root)
            if isinstance(root, TraefikDynamicHttpModel)
            else TraefikDynamicMiddlewareBuildModelBuilder(root)
        ).build_resource(
            resource_name,
            opts=opts,
            traefik_service=traefik_service,
            extractor_args=extractor_args,
        )
