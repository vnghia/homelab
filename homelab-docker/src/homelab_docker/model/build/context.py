from pathlib import PosixPath

import pulumi_docker as docker
import pulumi_docker_build as docker_build
from pulumi import Input, Output
from pydantic import AnyHttpUrl, BaseModel, ConfigDict, RootModel

from homelab_docker.pydantic import RelativePath


class BuildImageContextModel(BaseModel):
    image: str

    def to_location(self, remote_images: dict[str, docker.RemoteImage]) -> Input[str]:
        return Output.format("docker-image://{}", remote_images[self.image].repo_digest)


class BuildFullContextModel(RootModel[PosixPath | AnyHttpUrl | BuildImageContextModel]):
    def to_location(self, remote_images: dict[str, docker.RemoteImage]) -> Input[str]:
        root = self.root
        if isinstance(root, PosixPath):
            return root.as_posix()
        elif isinstance(root, AnyHttpUrl):
            return str(root)
        else:
            return root.to_location(remote_images)

    def to_args(
        self, remote_images: dict[str, docker.RemoteImage]
    ) -> docker_build.ContextArgs:
        return docker_build.ContextArgs(location=self.to_location(remote_images))


class BuildContextModel(BaseModel):
    model_config = ConfigDict(extra="allow")

    location: RelativePath
    base: str
    __pydantic_extra__: dict[str, BuildFullContextModel] = {}  # pyright: ignore [reportIncompatibleVariableOverride]

    def to_args(
        self, remote_images: dict[str, docker.RemoteImage]
    ) -> docker_build.BuildContextArgs:
        return docker_build.BuildContextArgs(
            location=self.location.as_posix(),
            named={
                "base": BuildFullContextModel(
                    BuildImageContextModel(image=self.base)
                ).to_args(remote_images)
            }
            | {
                name: model.to_args(remote_images)
                for name, model in self.__pydantic_extra__.items()
            },
        )
