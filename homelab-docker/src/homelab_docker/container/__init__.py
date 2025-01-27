import deepmerge
import pulumi_docker as docker
from pulumi import Input, Output, ResourceOptions
from pydantic import BaseModel, ConfigDict

from homelab_docker.container.env import Env
from homelab_docker.container.tmpfs import Tmpfs
from homelab_docker.container.volume import Volume


class Container(BaseModel):
    model_config = ConfigDict(strict=True)

    restart: str = "unless-stopped"
    read_only: bool = True
    remove: bool = False
    wait: bool = True

    image: str

    tmpfs: Tmpfs | None = None
    volumes: dict[str, Volume] = {}
    envs: dict[str, Env] = {}
    labels: dict[str, str] = {}

    def build_resource(
        self,
        resource_name: str,
        images: dict[str, docker.RemoteImage],
        volumes: dict[str, docker.Volume],
        opts: ResourceOptions | None = None,
        name: str | None = None,
        envs: dict[str, Input[str]] = {},
    ) -> docker.Container:
        image = images[self.image]
        return docker.Container(
            resource_name,
            opts=opts,
            name=name,
            image=image.name,
            read_only=self.read_only,
            restart=self.restart,
            rm=self.remove,
            wait=self.wait,
            mounts=[
                docker.ContainerMountArgs(
                    target=self.tmpfs.path.as_posix(),
                    type="tmpfs",
                    tmpfs_options=docker.ContainerMountTmpfsOptionsArgs(
                        size_bytes=self.tmpfs.size
                    ),
                )
            ]
            if self.tmpfs
            else [],
            volumes=[
                v.to_container_volume_args(name=volumes[k].name)
                for k, v in self.volumes.items()
            ],
            envs=[
                Output.concat(
                    k,
                    "=",
                    Output.from_input(v).apply(
                        lambda x: x.to_str(self.volumes) if isinstance(x, Env) else x
                    ),
                )
                for k, v in deepmerge.always_merger.merge(self.envs, envs).items()  # type: ignore[attr-defined]
            ],
            labels=[
                docker.ContainerLabelArgs(label=k, value=v)
                for k, v in self.labels.items()
            ]
            + [docker.ContainerLabelArgs(label="image.id", value=image.image_id)],
        )
