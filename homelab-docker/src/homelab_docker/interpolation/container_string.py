from pydantic import PositiveInt, RootModel

from homelab_docker.interpolation.volume_path import VolumePath
from homelab_docker.model.container.volume import Volume as ContainerVolume


class ContainerString(RootModel[bool | PositiveInt | str | VolumePath]):
    def to_str(
        self, container_volumes: dict[str, ContainerVolume] | None = None
    ) -> str:
        root = self.root
        if isinstance(root, VolumePath):
            return root.to_container_path(container_volumes or {}).as_posix()
        elif isinstance(root, bool):
            return str(root).lower()
        else:
            return str(root)
