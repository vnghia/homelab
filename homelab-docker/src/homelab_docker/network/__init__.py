import pulumi_docker as docker
from pydantic import BaseModel, ConfigDict


class Bridge(BaseModel):
    model_config = ConfigDict(strict=True)

    name: str
    ipv6: bool = True
    labels: dict[str, str] = {}

    def build_resource(self) -> docker.Network:
        return docker.Network(
            resource_name=self.name,
            name=self.name,
            driver="bridge",
            ipv6=self.ipv6,
            labels=[
                docker.NetworkLabelArgs(label=k, value=v)
                for k, v in self.labels.items()
            ],
        )
