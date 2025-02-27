from __future__ import annotations

import dataclasses
import typing

import pulumi_docker as docker
from homelab_pydantic import HomelabBaseModel, HomelabRootModel
from pulumi import Input, Output

if typing.TYPE_CHECKING:
    from ...resource.service import ServiceResourceBase


@dataclasses.dataclass
class ContainerNetworkArgs:
    mode: Input[str]
    advanced: list[docker.ContainerNetworksAdvancedArgs]


class ContainerNetworkModeConfig(HomelabBaseModel):
    service: str
    container: str | None = None

    def to_args(
        self, _resource_name: str | None, main_service: ServiceResourceBase
    ) -> ContainerNetworkArgs:
        return ContainerNetworkArgs(
            mode=Output.format(
                "container:{0}",
                main_service.CONTAINER_RESOURCE[self.service][self.container].id,
            ),
            advanced=[],
        )


class ContainerCommonNetworkConfig(HomelabBaseModel):
    default_bridge: bool = False
    internal_bridge: bool = True

    def to_args(
        self, resource_name: str | None, main_service: ServiceResourceBase
    ) -> ContainerNetworkArgs:
        # TODO: remove bridge mode after https://github.com/pulumi/pulumi-docker/issues/1272
        aliases = [resource_name] if resource_name else []
        return ContainerNetworkArgs(
            mode="bridge",
            advanced=(
                [main_service.docker_resource_args.network.default_bridge_args(aliases)]
                if self.default_bridge
                else []
            )
            + (
                [
                    main_service.docker_resource_args.network.internal_bridge_args(
                        aliases
                    )
                ]
                if self.internal_bridge
                else []
            ),
        )


class ContainerNetworkConfig(
    HomelabRootModel[ContainerCommonNetworkConfig | ContainerNetworkModeConfig]
):
    root: ContainerCommonNetworkConfig | ContainerNetworkModeConfig = (
        ContainerCommonNetworkConfig()
    )

    def to_args(
        self, resource_name: str | None, main_service: ServiceResourceBase
    ) -> ContainerNetworkArgs:
        return self.root.to_args(resource_name, main_service)
