from typing import ClassVar

from homelab_pydantic import HomelabBaseModel

from ...model.docker.container.network import ContainerNetworkConfig
from ...model.docker.network import BridgeNetworkModel


class NetworkConfig(HomelabBaseModel):
    PROXY_ALIAS: ClassVar[str] = "reverse-proxy"

    bridge: dict[str, BridgeNetworkModel]
    default: ContainerNetworkConfig
