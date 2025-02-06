from pydantic import PositiveInt, RootModel

from homelab_docker.model.container.volume import ContainerVolumesConfig

from .container_volume_path import ContainerVolumePath


class ContainerString(RootModel[bool | PositiveInt | str | ContainerVolumePath]):
    def to_str(
        self, container_volumes_config: ContainerVolumesConfig | None = None
    ) -> str:
        root = self.root
        if isinstance(root, ContainerVolumePath):
            if not container_volumes_config:
                raise ValueError("container volumes is None")
            return root.to_container_path(container_volumes_config).as_posix()
        elif isinstance(root, bool):
            return str(root).lower()
        else:
            return str(root)
