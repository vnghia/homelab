import pulumi_docker as docker
from pulumi import ResourceOptions
from pydantic import BaseModel


class BridgeNetwork(BaseModel):
    ipv6: bool = True
    internal: bool = False
    labels: dict[str, str] = {}

    def build_resource(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions,
        project_labels: dict[str, str],
    ) -> docker.Network:
        return docker.Network(
            resource_name,
            opts=opts,
            driver="bridge",
            ipv6=self.ipv6,
            internal=self.internal,
            labels=[
                docker.NetworkLabelArgs(label=k, value=v)
                for k, v in (project_labels | self.labels).items()
            ],
        )
