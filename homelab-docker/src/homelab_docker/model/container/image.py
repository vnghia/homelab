from pulumi import Output
from pydantic import BaseModel, RootModel

from homelab_docker.resource.image import ImageResource


class ContainerImageBuildModelConfig(BaseModel):
    build: str


class ContainerImageModelConfig(RootModel[str | ContainerImageBuildModelConfig]):
    def to_image_name(self, image_resource: ImageResource) -> Output[str]:
        root = self.root
        if isinstance(root, str):
            return image_resource.remotes[root].name
        else:
            return Output.from_input(image_resource.builds[root.build].ref)

    def to_image_id(self, image_resource: ImageResource) -> Output[str]:
        root = self.root
        if isinstance(root, str):
            return image_resource.remotes[root].image_id
        else:
            return image_resource.builds[root.build].ref
