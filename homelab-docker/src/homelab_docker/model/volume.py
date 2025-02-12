import pulumi_docker as docker
from pulumi import ResourceOptions
from pydantic import BaseModel

from homelab_docker.pydantic import AbsolutePath


class LocalVolumeModel(BaseModel):
    backup: bool = True

    bind: AbsolutePath | None = None
    labels: dict[str, str] = {}

    def build_resource(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions,
        project_labels: dict[str, str],
    ) -> docker.Volume:
        return docker.Volume(
            resource_name,
            opts=opts,
            driver="local",
            driver_opts={
                "type": "none",
                "o": "bind",
                "device": self.bind.as_posix(),
            }
            if self.bind
            else None,
            labels=[
                docker.VolumeLabelArgs(label=k, value=v)
                for k, v in (project_labels | self.labels).items()
            ],
        )
