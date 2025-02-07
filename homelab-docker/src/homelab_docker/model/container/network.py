import dataclasses

import pulumi_docker as docker
from pulumi import Input, Output
from pydantic import BaseModel, Field, RootModel

from homelab_docker.resource.network import NetworkResource


@dataclasses.dataclass
class ContainerNetworkArgs:
    mode: Input[str]
    advanced: list[docker.ContainerNetworksAdvancedArgs]


class ContainerNetworkModeConfig(BaseModel):
    container: str

    def to_args(
        self,
        _resource_name: str,
        _network_resource: NetworkResource,
        containers: dict[str, docker.Container],
    ) -> ContainerNetworkArgs:
        return ContainerNetworkArgs(
            mode=Output.format("container:{0}", containers[self.container].id),
            advanced=[],
        )


class ContainerCommonNetworkConfig(BaseModel):
    default_bridge: bool = Field(False, alias="default-bridge")
    internal_bridge: bool = Field(True, alias="internal-bridge")

    def to_args(
        self,
        resource_name: str,
        network: NetworkResource,
        _: dict[str, docker.Container],
    ) -> ContainerNetworkArgs:
        # TODO: remove bridge mode after https://github.com/pulumi/pulumi-docker/issues/1272
        return ContainerNetworkArgs(
            mode="bridge",
            advanced=(
                [network.default_bridge_args([resource_name])]
                if self.default_bridge
                else []
            )
            + (
                [network.internal_bridge_args([resource_name])]
                if self.internal_bridge
                else []
            ),
        )


class ContainerNetworkConfig(
    RootModel[ContainerCommonNetworkConfig | ContainerNetworkModeConfig]
):
    root: ContainerCommonNetworkConfig | ContainerNetworkModeConfig = (
        ContainerCommonNetworkConfig()  # type: ignore [call-arg]
    )

    def to_args(
        self,
        resource_name: str,
        network: NetworkResource,
        containers: dict[str, docker.Container],
    ) -> ContainerNetworkArgs:
        return self.root.to_args(resource_name, network, containers)
