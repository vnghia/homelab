from pydantic import PositiveInt, RootModel

from homelab_docker.interpolation.volume_path import VolumePath
from homelab_docker.model.container.volume import Volumes as ContainerVolumes


class ContainerString(RootModel[bool | PositiveInt | str | VolumePath]):
    def to_str(self, container_volumes: ContainerVolumes | None = None) -> str:
        root = self.root
        if isinstance(root, VolumePath):
            if not container_volumes:
                raise ValueError("container volumes is None")
            return root.to_container_path(container_volumes).as_posix()
        elif isinstance(root, bool):
            return str(root).lower()
        else:
            return str(root)
