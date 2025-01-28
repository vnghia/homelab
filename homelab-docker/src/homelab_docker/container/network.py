import pulumi_docker as docker
from pydantic import BaseModel, ConfigDict


class Network(BaseModel):
    model_config = ConfigDict(strict=True)

    aliases: list[str] = []

    def to_container_network_advance(
        self, resource_name: str, network: docker.Network
    ) -> docker.ContainerNetworksAdvancedArgs:
        return docker.ContainerNetworksAdvancedArgs(
            name=network.name, aliases=self.aliases + [resource_name]
        )
