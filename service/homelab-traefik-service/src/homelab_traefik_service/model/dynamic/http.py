from __future__ import annotations

import operator
import typing
from functools import reduce
from typing import Any, ClassVar

from homelab_docker.extract import ExtractorArgs
from homelab_docker.extract.global_ import GlobalExtractor
from homelab_pydantic import HomelabRootModel
from homelab_traefik_config.model.dynamic.http import TraefikDynamicHttpModel
from homelab_traefik_config.model.dynamic.middleware import (
    TraefikDynamicMiddlewareModel,
    TraefikDynamicMiddlewareUseModel,
)
from homelab_traefik_config.model.dynamic.service import TraefikDynamicServiceType
from pulumi import Output, ResourceOptions

from .middleware import TraefikDynamicMiddlewareModelBuilder
from .service import (
    TraefikDynamicServiceFullModelBuilder,
    TraefikDynamicServiceModelBuilder,
)

if typing.TYPE_CHECKING:
    from ... import TraefikService
    from ...resource.dynamic.router import TraefikDynamicRouterConfigResource


class TraefikDynamicHttpModelBuilder(HomelabRootModel[TraefikDynamicHttpModel]):
    LOCAL_MIDDLEWARE: ClassVar[str] = "local"

    def to_data(
        self, traefik_service: TraefikService, extractor_args: ExtractorArgs
    ) -> dict[str, Any]:
        root = self.root
        traefik_config = traefik_service.config
        main_service = extractor_args.service

        router_name = main_service.add_service_name(root.name)
        hostname = traefik_service.extractor_args.hostnames[root.record][
            root.hostname or router_name
        ]

        service = TraefikDynamicServiceModelBuilder(root.service).to_service_name(
            router_name
        )
        rule = Output.all(
            *(
                [Output.format("Host(`{}`)", hostname.value)]
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

        local_middlewares = [
            TraefikDynamicMiddlewareModelBuilder(middleware).get_name(
                traefik_service, extractor_args
            )
            for middleware in [
                TraefikDynamicMiddlewareModel(
                    TraefikDynamicMiddlewareUseModel(
                        service=traefik_service.name(), name=self.LOCAL_MIDDLEWARE
                    )
                ),
            ]
        ]

        entrypoint = traefik_config.entrypoint.mapping[root.record]
        entrypoint_config = traefik_config.entrypoint.config[entrypoint]
        entrypoint_middlewares = [
            TraefikDynamicMiddlewareModelBuilder(
                TraefikDynamicMiddlewareModel(
                    TraefikDynamicMiddlewareUseModel(
                        service=traefik_service.name(), name=middleware
                    )
                )
            ).get_name(traefik_service, extractor_args)
            for middleware in entrypoint_config.middlewares
        ]
        service_middlewares = [
            TraefikDynamicMiddlewareModelBuilder(middleware).get_name(
                traefik_service, extractor_args
            )
            for middleware in root.middlewares
        ]
        all_middlewares = entrypoint_middlewares + service_middlewares

        data: dict[str, Any] = {
            "http": {
                "routers": {
                    router_name: {
                        "service": service,
                        "entryPoints": [entrypoint],
                        "rule": rule,
                        "tls": {"certResolver": traefik_service.static.CERT_RESOLVER},
                    }
                    | ({"middlewares": all_middlewares} if all_middlewares else {})
                }
                | (
                    {
                        "{}-local".format(router_name): {
                            "service": service,
                            "entryPoints": [traefik_config.entrypoint.local_entrypoint],
                            "rule": rule,
                            "tls": {
                                "certResolver": traefik_service.static.CERT_RESOLVER
                            },
                            "middlewares": local_middlewares + service_middlewares,
                        }
                    }
                    if entrypoint_config.local
                    else {}
                ),
            }
        }

        service_full = TraefikDynamicServiceModelBuilder(root.service).full
        if service_full:
            data["http"]["services"] = TraefikDynamicServiceFullModelBuilder(
                service_full
            ).to_service(TraefikDynamicServiceType.HTTP, router_name, extractor_args)

        middlewares: dict[str, Any] = reduce(
            operator.or_,
            [
                TraefikDynamicMiddlewareModelBuilder(middleware).to_section(
                    traefik_service, extractor_args
                )
                for middleware in root.middlewares
            ],
            {},
        )
        if middlewares:
            data["http"]["middlewares"] = middlewares

        return data

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
