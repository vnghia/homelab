from __future__ import annotations

import operator
import typing
from functools import reduce
from typing import Any, ClassVar

from homelab_docker.extract import ExtractorArgs
from homelab_pydantic import HomelabRootModel
from homelab_traefik_config.model.dynamic.tcp import TraefikDynamicTcpModel
from homelab_traefik_config.model.dynamic.type import TraefikDynamicType
from pulumi import ResourceOptions

from .middleware import TraefikDynamicMiddlewareModelBuilder
from .service import (
    TraefikDynamicServiceFullModelBuilder,
    TraefikDynamicServiceModelBuilder,
)

if typing.TYPE_CHECKING:
    from ... import TraefikService
    from ...resource.dynamic.router import TraefikDynamicRouterConfigResource


class TraefikDynamicTcpModelBuilder(HomelabRootModel[TraefikDynamicTcpModel]):
    TYPE: ClassVar[TraefikDynamicType] = TraefikDynamicType.TCP

    LOCAL_MIDDLEWARE_NAMES: ClassVar[list[str]] = ["local-tcp"]
    LOCAL_MIDDLEWARES: ClassVar[list[str] | None] = None

    def to_data(
        self, traefik_service: TraefikService, extractor_args: ExtractorArgs
    ) -> dict[str, Any]:
        root = self.root
        traefik_config = traefik_service.config
        main_service = extractor_args.service

        router_name = main_service.add_service_name(root.name)
        hostsni = traefik_service.extractor_args.hostnames[root.record][root.hostsni]

        service = TraefikDynamicServiceModelBuilder(root.service).to_service_name(
            router_name
        )
        rule = "HostSNI(`{}`)".format(hostsni.value)

        entrypoint = traefik_config.entrypoint.mapping[root.record]
        entrypoint_config = traefik_config.entrypoint.config[entrypoint]
        entrypoint_middlewares = entrypoint_config.build_middlewares(
            traefik_service, extractor_args, self.TYPE
        )

        service_middlewares = [
            TraefikDynamicMiddlewareModelBuilder(middleware).get_name(
                traefik_service, extractor_args, self.TYPE
            )
            for middleware in root.middlewares
        ]

        all_middlewares = entrypoint_middlewares + service_middlewares

        tls_router: dict[str, Any] = {"passthrough": True}

        data: dict[str, Any] = {
            self.TYPE: {
                "routers": {
                    router_name: {
                        "service": service,
                        "entryPoints": [entrypoint],
                        "rule": rule,
                        "tls": tls_router,
                    }
                    | ({"middlewares": all_middlewares} if all_middlewares else {})
                }
            }
        }

        service_full = TraefikDynamicServiceModelBuilder(root.service).full
        if service_full:
            data[self.TYPE]["services"] = TraefikDynamicServiceFullModelBuilder(
                service_full
            ).to_service(self.TYPE, router_name, extractor_args)

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
            data[self.TYPE]["middlewares"] = middlewares

        return data

    @classmethod
    def build_local_middlewares(
        cls, traefik_service: TraefikService, extractor_args: ExtractorArgs
    ) -> list[str]:
        # Since local middleware's name won't change, we only need to build once regardless of extractor_args

        if cls.LOCAL_MIDDLEWARES is None:
            from homelab_traefik_config.model.dynamic.middleware import (
                TraefikDynamicMiddlewareModel,
                TraefikDynamicMiddlewareUseModel,
            )

            cls.LOCAL_MIDDLEWARES = [
                TraefikDynamicMiddlewareModelBuilder(
                    TraefikDynamicMiddlewareModel(
                        TraefikDynamicMiddlewareUseModel(
                            service=traefik_service.name(), name=middleware
                        )
                    ),
                ).get_name(traefik_service, extractor_args, cls.TYPE)
                for middleware in cls.LOCAL_MIDDLEWARE_NAMES
            ]
        return cls.LOCAL_MIDDLEWARES

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
