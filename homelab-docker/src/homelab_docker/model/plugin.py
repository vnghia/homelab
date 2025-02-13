import pulumi_docker as docker
from pulumi import ResourceOptions
from pydantic import BaseModel

from .platform import Platform, PlatformString


class PluginModel(BaseModel):
    repo: PlatformString
    tag: PlatformString

    def build_name(self, platform: Platform) -> str:
        return "{}:{}".format(self.repo.to_str(platform), self.tag.to_str(platform))

    def build_resource(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions,
        platform: Platform,
    ) -> docker.Plugin:
        return docker.Plugin(
            resource_name,
            opts=opts,
            name=self.build_name(platform),
            enabled=False,
            grant_all_permissions=True,
        )
