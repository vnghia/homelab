from homelab_pydantic import HomelabBaseModel
from homelab_pydantic.model import HomelabRootModel


class ContainerInheritFullConfig(HomelabBaseModel):
    service: str | None
    container: str | None = None


class ContainerInheritConfig(HomelabRootModel[str | None | ContainerInheritFullConfig]):
    root: str | ContainerInheritFullConfig | None = None

    def to_full(self) -> ContainerInheritFullConfig:
        root = self.root
        if isinstance(root, ContainerInheritFullConfig):
            return root
        return ContainerInheritFullConfig(service=None, container=root)
