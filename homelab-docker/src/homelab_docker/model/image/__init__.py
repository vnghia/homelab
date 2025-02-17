import pulumi_docker as docker
from homelab_pydantic import HomelabBaseModel
from pulumi import ResourceOptions

from ..platform import Platform, PlatformString


class RemoteImageModel(HomelabBaseModel):
    repo: PlatformString
    tag: PlatformString
    delete_before_replace: bool = False

    def build_name(self, platform: Platform) -> str:
        return "{}:{}".format(self.repo.to_str(platform), self.tag.to_str(platform))

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
                opts, ResourceOptions(delete_before_replace=self.delete_before_replace)
            ),
            name=self.build_name(platform),
            force_remove=False,
            keep_locally=False,
            platform=platform.value,
        )
