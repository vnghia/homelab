import pulumi_docker as docker
from pulumi import ResourceOptions
from pydantic import BaseModel, ConfigDict


class Bridge(BaseModel):
    model_config = ConfigDict(strict=True)

    ipv6: bool = True
    labels: dict[str, str] = {}

    def build_resource(
        self,
        resource_name: str,
        opts: ResourceOptions | None = None,
        name: str | None = None,
    ) -> docker.Network:
        return docker.Network(
            resource_name,
            opts=opts,
            name=name,
            driver="bridge",
            ipv6=self.ipv6,
            labels=[
                docker.NetworkLabelArgs(label=k, value=v)
                for k, v in self.labels.items()
            ],
        )
