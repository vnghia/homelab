import pulumi_docker as docker
from pydantic import BaseModel, ConfigDict


class Network(BaseModel):
    model_config = ConfigDict(strict=True)

    def to_container_network_advance(
        self, network: docker.Network
    ) -> docker.ContainerNetworksAdvancedArgs:
        return docker.ContainerNetworksAdvancedArgs(name=network.name)
