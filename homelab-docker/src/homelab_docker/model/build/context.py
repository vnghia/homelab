from pathlib import PosixPath

import pulumi_docker_build as docker_build
from pulumi import Input, Output
from pydantic import AnyHttpUrl, BaseModel, ConfigDict, RootModel

from homelab_docker.pydantic import RelativePath
from homelab_docker.resource.image import ImageResource


class BuildImageContextModel(BaseModel):
    image: str

    def to_location(self, image_resource: ImageResource) -> Input[str]:
        return Output.format(
            "docker-image://{}", image_resource.remotes[self.image].repo_digest
        )


class BuildFullContextModel(RootModel[PosixPath | AnyHttpUrl | BuildImageContextModel]):
    def to_location(self, image_resource: ImageResource) -> Input[str]:
        root = self.root
        if isinstance(root, PosixPath):
            return root.as_posix()
        elif isinstance(root, AnyHttpUrl):
            return str(root)
        else:
            return root.to_location(image_resource)

    def to_args(self, image_resource: ImageResource) -> docker_build.ContextArgs:
        return docker_build.ContextArgs(location=self.to_location(image_resource))


class BuildContextModel(BaseModel):
    model_config = ConfigDict(extra="allow")

    localtion: RelativePath
    base: BuildImageContextModel
    __pydantic_extra__: dict[str, BuildFullContextModel] = {}  # pyright: ignore [reportIncompatibleVariableOverride]
