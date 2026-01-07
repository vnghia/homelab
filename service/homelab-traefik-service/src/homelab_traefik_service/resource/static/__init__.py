from __future__ import annotations

import typing
from typing import Any

from homelab_docker.extract.global_ import GlobalExtractor
from homelab_docker.resource.file.config import ConfigFileResource, TomlDumper
from pulumi import ResourceOptions

from . import schema

if typing.TYPE_CHECKING:
    from ... import TraefikService


class TraefikStaticConfigResource(
    ConfigFileResource[schema.TraefikV3StaticConfiguration],
    module="traefik",
    name="StaticConfig",
):
    validator = schema.TraefikV3StaticConfiguration
    dumper = TomlDumper[schema.TraefikV3StaticConfiguration]

    CERT_RESOLVER = "cert-resolver"

    def __init__(
        self, *, opts: ResourceOptions, traefik_service: TraefikService
    ) -> None:
        traefik_config = traefik_service.config

        static_volume_path = GlobalExtractor(
            traefik_service.config.path.static
        ).extract_volume_path(traefik_service.extractor_args)

        access_log: dict[str, Any] = {"format": "json"}
        if traefik_access_log_config := traefik_config.log.access:
            if traefik_access_log_config.path:
                access_log["filePath"] = (
                    GlobalExtractor(traefik_access_log_config.path)
                    .extract_path(traefik_service.extractor_args)
                    .as_posix()
                )
            if traefik_access_log_config.config:
                access_log |= traefik_access_log_config.config.model_dump(
                    exclude_unset=True
                )

        metrics: dict[str, Any] = {}
        if traefik_metrics_config := traefik_config.metrics:
            if traefik_metrics_otlp_config := traefik_metrics_config.otlp:
                otlp: dict[str, Any] = traefik_metrics_otlp_config.model_dump(
                    exclude_unset=True
                )
            else:
                otlp = {"grpc": {}}

            otlp["serviceName"] = GlobalExtractor(
                traefik_metrics_config.service_name
            ).extract_str(traefik_service.extractor_args)
            otlp["grpc"]["endpoint"] = GlobalExtractor(
                traefik_config.metrics.endpoint
            ).extract_str(traefik_service.extractor_args)

            if traefik_metrics_config.headers:
                otlp["grpc"]["headers"] = {
                    key: GlobalExtractor(value).extract_str(
                        traefik_service.extractor_args
                    )
                    for key, value in traefik_config.metrics.headers.items()
                }

            if traefik_metrics_config.resource_attributes:
                otlp["resourceAttributes"] = {
                    key: GlobalExtractor(value).extract_str(
                        traefik_service.extractor_args
                    )
                    for key, value in traefik_config.metrics.resource_attributes.items()
                }

            metrics["otlp"] = otlp

        super().__init__(
            "static",
            opts=opts,
            volume_path=static_volume_path,
            data={
                "global": {"checkNewVersion": False, "sendAnonymousUsage": False},
                "accessLog": access_log,
                "api": {
                    "dashboard": True,
                    "disableDashboardAd": True,
                }
                | (
                    {
                        "basePath": GlobalExtractor(
                            traefik_config.path.api
                        ).extract_str(traefik_service.extractor_args)
                    }
                    if traefik_config.path.api
                    else {}
                ),
                "log": {"level": "INFO", "format": "json"},
                "metrics": metrics,
                "ping": {},
                "entryPoints": {
                    key: entrypoint.to_entry_point(traefik_service.extractor_args)
                    for key, entrypoint in traefik_config.entrypoint.config.items()
                },
                "providers": {
                    "file": {
                        "directory": traefik_service.dynamic_directory_volume_path.to_path(
                            traefik_service.extractor_args_from_self(None)
                        ),
                        "watch": True,
                    },
                },
                "serversTransport": {"insecureSkipVerify": True},
                "certificatesResolvers": {
                    self.CERT_RESOLVER: {
                        "acme": {
                            "caServer": str(traefik_config.acme.server),
                            "email": traefik_config.acme.email,
                            "storage": GlobalExtractor(
                                traefik_config.acme.storage
                            ).extract_path(traefik_service.extractor_args),
                            "dnsChallenge": {
                                "provider": "cloudflare",
                                "resolvers": ["1.1.1.1:53", "8.8.8.8:53"],
                                "propagation": {
                                    "disableChecks": traefik_config.acme.disable_checks,
                                    "requireAllRNS": traefik_config.acme.require_all_rns,
                                    "disableANSChecks": traefik_config.acme.disable_ans_checks,
                                    "delayBeforeChecks": traefik_config.acme.delay_before_checks,
                                },
                            },
                        }
                    },
                },
            }
            | (
                {
                    "experimental": {
                        "plugins": {
                            name: {
                                "moduleName": model.name,
                                "version": model.version,
                            }
                            for name, model in traefik_config.plugins.items()
                        }
                    }
                }
                if traefik_config.plugins
                else {}
            ),
            permission=traefik_service.user,
            extractor_args=traefik_service.extractor_args,
        )
