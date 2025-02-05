import pulumi_docker as docker
from pulumi import ResourceOptions
from pydantic import BaseModel

from homelab_docker.model.platform import Platform


class RemoteImage(BaseModel):
    repo: str
    tag: str

    @property
    def name(self) -> str:
        return "{}:{}".format(self.repo, self.tag)

    def build_resource(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions,
        platform: Platform,
    ) -> docker.RemoteImage:
        return docker.RemoteImage(
            resource_name,
            opts=ResourceOptions.merge(
                opts, ResourceOptions(delete_before_replace=True)
            ),
            name=self.name,
            force_remove=False,
            keep_locally=False,
            platform=platform.value,
        )
