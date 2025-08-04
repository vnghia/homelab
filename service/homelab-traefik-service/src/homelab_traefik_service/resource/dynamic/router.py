from __future__ import annotations

import typing

from homelab_docker.extract import ExtractorArgs
from pulumi import ResourceOptions

from ...model.dynamic.http import TraefikDynamicHttpModelBuilder
from . import TraefikDynamicConfigResource

if typing.TYPE_CHECKING:
    from ... import TraefikService


class TraefikDynamicRouterConfigResource(
    TraefikDynamicConfigResource, module="traefik", name="DynamicConfig"
):
    def __init__(
        self,
        resource_name: str | None,
        model: TraefikDynamicHttpModelBuilder,
        *,
        opts: ResourceOptions,
        traefik_service: TraefikService,
        extractor_args: ExtractorArgs,
    ) -> None:
        super().__init__(
            resource_name,
            model,
            opts=opts,
            traefik_service=traefik_service,
            extractor_args=extractor_args,
        )
