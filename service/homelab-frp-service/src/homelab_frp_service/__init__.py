from __future__ import annotations

from typing import Any

from homelab_docker.config.network import NetworkConfig
from homelab_docker.extract import GlobalExtractor
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource import DockerResourceArgs
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
        opts: ResourceOptions | None,
        network_resource: NetworkResource,
        frp_service: FrpService,
    ) -> None:
        proxies = []
        for prefix, service in frp_service.docker_resource_args.models.items():
            for name, container in service.containers.items():
                for key, port in container.ports.items():
                    if port.forward:
                        proxy_name = frp_service.add_service_name(key, prefix=prefix)
                        alias = port.forward.alias or frp_service.add_service_name(
                            name, prefix=prefix
                        )
                        proxy = (
                            self.build_tcp(
                                proxy_name, alias, port.internal, port.external, False
                            )
                            if port.protocol == "tcp"
                            else self.build_udp(
                                proxy_name, alias, port.internal, port.external
                            )
                        )
                        proxies.append(proxy)

        port_config = network_resource.config.port
        config = frp_service.config
        super().__init__(
            resource_name,
            opts=opts,
            volume_path=GlobalExtractor(config.path).extract_volume_path(
                frp_service, None
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
                },
                "proxies": [
                    self.build_tcp(
                        "http",
                        NetworkConfig.PROXY_ALIAS,
                        port_config.internal.http,
                        port_config.external.http,
                        True,
                    ),
                    self.build_tcp(
                        "https",
                        NetworkConfig.PROXY_ALIAS,
                        port_config.internal.https,
                        port_config.external.https,
                        True,
                    ),
                    self.build_udp(
                        "h3",
                        NetworkConfig.PROXY_ALIAS,
                        port_config.internal.https,
                        port_config.external.https,
                    ),
                    *proxies,
                ],
            },
            volume_resource=frp_service.docker_resource_args.volume,
        )

    @classmethod
    def build_common(
        cls,
        name: str,
        local_ip: str,
        local_port: PositiveInt,
        remote_port: PositiveInt,
    ) -> dict[str, Any]:
        return {
            "name": name,
            "localIP": local_ip,
            "localPort": local_port,
            "remotePort": remote_port,
        }

    @classmethod
    def build_tcp(
        cls,
        name: str,
        local_ip: str,
        local_port: PositiveInt,
        remote_port: PositiveInt,
        proxy_protocol: bool,
    ) -> dict[str, Any]:
        return (
            cls.build_common(name, local_ip, local_port, remote_port)
            | {
                "type": "tcp",
            }
            | ({"transport": {"proxyProtocolVersion": "v2"}} if proxy_protocol else {})
        )

    @classmethod
    def build_udp(
        cls, name: str, local_ip: str, local_port: PositiveInt, remote_port: PositiveInt
    ) -> dict[str, Any]:
        return cls.build_common(name, local_ip, local_port, remote_port) | {
            "type": "udp",
        }


class FrpService(ServiceWithConfigResourceBase[FrpConfig]):
    def __init__(
        self,
        model: ServiceWithConfigModel[FrpConfig],
        *,
        opts: ResourceOptions | None,
        network_resource: NetworkResource,
        docker_resource_args: DockerResourceArgs,
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)

        self.client_config = FrpClientConfigResource(
            "client-config",
            opts=self.child_opts,
            network_resource=network_resource,
            frp_service=self,
        )
        self.options[None].files = [self.client_config]
        self.build_containers()

        self.register_outputs({})
