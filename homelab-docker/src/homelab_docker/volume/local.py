import pulumi_docker as docker
from pulumi import ResourceOptions
from pydantic import BaseModel, ConfigDict

from homelab_docker.pydantic.path import AbsolutePath


class Local(BaseModel):
    model_config = ConfigDict(strict=True)

    bind: AbsolutePath | None = None
    labels: dict[str, str] = {}

    def build_resource(
        self,
        resource_name: str,
        opts: ResourceOptions | None = None,
        name: str | None = None,
    ) -> docker.Volume:
        return docker.Volume(
            resource_name,
            opts=opts,
            name=name,
            driver="local",
            driver_opts={
                "type": "none",
                "o": "bind",
                "device": self.bind.as_posix(),
            }
            if self.bind
            else None,
            labels=[
                docker.VolumeLabelArgs(label=k, value=v) for k, v in self.labels.items()
            ],
        )
