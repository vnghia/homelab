from __future__ import annotations

import typing
from typing import Any, ClassVar

from homelab_docker.extract import ExtractorArgs
from homelab_traefik_config.model.dynamic.tcp import TraefikDynamicTcpModel
from homelab_traefik_config.model.dynamic.type import TraefikDynamicType
from pulumi import Output, ResourceOptions

from .base import TraefikDynamicBaseModelBuilder

if typing.TYPE_CHECKING:
    from ... import TraefikService
    from ...resource.dynamic.router import TraefikDynamicRouterConfigResource


class TraefikDynamicTcpModelBuilder(
    TraefikDynamicBaseModelBuilder[TraefikDynamicTcpModel]
):
    TYPE: ClassVar[TraefikDynamicType] = TraefikDynamicType.TCP

    LOCAL_MIDDLEWARE_NAMES: ClassVar[list[str]] = ["local-tcp"]
    LOCAL_MIDDLEWARES: ClassVar[list[str] | None] = None

    def build_rule(
        self,
        record: str,
        router_name: str,
        traefik_service: TraefikService,
        extractor_args: ExtractorArgs,
    ) -> Output[str]:
        root = self.root
        hostsni = traefik_service.extractor_args.hostnames[record][root.hostsni]
        return Output.from_input("HostSNI(`{}`)".format(hostsni.value))

    def build_tls(
        self, traefik_service: TraefikService, extractor_args: ExtractorArgs
    ) -> tuple[dict[str, Any] | None, dict[str, Any]]:
        return (None, {"passthrough": True})

    def build_resource(
        self,
        resource_name: str | None,
        *,
        opts: ResourceOptions,
        traefik_service: TraefikService,
        extractor_args: ExtractorArgs,
    ) -> TraefikDynamicRouterConfigResource:
        from ...resource.dynamic.router import TraefikDynamicRouterConfigResource

        resource = TraefikDynamicRouterConfigResource(
            resource_name,
            self,
            opts=opts,
            traefik_service=traefik_service,
            extractor_args=extractor_args,
        )
        traefik_service.routers[extractor_args.service.name()][resource_name] = resource
        return resource
