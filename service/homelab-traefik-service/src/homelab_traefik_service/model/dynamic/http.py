from __future__ import annotations

import typing
from typing import Any, ClassVar

from homelab_docker.extract import ExtractorArgs
from homelab_docker.extract.global_ import GlobalExtractor
from homelab_traefik_config.model.dynamic.http import TraefikDynamicHttpModel
from homelab_traefik_config.model.dynamic.type import TraefikDynamicType
from pulumi import Output, ResourceOptions

from .base import TraefikDynamicBaseModelBuilder
from .tls import TraefikDynamicTlsModelBuilder

if typing.TYPE_CHECKING:
    from ... import TraefikService
    from ...resource.dynamic.router import TraefikDynamicRouterConfigResource


class TraefikDynamicHttpModelBuilder(
    TraefikDynamicBaseModelBuilder[TraefikDynamicHttpModel]
):
    TYPE: ClassVar[TraefikDynamicType] = TraefikDynamicType.HTTP

    LOCAL_MIDDLEWARE_NAMES: ClassVar[list[str]] = ["local"]
    LOCAL_MIDDLEWARES: ClassVar[list[str] | None] = None

    def build_rule(
        self,
        record: str,
        router_name: str,
        traefik_service: TraefikService,
        extractor_args: ExtractorArgs,
    ) -> Output[str]:
        root = self.root
        hostname = self.get_host(
            record, root.hostname, router_name, traefik_service, extractor_args
        )
        return Output.all(
            *(
                [Output.format("Host(`{}`)", hostname)]
                + (
                    [
                        Output.format(
                            "PathPrefix(`{}`)",
                            GlobalExtractor(root.prefix).extract_str(extractor_args),
                        ),
                    ]
                    if root.prefix
                    else []
                )
                + [
                    GlobalExtractor(rule).extract_str(extractor_args)
                    for rule in root.rules
                ]
            )
        ).apply(lambda extractor_args: " && ".join(extractor_args))

    def build_tls(
        self, traefik_service: TraefikService, extractor_args: ExtractorArgs
    ) -> tuple[dict[str, Any] | None, dict[str, Any]]:
        root = self.root
        main_service = extractor_args.service

        tls = None
        tls_router: dict[str, Any] = {}
        if root.tls:
            tls = TraefikDynamicTlsModelBuilder(root.tls).to_data(
                traefik_service, extractor_args
            )
            tls_router["options"] = main_service.add_service_name(root.tls.name)
        else:
            tls_router["certResolver"] = traefik_service.static.CERT_RESOLVER

        return (tls, tls_router)

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
