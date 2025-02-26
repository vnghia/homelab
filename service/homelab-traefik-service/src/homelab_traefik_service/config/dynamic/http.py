from __future__ import annotations

import operator
import typing
from functools import reduce
from typing import Any

from homelab_docker.resource.service import ServiceResourceBase
from homelab_pydantic import HomelabBaseModel
from pulumi import ResourceOptions

from .middleware import TraefikDynamicMiddlewareConfig
from .service import TraefikDynamicServiceConfig, TraefikDynamicServiceType

if typing.TYPE_CHECKING:
    from ... import TraefikService
    from ...resource.dynamic import TraefikDynamicConfigResource


class TraefikDynamicHttpConfig(HomelabBaseModel):
    name: str | None = None
    public: bool
    hostname: str | None = None
    prefix: str | None = None

    rules: list[str] = []
    service: TraefikDynamicServiceConfig
    middlewares: list[TraefikDynamicMiddlewareConfig] = []

    def to_data(
        self, main_service: ServiceResourceBase, traefik_service: TraefikService
    ) -> dict[str, Any]:
        entrypoint = traefik_service.config.entrypoint
        router_name = main_service.add_service_name(self.name)
        hostname = (
            traefik_service.network_resource.public.hostnames
            if self.public
            else traefik_service.network_resource.private.hostnames
        )[self.hostname or router_name]

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
                        "rule": hostname.apply(
                            lambda x: " && ".join(
                                ["Host(`{}`)".format(x)]
                                + (
                                    ["PathPrefix(`{}`)".format(self.prefix)]
                                    if self.prefix
                                    else []
                                )
                                + self.rules
                            )
                        ),
                        "middlewares": [
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
            [middleware.to_section(main_service) for middleware in self.middlewares],
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
    ) -> TraefikDynamicConfigResource:
        from ...resource.dynamic import TraefikDynamicConfigResource

        return TraefikDynamicConfigResource(
            resource_name,
            self,
            opts=opts,
            main_service=main_service,
            traefik_service=traefik_service,
        )
