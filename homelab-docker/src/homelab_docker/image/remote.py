import pulumi_docker as docker
from pulumi import ResourceOptions
from pydantic import BaseModel, ConfigDict, computed_field

from homelab_docker.image.platform import Platform


class Remote(BaseModel):
    model_config = ConfigDict(strict=True)

    repo: str
    tag: str

    platform: Platform | None = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def name(self) -> str:
        return f"{self.repo}:{self.tag}"

    def build_resource(self, opts: ResourceOptions | None) -> docker.RemoteImage:
        return docker.RemoteImage(
            resource_name=self.repo,
            opts=opts,
            name=self.name,
            force_remove=False,
            keep_locally=False,
            platform=self.platform.value if self.platform else None,
        )
