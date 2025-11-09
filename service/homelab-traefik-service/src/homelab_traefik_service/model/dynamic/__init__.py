from __future__ import annotations

import typing

from homelab_docker.extract import ExtractorArgs
from homelab_pydantic import HomelabRootModel
from homelab_traefik_config.model.dynamic import TraefikDynamicModel
from homelab_traefik_config.model.dynamic.http import TraefikDynamicHttpModel
from homelab_traefik_config.model.dynamic.tcp import TraefikDynamicTcpModel
from pulumi import ResourceOptions

from .http import TraefikDynamicHttpModelBuilder
from .middleware import TraefikDynamicMiddlewareBuildModelBuilder
from .tcp import TraefikDynamicTcpModelBuilder

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

        builder: (
            TraefikDynamicHttpModelBuilder
            | TraefikDynamicTcpModelBuilder
            | TraefikDynamicMiddlewareBuildModelBuilder
            | None
        ) = None
        if isinstance(root, TraefikDynamicHttpModel):
            builder = TraefikDynamicHttpModelBuilder(root)
        elif isinstance(root, TraefikDynamicTcpModel):
            builder = TraefikDynamicTcpModelBuilder(root)
        else:
            builder = TraefikDynamicMiddlewareBuildModelBuilder(root)

        return builder.build_resource(
            resource_name,
            opts=opts,
            traefik_service=traefik_service,
            extractor_args=extractor_args,
        )
