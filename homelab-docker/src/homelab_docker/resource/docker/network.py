from collections import defaultdict
from functools import partial

import pulumi
import pulumi_docker as docker
from homelab_extract import GlobalExtract
from homelab_global import GlobalArgs
from homelab_pydantic import IPvAnyNetworkAdapter
from homelab_sequence import HomelabSequenceResource
from pulumi import ComponentResource, Input, Output, ResourceOptions
from pydantic import IPvAnyNetwork, NonNegativeInt

from ...config.service.network import (
    ServiceNetworkBridgeConfig,
    ServiceNetworkProxyEgressType,
)
from ...model.docker.container import ContainerNetworkModelBuildArgs
from ...model.docker.container.network import (
    ContainerBridgeNetworkConfig,
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
        global_args: GlobalArgs,
        host: str,
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
                project_labels=global_args.project.labels,
                ipam=[],
            )
            for key, model in self.bridge_config.items()
        }

        self.options: defaultdict[
            str, dict[str | None, ContainerNetworkModelBuildArgs]
        ] = defaultdict(lambda: defaultdict(ContainerNetworkModelBuildArgs))

        self.service_networks = []
        self.service_subnets: dict[str, list[Output[IPvAnyNetwork]]] = {}
        self.service_egresses: dict[
            str, dict[ServiceNetworkProxyEgressType, dict[str, GlobalExtract]]
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
                self.service_networks.append(service_name)
                self.build_service_proxy_bridge_config(
                    service_name, service_network.bridge
                )

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

        self.proxy_option.bridges = dict(
            sorted(self.proxy_option.bridges.items(), key=lambda x: x[0])
        )
        self.build_service_networks(global_args)

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

    def build_service_proxy_bridge_config(
        self, service: str, bridge_config: ServiceNetworkBridgeConfig
    ) -> None:
        proxy_bridge_config = self.config.proxy.bridge
        aliases = proxy_bridge_config.aliases

        proxy_config = bridge_config.proxy
        if proxy_config.aliases:
            aliases = aliases + [
                alias.with_service(service, False) for alias in proxy_config.aliases
            ]

        if proxy_config.egress:
            if aliases is proxy_bridge_config.aliases:
                aliases = aliases.copy()

            self.service_egresses[service] = {}
            for egress_type, egress in proxy_config.egress.items():
                self.service_egresses[service][egress_type] = {}
                for egress_key, egress_model in egress.items():
                    service_egress_model = egress_model.with_service(service, False)
                    self.service_egresses[service][egress_type][egress_key] = (
                        egress_model
                    )
                    aliases.append(service_egress_model)

        if aliases is not proxy_bridge_config.aliases:
            proxy_bridge_config = proxy_bridge_config.__replace__(aliases=aliases)

        self.proxy_option.bridges[service] = proxy_bridge_config

    def build_service_networks(self, global_args: GlobalArgs) -> None:
        service_network_model = BridgeNetworkModel(internal=True)
        service_network_sequence = HomelabSequenceResource(
            "service", opts=self.child_opts, names=self.service_networks
        )

        build_ipam_fns = [
            partial(self.__class__.build_ipam, subnet=ipam)
            for ipam in self.config.bridge.service
        ]
        for service in self.service_networks:
            service_sequence = service_network_sequence[service]
            self.bridge_config[service] = service_network_model
            self.service_subnets[service] = []

            ipam = []
            for build_ipam_fn in build_ipam_fns:
                model = service_sequence.apply(build_ipam_fn)
                self.service_subnets[service].append(
                    model.apply(lambda model: model.subnet)
                )
                ipam.append(model)

            self.bridge[service] = service_network_model.build_resource(
                self.get_bridge_name(service),
                opts=self.child_opts,
                project_labels=global_args.project.labels,
                ipam=ipam,
            )

    @classmethod
    def get_bridge_name(cls, name: str) -> str:
        return "{}-bridge".format(name)

    def get_bridge_args(
        self, name: str, aliases: list[Input[str]]
    ) -> docker.ContainerNetworksAdvancedArgs:
        return docker.ContainerNetworksAdvancedArgs(
            name=self.bridge[name].name, aliases=aliases
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

    def get_proxy_bridges(self) -> dict[str, ContainerBridgeNetworkConfig]:
        proxy_config = self.config.proxy
        proxy_service, proxy_container = self.compute_proxy(
            proxy_config.service, proxy_config.container
        )
        return self.options[proxy_service][proxy_container].bridges
