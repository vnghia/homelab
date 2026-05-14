from typing import Self

from homelab_pydantic import HomelabBaseModel, HomelabRootModel


class ContainerInheritFullConfig(HomelabBaseModel):
    service: str | None
    container: str | None = None


class ContainerInheritConfig(HomelabRootModel[str | None | ContainerInheritFullConfig]):
    @classmethod
    def default(cls) -> Self:
        return cls(None)

    def to_full(self) -> ContainerInheritFullConfig:
        root = self.root
        if isinstance(root, ContainerInheritFullConfig):
            return root
        return ContainerInheritFullConfig(service=None, container=root)
