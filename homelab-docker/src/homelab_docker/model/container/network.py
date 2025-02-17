import dataclasses
import typing

import pulumi_docker as docker
from homelab_pydantic import HomelabBaseModel
from pulumi import Input, Output
from pydantic import Field, RootModel

if typing.TYPE_CHECKING:
    from ...resource.network import NetworkResource
    from ...resource.service import ServiceResourceArgs


@dataclasses.dataclass
class ContainerNetworkArgs:
    mode: Input[str]
    advanced: list[docker.ContainerNetworksAdvancedArgs]


class ContainerNetworkModeConfig(HomelabBaseModel):
    container: str

    def to_args(
        self,
        _resource_name: str | None,
        _network_resource: "NetworkResource",
        service_resource_args: "ServiceResourceArgs",
    ) -> ContainerNetworkArgs:
        return ContainerNetworkArgs(
            mode=Output.format(
                "container:{0}", service_resource_args.containers[self.container].id
            ),
            advanced=[],
        )


class ContainerCommonNetworkConfig(HomelabBaseModel):
    default_bridge: bool = Field(False, alias="default-bridge")
    internal_bridge: bool = Field(True, alias="internal-bridge")

    def to_args(
        self,
        resource_name: str | None,
        network_resource: "NetworkResource",
        _: "ServiceResourceArgs",
    ) -> ContainerNetworkArgs:
        # TODO: remove bridge mode after https://github.com/pulumi/pulumi-docker/issues/1272
        aliases = [resource_name] if resource_name else []
        return ContainerNetworkArgs(
            mode="bridge",
            advanced=(
                [network_resource.default_bridge_args(aliases)]
                if self.default_bridge
                else []
            )
            + (
                [network_resource.internal_bridge_args(aliases)]
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
        resource_name: str | None,
        network_resource: "NetworkResource",
        service_resource_args: "ServiceResourceArgs",
    ) -> ContainerNetworkArgs:
        return self.root.to_args(resource_name, network_resource, service_resource_args)
