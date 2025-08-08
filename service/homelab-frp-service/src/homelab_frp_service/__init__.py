from __future__ import annotations

from typing import Any

from homelab_docker.config.network import NetworkConfig
from homelab_docker.extract import ExtractorArgs
from homelab_docker.extract.global_ import GlobalExtractor
from homelab_docker.model.container.port import ContainerPortProtocol
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource.file.config import (
    ConfigFileResource,
    JsonDefaultModel,
    TomlDumper,
)
from homelab_docker.resource.service import ServiceWithConfigResourceBase
from homelab_network.resource.network import NetworkResource
from pulumi import ResourceOptions
from pydantic import PositiveInt

from .config import FrpConfig


class FrpClientConfigResource(
    ConfigFileResource[JsonDefaultModel], module="frp", name="ClientConfig"
):
    validator = JsonDefaultModel
    dumper = TomlDumper[JsonDefaultModel]

    def __init__(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions,
        network_resource: NetworkResource,
        frp_service: FrpService,
    ) -> None:
        proxies = []
        for prefix, service in frp_service.docker_resource_args.models.items():
            for name, container in service.containers.items():
                for key, port in container.build_ports().items():
                    if port.forward:
                        proxy_name = frp_service.add_service_name(key, prefix=prefix)
                        alias = port.forward.alias or frp_service.add_service_name(
                            name, prefix=prefix
                        )
                        proxy = self.build_proxy(
                            proxy_name,
                            alias,
                            port.internal,
                            port.external,
                            port.protocol or ContainerPortProtocol.TCP,
                            False,
                        )
                        proxies.append(proxy)

        port_config = network_resource.config.port
        config = frp_service.config
        super().__init__(
            resource_name,
            opts=opts,
            volume_path=GlobalExtractor(config.path).extract_volume_path(
                frp_service.extractor_args
            ),
            data={
                "serverAddr": str(config.server.addr),
                "serverPort": config.server.port,
                "log": {"to": "console"},
                "auth": {"method": "token", "token": config.server.token},
                "transport": {
                    "protocol": config.protocol,
                    "tls": {"enable": False},
                    "poolCount": config.pool,
                    "tcpMux": True,
                },
                "proxies": [
                    self.build_proxy(
                        "http",
                        NetworkConfig.PROXY_ALIAS,
                        port_config.internal.http,
                        port_config.external.http,
                        ContainerPortProtocol.TCP,
                        True,
                    ),
                    self.build_proxy(
                        "https",
                        NetworkConfig.PROXY_ALIAS,
                        port_config.internal.https,
                        port_config.external.https,
                        ContainerPortProtocol.TCP,
                        True,
                    ),
                    self.build_proxy(
                        "h3",
                        NetworkConfig.PROXY_ALIAS,
                        port_config.internal.https,
                        port_config.external.https,
                        ContainerPortProtocol.UDP,
                        True,
                    ),
                    *proxies,
                ],
            },
            docker_resource_args=frp_service.docker_resource_args,
        )

    @classmethod
    def build_proxy(
        cls,
        name: str,
        local_ip: str,
        local_port: PositiveInt,
        remote_port: PositiveInt,
        proxy_type: ContainerPortProtocol,
        proxy_protocol: bool,
    ) -> dict[str, Any]:
        return (
            {
                "name": name,
                "localIP": local_ip,
                "localPort": local_port,
                "remotePort": remote_port,
            }
            | {
                "type": str(proxy_type),
            }
            | ({"transport": {"proxyProtocolVersion": "v2"}} if proxy_protocol else {})
        )


class FrpService(ServiceWithConfigResourceBase[FrpConfig]):
    def __init__(
        self,
        model: ServiceWithConfigModel[FrpConfig],
        *,
        opts: ResourceOptions,
        network_resource: NetworkResource,
        extractor_args: ExtractorArgs,
    ) -> None:
        super().__init__(model, opts=opts, extractor_args=extractor_args)

        self.client_config = FrpClientConfigResource(
            "client-config",
            opts=self.child_opts,
            network_resource=network_resource,
            frp_service=self,
        )
        self.options[None].files = [self.client_config]
        self.build_containers()

        self.register_outputs({})
