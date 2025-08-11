from __future__ import annotations

import typing

from homelab_pydantic import HomelabBaseModel, HomelabRootModel
from pulumi import Output

if typing.TYPE_CHECKING:
    from ....resource.docker.image import ImageResource


class ContainerImageBuildModelConfig(HomelabBaseModel):
    build: str


class ContainerImageModelConfig(HomelabRootModel[str | ContainerImageBuildModelConfig]):
    def to_image_name(self, image_resource: ImageResource) -> Output[str]:
        root = self.root
        if isinstance(root, str):
            return image_resource.remotes[root].name
        return Output.from_input(image_resource.builds[root.build].ref)

    def to_image_id(self, image_resource: ImageResource) -> Output[str]:
        root = self.root
        if isinstance(root, str):
            return image_resource.remotes[root].image_id
        return image_resource.builds[root.build].digest
