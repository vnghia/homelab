import typing

import pulumi_docker as docker
from homelab_pydantic import HomelabBaseModel
from pulumi import ResourceOptions
from pydantic import Field

from ..platform import PlatformString

if typing.TYPE_CHECKING:
    from ....config.docker import DockerConfig


class RemoteImageTagFromModel(HomelabBaseModel):
    from_: str = Field(alias="from")


class RemoteImageModel(HomelabBaseModel):
    repo: PlatformString
    tag: PlatformString | RemoteImageTagFromModel
    prefix: PlatformString | None = None
    suffix: PlatformString | None = None
    delete_before_replace: bool = False

    def build_tag(self, config: DockerConfig) -> str:
        if isinstance(self.tag, PlatformString):
            return self.tag.to_str(config.platform)
        return config.images.remote[self.tag.from_].build_tag(config)

    def build_name(self, config: DockerConfig) -> str:
        platform = config.platform
        tag = self.build_tag(config)
        if self.prefix:
            tag = self.prefix.to_str(platform) + tag
        if self.suffix:
            tag = tag + self.suffix.to_str(platform)
        return "{}:{}".format(self.repo.to_str(platform), tag)

    def build_resource(
        self, resource_name: str, *, opts: ResourceOptions, config: DockerConfig
    ) -> docker.RemoteImage:
        platform = config.platform
        return docker.RemoteImage(
            resource_name,
            opts=ResourceOptions.merge(
                opts, ResourceOptions(delete_before_replace=self.delete_before_replace)
            ),
            name=self.build_name(config),
            force_remove=False,
            keep_locally=False,
            platform=platform,
        )
