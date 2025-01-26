import pulumi_docker as docker
from pulumi import ResourceOptions
from pydantic import BaseModel, ConfigDict


class Bridge(BaseModel):
    model_config = ConfigDict(strict=True)

    resource_name: str
    name: str | None = None
    ipv6: bool = True
    labels: dict[str, str] = {}

    def build_resource(self, opts: ResourceOptions | None) -> docker.Network:
        return docker.Network(
            self.resource_name,
            opts=opts,
            name=self.name,
            driver="bridge",
            ipv6=self.ipv6,
            labels=[
                docker.NetworkLabelArgs(label=k, value=v)
                for k, v in self.labels.items()
            ],
        )
