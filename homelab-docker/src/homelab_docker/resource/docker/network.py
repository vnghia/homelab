from collections import defaultdict
from functools import partial

import pulumi
import pulumi_docker as docker
from homelab_global import GlobalArgs
from homelab_sequence import HomelabSequenceResource
from netaddr_pydantic import IPNetwork
from pulumi import ComponentResource, Input, ResourceOptions
from pydantic import NonPositiveInt

from ...model.docker.container import ContainerNetworkModelBuildArgs
from ...model.docker.container.network import ContainerNetworkContainerConfig
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
        self.config = config.docker.network

        self.bridge = {
            key: model.build_resource(
                self.get_bridge_name(key),
                opts=self.child_opts,
                project_labels=global_args.project.labels,
                ipam=[],
            )
            for key, model in self.config.bridge.host.items()
        }

        self.options: defaultdict[
            str, dict[str | None, ContainerNetworkModelBuildArgs]
        ] = defaultdict(lambda: defaultdict(ContainerNetworkModelBuildArgs))

        service_networks = []

        for (
            service_name,
            service_model,
        ) in config.services.items():
            service_network = service_model.network
            if service_network.bridge:
                service_networks.append(service_name)

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

        service_network_sequence = HomelabSequenceResource(
            "service", opts=self.child_opts, names=service_networks
        )
        build_ipam_fns = [
            partial(self.__class__.build_ipam, subnet=ipam)
            for ipam in self.config.bridge.service
        ]
        for service in service_networks:
            service_sequence = service_network_sequence[service]
            self.bridge[service] = BridgeNetworkModel().build_resource(
                self.get_bridge_name(service),
                opts=self.child_opts,
                project_labels=global_args.project.labels,
                ipam=[
                    service_sequence.apply(build_ipam_fn)
                    for build_ipam_fn in build_ipam_fns
                ],
            )

        for value in self.bridge.values():
            pulumi.export(
                "{}.{}.{}".format(host, self.RESOURCE_NAME, value._name), value.name
            )
        self.register_outputs({})

    @classmethod
    def build_ipam(
        cls, sequence: NonPositiveInt, subnet: IPNetwork
    ) -> BridgeIpamNetworkModel:
        return BridgeIpamNetworkModel(subnet=subnet.next(sequence))

    @classmethod
    def get_bridge_name(cls, name: str) -> str:
        return "{}-bridge".format(name)

    def get_bridge_args(
        self, name: str, aliases: list[Input[str]]
    ) -> docker.ContainerNetworksAdvancedArgs:
        return docker.ContainerNetworksAdvancedArgs(
            name=self.bridge[name].name, aliases=aliases
        )
