from __future__ import annotations

import abc
import operator
import typing
from functools import reduce
from typing import Any, ClassVar

from homelab_docker.extract import ExtractorArgs
from homelab_docker.extract.global_ import GlobalExtractor
from homelab_pydantic import HomelabRootModel
from homelab_traefik_config.model.dynamic.base import TraefikDynamicBaseModel
from homelab_traefik_config.model.dynamic.type import TraefikDynamicType
from pulumi import Output

from .middleware import TraefikDynamicMiddlewareModelBuilder
from .service import (
    TraefikDynamicServiceFullModelBuilder,
    TraefikDynamicServiceModelBuilder,
)

if typing.TYPE_CHECKING:
    from ... import TraefikService


class TraefikDynamicBaseModelBuilder[T: TraefikDynamicBaseModel](HomelabRootModel[T]):
    TYPE: ClassVar[TraefikDynamicType]

    LOCAL_MIDDLEWARE_NAMES: ClassVar[list[str]]
    LOCAL_MIDDLEWARES: ClassVar[list[str] | None]

    def get_host(
        self,
        record: str,
        hostname: str | None,
        router_name: str,
        traefik_service: TraefikService,
        extractor_args: ExtractorArgs,
    ) -> Output[str]:
        root = self.root
        return Output.from_input(
            GlobalExtractor(root.address).extract_str(extractor_args)
            if root.address
            else traefik_service.extractor_args.hostnames[record][
                hostname or router_name
            ].value
        )

    @abc.abstractmethod
    def build_rule(
        self,
        record: str,
        router_name: str,
        traefik_service: TraefikService,
        extractor_args: ExtractorArgs,
    ) -> Output[str]: ...

    @abc.abstractmethod
    def build_tls(
        self, traefik_service: TraefikService, extractor_args: ExtractorArgs
    ) -> tuple[dict[str, Any] | None, dict[str, Any]]: ...

    def to_data(
        self, traefik_service: TraefikService, extractor_args: ExtractorArgs
    ) -> dict[str, Any]:
        root = self.root
        record = root.record or extractor_args.host.name
        traefik_config = traefik_service.config
        main_service = extractor_args.service

        router_name = main_service.add_service_name(root.name)
        service = TraefikDynamicServiceModelBuilder(root.service).to_service_name(
            router_name
        )

        rule = self.build_rule(record, router_name, traefik_service, extractor_args)

        entrypoint = root.entrypoint or traefik_config.entrypoint.mapping[record]
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

        tls, tls_router = self.build_tls(traefik_service, extractor_args)

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
                | (
                    {
                        "{}-local".format(router_name): {
                            "service": service,
                            "entryPoints": [traefik_config.entrypoint.local_],
                            "rule": rule,
                            "tls": tls_router,
                            "middlewares": self.build_local_middlewares(
                                traefik_service, extractor_args
                            )
                            + service_middlewares,
                        }
                    }
                    if root.entrypoint is None and entrypoint_config.local
                    else {}
                )
                | (
                    {
                        "{}-internal".format(router_name): {
                            "service": service,
                            "entryPoints": [traefik_config.entrypoint.internal_],
                            "rule": rule,
                            "tls": tls_router,
                            "middlewares": service_middlewares,
                        }
                    }
                    if root.entrypoint is None and entrypoint_config.internal
                    else {}
                ),
            }
        }

        if service_full := TraefikDynamicServiceModelBuilder(root.service).full:
            data[self.TYPE]["services"] = TraefikDynamicServiceFullModelBuilder(
                service_full
                if service_full.port is not None
                else service_full.__replace__(port=entrypoint_config.root.port)
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

        if tls:
            data |= tls

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
