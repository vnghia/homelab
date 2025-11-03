from functools import cached_property
from typing import Any, ClassVar

from homelab_docker.extract import ExtractorArgs
from homelab_docker.extract.global_ import GlobalExtractor
from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel, HomelabRootModel
from pulumi import Output
from pydantic import NonNegativeInt


class TraefikEntrypointPortModel(HomelabBaseModel):
    port: GlobalExtract

    def to_address(self, extractor_args: ExtractorArgs) -> Output[str]:
        return (
            GlobalExtractor(self.port)
            .extract_str(extractor_args)
            .apply(lambda x: ":{}".format(int(x)))
        )


class TraefikEntrypointRedirectModel(TraefikEntrypointPortModel):
    to: GlobalExtract

    def to_entry_point(self, extractor_args: ExtractorArgs) -> dict[str, Any]:
        return {
            "address": self.to_address(extractor_args),
            "http": {
                "redirections": {
                    "entryPoint": {
                        "to": TraefikEntrypointPortModel(port=self.to).to_address(
                            extractor_args
                        ),
                        "scheme": "https",
                    }
                }
            },
        }


class TraefikEntrypointHttp3Model(HomelabBaseModel):
    port: GlobalExtract | None = None

    def to_config(self, extractor_args: ExtractorArgs) -> dict[str, Any]:
        return {
            "http3": (
                {
                    "advertisedPort": GlobalExtractor(self.port)
                    .extract_str(extractor_args)
                    .apply(int)
                }
                if self.port
                else {}
            )
        }


class TraefikEntrypointTimeoutModel(HomelabBaseModel):
    read: str
    write: str
    idle: str

    def to_config(self) -> dict[str, Any]:
        return {
            "transport": {
                "respondingTimeouts": {
                    "readTimeout": self.read,
                    "writeTimeout": self.idle,
                    "idleTimeout": self.write,
                }
            }
        }


class TraefikEntrypointProxyProtocolModel(HomelabBaseModel):
    ips: list[GlobalExtract] = []
    proxy_network: str | None = None

    def to_config(self, extractor_args: ExtractorArgs) -> dict[str, Any]:
        ips = [GlobalExtractor(ip).extract_str(extractor_args) for ip in self.ips]
        proxy_ips = (
            extractor_args.host.docker.network.bridge[
                self.proxy_network
            ].ipam_configs.apply(
                lambda ipam_configs: [
                    ipam_config.subnet
                    for ipam_config in ipam_configs
                    if ipam_config.subnet
                ]
            )
            if self.proxy_network
            else None
        )

        return {
            "proxyProtocol": {
                "trustedIPs": Output.all(ips=ips, proxy_ips=proxy_ips).apply(
                    lambda args: list(args["ips"] + (args["proxy_ips"] or []))
                )
            }
        }


class TraefikEntrypointMiddlewareFullModel(HomelabBaseModel):
    DEFAULT_PRIORITY: ClassVar[NonNegativeInt] = 100
    service: str | None = None
    middleware: str | None = None
    priority: NonNegativeInt = DEFAULT_PRIORITY


class TraefikEntrypointMiddlewareModel(
    HomelabRootModel[str | TraefikEntrypointMiddlewareFullModel]
):
    def to_full(self) -> TraefikEntrypointMiddlewareFullModel:
        from .. import TraefikService

        root = self.root
        if isinstance(root, TraefikEntrypointMiddlewareFullModel):
            return root
        return TraefikEntrypointMiddlewareFullModel(
            service=TraefikService.name(), middleware=root
        )


class TraefikEntrypointFullModel(TraefikEntrypointPortModel):
    local: bool = False
    internal: bool = False
    http3: TraefikEntrypointHttp3Model | None = None
    timeout: TraefikEntrypointTimeoutModel | None = None
    proxy_protocol: TraefikEntrypointProxyProtocolModel | None = None
    middlewares: list[TraefikEntrypointMiddlewareModel] = []

    def to_entry_point(self, extractor_args: ExtractorArgs) -> dict[str, Any]:
        return (
            {
                "address": self.to_address(extractor_args),
            }
            | (self.timeout.to_config() if self.timeout else {})
            | (self.http3.to_config(extractor_args) if self.http3 else {})
            | (
                self.proxy_protocol.to_config(extractor_args)
                if self.proxy_protocol
                else {}
            )
        )


class TraefikEntrypointModel(
    HomelabRootModel[TraefikEntrypointRedirectModel | TraefikEntrypointFullModel]
):
    def to_entry_point(self, extractor_args: ExtractorArgs) -> dict[str, Any]:
        return self.root.to_entry_point(extractor_args)

    @cached_property
    def middlewares(self) -> list[TraefikEntrypointMiddlewareFullModel]:
        root = self.root
        if isinstance(root, TraefikEntrypointFullModel):
            return sorted(
                map(TraefikEntrypointMiddlewareModel.to_full, root.middlewares),
                key=lambda x: x.priority,
            )
        return []

    @property
    def local(self) -> bool:
        root = self.root
        if isinstance(root, TraefikEntrypointFullModel):
            return root.local
        return False

    @property
    def internal(self) -> bool:
        root = self.root
        if isinstance(root, TraefikEntrypointFullModel):
            return root.internal
        return False
