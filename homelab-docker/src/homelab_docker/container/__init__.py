import pulumi_docker as docker
from pulumi import ResourceOptions
from pydantic import BaseModel, ConfigDict


class Container(BaseModel):
    model_config = ConfigDict(strict=True)

    name: str
    restart: str = "unless-stopped"
    remove: bool = False

    image: str

    labels: dict[str, str] = {}

    def build_resource(
        self,
        image: dict[str, docker.RemoteImage],
        opts: ResourceOptions | None = None,
        name: str | None = None,
    ) -> docker.Container:
        image_data = image[self.image]
        return docker.Container(
            self.name,
            opts=opts,
            name=name,
            image=image_data.name,
            restart=self.restart,
            rm=self.remove,
            labels=[docker.ContainerLabelArgs(label=k, value=v) for k, v in self.labels]
            + [docker.ContainerLabelArgs(label="image.id", value=image_data.image_id)],
        )
