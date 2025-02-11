from pydantic import PositiveInt, RootModel

from .volume import ContainerVolumesConfig
from .volume_path import ContainerVolumePath


class ContainerString(RootModel[bool | PositiveInt | str | ContainerVolumePath]):
    def to_str(
        self, container_volumes_config: ContainerVolumesConfig | None = None
    ) -> str:
        root = self.root
        if isinstance(root, ContainerVolumePath):
            if not container_volumes_config:
                raise ValueError("Container volumes is None")
            return root.to_container_path(container_volumes_config).as_posix()
        elif isinstance(root, bool):
            return str(root).lower()
        else:
            return str(root)

    def as_container_volume_path(self) -> ContainerVolumePath:
        root = self.root
        if isinstance(root, ContainerVolumePath):
            return root
        else:
            raise TypeError("Container string real type is not container volume path")
