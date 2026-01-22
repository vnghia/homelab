from collections import defaultdict
from functools import partial
from ipaddress import IPv4Address, IPv6Address

import pulumi
import pulumi_docker as docker
from homelab_global import ProjectArgs
from homelab_pydantic import IPvAnyNetworkAdapter
from homelab_sequence import HomelabSequenceResource
from pulumi import ComponentResource, Input, Output, ResourceOptions
from pydantic import IPvAnyNetwork, NonNegativeInt

from ...config.docker.network import NetworkEgressType
from ...config.service.network import (
    ServiceNetworkBridgeConfig,
    ServiceNetworkEgressFullConfig,
)
from ...extract import ExtractorArgs
from ...model.docker.container import ContainerNetworkModelBuildArgs
from ...model.docker.container.host import ContainerHostConfig, ContainerHostHostConfig
from ...model.docker.container.network import (
    ContainerBridgeNetworkArgs,
    ContainerCommonNetworkConfig,
    ContainerNetworkContainerConfig,
)
from ...model.docker.network import BridgeIpamNetworkModel, BridgeNetworkModel
from ...model.host import HostServiceModelModel


class NetworkResource(ComponentResource):
    RESOURCE_NAME = "network"

    def __init__(
        self,
        config: HostServiceModelModel,
        *,
        opts: ResourceOptions,
        project_args: ProjectArgs,
        host: str,
        extractor_args: ExtractorArgs,
    ) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)
        self.host_model = config
        self.config = self.host_model.docker.network
        self.bridge_config = self.config.bridge.host

        self.bridge = {
            key: model.build_resource(
                self.get_bridge_name(key),
                opts=self.child_opts,
                project_labels=project_args.labels,
                ipam=[],
            )
            for key, model in self.bridge_config.items()
        }

        self.options: defaultdict[
            str, dict[str | None, ContainerNetworkModelBuildArgs]
        ] = defaultdict(lambda: defaultdict(ContainerNetworkModelBuildArgs))

        self.service_networks: dict[str, ServiceNetworkBridgeConfig] = {}
        self.service_subnets: dict[str, list[Output[str]]] = {}
        self.service_egresses: dict[
            str,
            dict[
                NetworkEgressType,
                dict[str, ServiceNetworkEgressFullConfig],
            ],
        ] = {}

        proxy_config = self.config.proxy
        proxy_service, proxy_container = self.compute_proxy(
            proxy_config.service, proxy_config.container
        )
        self.proxy_option = self.options[proxy_service][proxy_container]

        for (
            service_name,
            service_model,
        ) in self.host_model.services.items():
            service_network = service_model.network
            if service_network.bridge:
                self.service_networks[service_name] = service_network.bridge

            for container_model in service_model.containers.values():
                network_mode = container_model.network.root
                if isinstance(network_mode, ContainerNetworkContainerConfig):
                    network = self.options[network_mode.service or service_name][
                        network_mode.container
                    ]
                    network.add_hosts(
                        [
                            host.with_service(service_name, False)
                            for host in container_model.hosts
                        ]
                    )
                    network.add_ports(
                        container_model.ports.with_service(service_name, False)
                    )

        self.build_service_networks(extractor_args)

        for value in self.bridge.values():
            pulumi.export(
                "{}.{}.{}".format(host, self.RESOURCE_NAME, value._name), value.name
            )
        self.register_outputs({})

    @classmethod
    def build_ipam(
        cls, sequence: NonNegativeInt, subnet: IPvAnyNetwork
    ) -> BridgeIpamNetworkModel:
        return BridgeIpamNetworkModel.model_construct(
            subnet=IPvAnyNetworkAdapter.validate_python(
                (
                    subnet.network_address + subnet.num_addresses * sequence,
                    subnet.prefixlen,
                )
            )
        )

    def build_service_proxy_bridge_args(
        self,
        service: str,
        bridge_config: ServiceNetworkBridgeConfig,
        extractor_args: ExtractorArgs,
        ipams: list[Output[BridgeIpamNetworkModel]],
    ) -> None:
        proxy_bridge_config = self.config.proxy.bridge

        egress_config = bridge_config.egress
        if egress_config:
            self.service_egresses[service] = {}
            for egress_type, egress in egress_config.items():
                self.service_egresses[service][egress_type] = {}

                for egress_key, egress_model in egress.items():
                    service_egress_model = egress_model.with_service(service).to_full(
                        extractor_args
                    )

                    self.service_egresses[service][egress_type][egress_key] = (
                        service_egress_model
                    )
                    for container_name in self.host_model.services[service].containers:
                        self.options[service][container_name].add_hosts(
                            [
                                ContainerHostConfig(
                                    ContainerHostHostConfig(hostname=address)
                                )
                                for address in service_egress_model.addresses
                            ]
                        )

        if proxy_bridge_config.offset:
            ipv4 = ipams[0].apply(
                lambda x: str(x.ip(proxy_bridge_config.offset, IPv4Address))
            )
            ipv6 = ipams[1].apply(
                lambda x: str(x.ip(proxy_bridge_config.offset, IPv6Address))
            )
            proxy_bridge_args = ContainerBridgeNetworkArgs(
                proxy_bridge_config, ipv4, ipv6
            )
        else:
            proxy_bridge_args = ContainerBridgeNetworkArgs(proxy_bridge_config)

        self.proxy_option.bridges[service] = proxy_bridge_args

    def build_service_networks(self, extractor_args: ExtractorArgs) -> None:
        service_network_model = BridgeNetworkModel(internal=True)
        service_network_sequence = HomelabSequenceResource(
            "service", opts=self.child_opts, names=list(self.service_networks.keys())
        )

        build_ipam_fns = [
            partial(self.__class__.build_ipam, subnet=ipam)
            for ipam in self.config.bridge.service
        ]
        for service_name, service_bridge in self.service_networks.items():
            service_sequence = service_network_sequence[service_name]
            self.bridge_config[service_name] = service_network_model
            self.service_subnets[service_name] = []

            ipam = []
            for build_ipam_fn in build_ipam_fns:
                model = service_sequence.apply(build_ipam_fn)
                self.service_subnets[service_name].append(
                    model.apply(lambda model: str(model.subnet))
                )
                ipam.append(model)

            self.bridge[service_name] = service_network_model.build_resource(
                self.get_bridge_name(service_name),
                opts=self.child_opts,
                project_labels=extractor_args.global_resource.project_args.labels,
                ipam=ipam,
            )
            self.build_service_proxy_bridge_args(
                service_name, service_bridge, extractor_args, ipam
            )

    @classmethod
    def get_bridge_name(cls, name: str) -> str:
        return "{}-bridge".format(name)

    def get_bridge_args(
        self,
        name: str,
        aliases: list[Input[str]],
        ipv4: Output[str] | None,
        ipv6: Output[str] | None,
    ) -> docker.ContainerNetworksAdvancedArgs:
        return docker.ContainerNetworksAdvancedArgs(
            name=self.bridge[name].name,
            aliases=aliases,
            ipv4_address=ipv4,
            ipv6_address=ipv6,
        )

    def compute_proxy(
        self, service: str, container: str | None
    ) -> tuple[str, str | None]:
        network_mode = (
            self.host_model.services[service].containers[container].network.root
        )
        if isinstance(network_mode, ContainerCommonNetworkConfig):
            return (service, container)
        if isinstance(network_mode, ContainerNetworkContainerConfig):
            return self.compute_proxy(
                network_mode.service or service, network_mode.container
            )
        raise ValueError(
            "Proxy container must have either common network or container network config"
        )

    def get_proxy_bridges(self) -> dict[str, ContainerBridgeNetworkArgs]:
        proxy_config = self.config.proxy
        proxy_service, proxy_container = self.compute_proxy(
            proxy_config.service, proxy_config.container
        )
        return self.options[proxy_service][proxy_container].bridges
