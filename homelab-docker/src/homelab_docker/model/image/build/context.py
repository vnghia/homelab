import pulumi_docker as docker
import pulumi_docker_build as docker_build
from homelab_pydantic import HomelabBaseModel, HomelabRootModel, RelativePath
from pulumi import Input, Output
from pydantic import AnyHttpUrl, ConfigDict


class BuildImageRemoteImageContextModel(HomelabBaseModel):
    image: str

    def to_location(self, remote_images: dict[str, docker.RemoteImage]) -> Input[str]:
        return Output.format("docker-image://{}", remote_images[self.image].repo_digest)


class BuildImageFullContextModel(
    HomelabRootModel[RelativePath | AnyHttpUrl | BuildImageRemoteImageContextModel]
):
    def to_location(self, remote_images: dict[str, docker.RemoteImage]) -> Input[str]:
        root = self.root
        if isinstance(root, RelativePath):
            return root.as_posix()
        elif isinstance(root, AnyHttpUrl):
            return str(root)
        else:
            return root.to_location(remote_images)

    def to_args(
        self, remote_images: dict[str, docker.RemoteImage]
    ) -> docker_build.ContextArgs:
        return docker_build.ContextArgs(location=self.to_location(remote_images))


class BuildImageContextModel(HomelabBaseModel):
    model_config = ConfigDict(extra="allow")

    location: RelativePath
    base: str

    def to_args(
        self, remote_images: dict[str, docker.RemoteImage]
    ) -> docker_build.BuildContextArgs:
        return docker_build.BuildContextArgs(
            location=self.location.as_posix(),
            named={
                "base": BuildImageFullContextModel(
                    BuildImageRemoteImageContextModel(image=self.base)
                ).to_args(remote_images)
            }
            | {
                name: BuildImageFullContextModel(**data).to_args(remote_images)
                for name, data in (self.model_extra or {}).items()
            },
        )
