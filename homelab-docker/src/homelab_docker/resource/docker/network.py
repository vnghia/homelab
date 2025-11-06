from collections import defaultdict

import pulumi
import pulumi_docker as docker
from homelab_global import GlobalArgs
from pulumi import ComponentResource, Input, ResourceOptions

from ...model.docker.container import ContainerNetworkModelBuildArgs
from ...model.docker.container.network import ContainerNetworkContainerConfig
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
            for key, model in self.config.bridge.items()
        }

        self.options: defaultdict[
            str, dict[str | None, ContainerNetworkModelBuildArgs]
        ] = defaultdict(lambda: defaultdict(ContainerNetworkModelBuildArgs))

        for (
            service_name,
            service_model,
        ) in config.services.items():
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

        for value in self.bridge.values():
            pulumi.export(
                "{}.{}.{}".format(host, self.RESOURCE_NAME, value._name), value.name
            )
        self.register_outputs({})

    @classmethod
    def get_bridge_name(cls, name: str) -> str:
        return "{}-bridge".format(name)

    def get_bridge_args(
        self, name: str, aliases: list[Input[str]]
    ) -> docker.ContainerNetworksAdvancedArgs:
        return docker.ContainerNetworksAdvancedArgs(
            name=self.bridge[name].name, aliases=aliases
        )
