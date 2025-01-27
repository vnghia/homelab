import deepmerge
import pulumi_docker as docker
from pulumi import Input, Output, ResourceOptions
from pydantic import BaseModel, ConfigDict


class Container(BaseModel):
    model_config = ConfigDict(strict=True)

    restart: str = "unless-stopped"
    read_only: bool = True
    remove: bool = False
    wait: bool = True

    image: str

    envs: dict[str, str] = {}
    labels: dict[str, str] = {}

    def build_resource(
        self,
        resource_name: str,
        images: dict[str, docker.RemoteImage],
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
            envs=[
                Output.concat(k, "=", Output.from_input(v).apply(str))
                for k, v in deepmerge.always_merger.merge(self.envs, envs).items()  # type: ignore[attr-defined]
            ],
            read_only=self.read_only,
            restart=self.restart,
            rm=self.remove,
            wait=self.wait,
            labels=[
                docker.ContainerLabelArgs(label=k, value=v)
                for k, v in self.labels.items()
            ]
            + [docker.ContainerLabelArgs(label="image.id", value=image.image_id)],
        )
