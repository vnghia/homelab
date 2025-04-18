from __future__ import annotations

import operator
import typing
from functools import reduce
from typing import Any, ClassVar

from homelab_docker.extract import GlobalExtractor
from homelab_docker.resource.service import ServiceResourceBase
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
    CROWDSEC_MIDDLEWARE: ClassVar[str] = "crowdsec"

    def to_data(
        self, main_service: ServiceResourceBase, traefik_service: TraefikService
    ) -> dict[str, Any]:
        root = self.root

        entrypoint = traefik_service.config.entrypoint
        router_name = main_service.add_service_name(root.name)
        hostname = traefik_service.docker_resource_args.hostnames[root.public][
            root.hostname or router_name
        ]

        data: dict[str, Any] = {
            "http": {
                "routers": {
                    router_name: {
                        "service": TraefikDynamicServiceModelBuilder(
                            root.service
                        ).to_service_name(router_name),
                        "entryPoints": (
                            [entrypoint.public_https] if root.public else []
                        )
                        + [entrypoint.private_https],
                        "rule": Output.all(
                            *(
                                [Output.format("Host(`{}`)", hostname)]
                                + (
                                    [
                                        Output.format(
                                            "PathPrefix(`{}`)",
                                            GlobalExtractor(root.prefix).extract_str(
                                                main_service, None
                                            ),
                                        ),
                                    ]
                                    if root.prefix
                                    else []
                                )
                                + [
                                    GlobalExtractor(rule).extract_str(
                                        main_service, None
                                    )
                                    for rule in root.rules
                                ]
                            )
                        ).apply(lambda args: " && ".join(args)),
                        "middlewares": [
                            TraefikDynamicMiddlewareModelBuilder(middleware).get_name(
                                main_service, traefik_service
                            )
                            for middleware in (
                                (
                                    [
                                        TraefikDynamicMiddlewareModel(
                                            TraefikDynamicMiddlewareUseModel(
                                                service=traefik_service.name(),
                                                name=self.CROWDSEC_MIDDLEWARE,
                                            )
                                        )
                                    ]
                                    if root.public
                                    else []
                                )
                                + root.middlewares
                            )
                        ],
                        "tls": {"certResolver": traefik_service.static.CERT_RESOLVER},
                    }
                },
            }
        }

        service_full = TraefikDynamicServiceModelBuilder(root.service).full
        if service_full:
            data["http"]["services"] = TraefikDynamicServiceFullModelBuilder(
                service_full
            ).to_service(TraefikDynamicServiceType.HTTP, router_name, main_service)

        middlewares: dict[str, Any] = reduce(
            operator.or_,
            [
                TraefikDynamicMiddlewareModelBuilder(middleware).to_section(
                    main_service, traefik_service
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
        opts: ResourceOptions | None,
        main_service: ServiceResourceBase,
        traefik_service: TraefikService,
    ) -> TraefikDynamicRouterConfigResource:
        from ...resource.dynamic.router import TraefikDynamicRouterConfigResource

        resource = TraefikDynamicRouterConfigResource(
            resource_name,
            self,
            opts=opts,
            main_service=main_service,
            traefik_service=traefik_service,
        )
        traefik_service.routers[main_service.name()][resource_name] = resource
        return resource
