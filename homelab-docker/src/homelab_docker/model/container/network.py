import dataclasses

import pulumi_docker as docker
from pulumi import Input, Output
from pydantic import BaseModel, RootModel

from homelab_docker.resource.network import Network as NetworkResource


@dataclasses.dataclass
class NetworkArgs:
    mode: Input[str]
    advanced: list[docker.ContainerNetworksAdvancedArgs]


class ContainerNetwork(BaseModel):
    container: str

    def to_args(
        self, _: NetworkResource, containers: dict[str, docker.Container]
    ) -> NetworkArgs:
        return NetworkArgs(
            mode=Output.format("container:{0}", containers[self.container].id),
            advanced=[],
        )


class CommonNetwork(BaseModel):
    default_bridge: bool
    internal_bridge: bool

    def to_args(
        self, network: NetworkResource, _: dict[str, docker.Container]
    ) -> NetworkArgs:
        # TODO: remove bridge mode after https://github.com/pulumi/pulumi-docker/issues/1272
        return NetworkArgs(
            mode="bridge",
            advanced=[network.default_bridge_args]
            if self.default_bridge
            else [] + [network.internal_bridge_args]
            if self.internal_bridge
            else [],
        )


class Network(RootModel[CommonNetwork | ContainerNetwork]):
    root: CommonNetwork | ContainerNetwork = CommonNetwork(
        default_bridge=False, internal_bridge=True
    )

    def to_args(
        self, network: NetworkResource, containers: dict[str, docker.Container]
    ) -> NetworkArgs:
        return self.root.to_args(network, containers)
