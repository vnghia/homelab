from __future__ import annotations

import typing
from typing import Any

from homelab_pydantic import HomelabBaseModel
from pulumi import ResourceOptions

from .middleware import TraefikDynamicMiddlewareConfig
from .service import TraefikDynamicServiceConfig, TraefikDynamicServiceType

if typing.TYPE_CHECKING:
    from ... import TraefikService
    from ..dynamic import TraefikDynamicConfigResource


class TraefikHttpDynamicConfig(HomelabBaseModel):
    name: str
    public: bool
    hostname: str | None = None
    prefix: str | None = None

    rules: list[str] = []
    service: TraefikDynamicServiceConfig
    middlewares: list[TraefikDynamicMiddlewareConfig] = []

    def to_data(self, traefik_service: TraefikService) -> dict[str, Any]:
        entrypoint = traefik_service.config.entrypoint
        hostname = (
            traefik_service.network_resource.public.hostnames
            if self.public
            else traefik_service.network_resource.private.hostnames
        )[self.hostname or self.name]

        data: dict[str, Any] = {
            "http": {
                "routers": {
                    self.name: {
                        "service": self.service.to_service_name(self.name),
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
                            middleware.name for middleware in self.middlewares
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
                TraefikDynamicServiceType.HTTP, self.name, traefik_service.args
            )

        middlewares = {
            middleware.name: middleware.data
            for middleware in self.middlewares
            if middleware.data is not None
        }
        if middlewares:
            data["http"]["middlewares"] = middlewares

        return data

    def build_resource(
        self,
        resource_name: str | None,
        *,
        opts: ResourceOptions | None,
        traefik_service: TraefikService,
    ) -> TraefikDynamicConfigResource:
        from homelab_traefik_service.config.dynamic import TraefikDynamicConfigResource

        return TraefikDynamicConfigResource(
            resource_name, self, opts=opts, traefik_service=traefik_service
        )
