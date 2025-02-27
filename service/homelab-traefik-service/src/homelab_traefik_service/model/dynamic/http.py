from __future__ import annotations

import operator
import typing
from functools import reduce
from typing import Any

from homelab_docker.model.service.extract import ServiceExtract
from homelab_docker.resource.service import ServiceResourceBase
from homelab_pydantic import HomelabBaseModel
from pulumi import Output, ResourceOptions

from .middleware import TraefikDynamicMiddlewareModel
from .service import TraefikDynamicServiceModel, TraefikDynamicServiceType

if typing.TYPE_CHECKING:
    from ... import TraefikService
    from ...resource.dynamic.router import TraefikDynamicRouterConfigResource


class TraefikDynamicHttpModel(HomelabBaseModel):
    name: str | None = None
    public: bool
    hostname: str | None = None
    prefix: ServiceExtract | None = None

    rules: list[ServiceExtract] = []
    service: TraefikDynamicServiceModel
    middlewares: list[TraefikDynamicMiddlewareModel] = []

    def to_data(
        self, main_service: ServiceResourceBase, traefik_service: TraefikService
    ) -> dict[str, Any]:
        entrypoint = traefik_service.config.entrypoint
        router_name = main_service.add_service_name(self.name)
        hostname = traefik_service.docker_resource_args.hostnames[self.public][
            self.hostname or router_name
        ]

        data: dict[str, Any] = {
            "http": {
                "routers": {
                    router_name: {
                        "service": self.service.to_service_name(router_name),
                        "entryPoints": [
                            entrypoint.public_https
                            if self.public
                            else entrypoint.private_https
                        ],
                        "rule": Output.all(
                            *(
                                [Output.format("Host(`{}`)", hostname)]
                                + (
                                    [
                                        Output.format(
                                            "PathPrefix(`{}`)",
                                            self.prefix.extract_str(main_service),
                                        ),
                                    ]
                                    if self.prefix
                                    else []
                                )
                                + [
                                    rule.extract_str(main_service)
                                    for rule in self.rules
                                ]
                            )
                        ).apply(lambda args: " && ".join(args)),
                        "middlewares": (
                            [traefik_service.crowdsec.name] if self.public else []
                        )
                        + [
                            middleware.get_name(main_service)
                            for middleware in self.middlewares
                        ],
                        "tls": {
                            "certResolver": traefik_service.static.PUBLIC_CERT_RESOLVER
                            if self.public
                            else traefik_service.static.PRIVATE_CERT_RESOLVER
                        },
                    }
                },
            }
        }

        service_full = self.service.full
        if service_full:
            data["http"]["services"] = service_full.to_http_service(
                TraefikDynamicServiceType.HTTP, router_name, main_service
            )

        middlewares: dict[str, Any] = reduce(
            operator.or_,
            [
                middleware.to_section(main_service, traefik_service)
                for middleware in self.middlewares
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
        opts: ResourceOptions | None,
        main_service: ServiceResourceBase,
        traefik_service: TraefikService,
    ) -> TraefikDynamicRouterConfigResource:
        from ...resource.dynamic.router import TraefikDynamicRouterConfigResource

        return TraefikDynamicRouterConfigResource(
            resource_name,
            self,
            opts=opts,
            main_service=main_service,
            traefik_service=traefik_service,
        )
