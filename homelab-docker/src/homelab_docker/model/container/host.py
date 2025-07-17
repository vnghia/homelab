import pulumi_docker as docker
from homelab_pydantic import HomelabBaseModel


class ContainerHostConfig(HomelabBaseModel):
    host: str
    ip: str

    def to_args(self) -> docker.ContainerHostArgs:
        return docker.ContainerHostArgs(host=self.host, ip=self.ip)
