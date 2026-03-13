from __future__ import annotations

import abc
import operator
import typing
from functools import reduce
from typing import Any, ClassVar

from homelab_docker.extract import ExtractorArgs
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

    def get_host(
        self,
        record: str,
        hostname: str | None,
        router_name: str,
        traefik_service: TraefikService,
        extractor_args: ExtractorArgs,
    ) -> Output[str]:
        hostnames = traefik_service.extractor_args.hostnames[record]
        if hostname:
            return Output.from_input(hostnames[hostname].value)

        return Output.from_input(
            (
                hostnames.get(extractor_args.service.name()) or hostnames[router_name]
            ).value
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
        record_config = traefik_config.record.config[record]
        main_service = extractor_args.service

        router_name = main_service.add_service_name(root.name)
        service = TraefikDynamicServiceModelBuilder(root.service).to_service_name(
            router_name
        )

        rule = self.build_rule(record, router_name, traefik_service, extractor_args)

        entrypoint = root.entrypoint or record_config.entrypoint
        entrypoint_config = traefik_config.entrypoint.config[entrypoint]

        service_middlewares = [
            TraefikDynamicMiddlewareModelBuilder(middleware).get_name(
                traefik_service, extractor_args, self.TYPE
            )
            for middleware in root.middlewares
        ]

        if root.entrypoint:
            all_middlewares = service_middlewares
        else:
            all_middlewares = (
                traefik_config.record.build_middlewares(
                    extractor_args.host.network.config.records[record].is_internal,
                    traefik_service,
                    extractor_args,
                    self.TYPE,
                )
                + record_config.build_middlewares(
                    traefik_service, extractor_args, self.TYPE
                )
                + service_middlewares
            )

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
