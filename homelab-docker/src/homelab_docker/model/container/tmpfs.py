import pulumi_docker as docker
from homelab_pydantic import AbsolutePath, HomelabBaseModel, HomelabRootModel
from pydantic import PositiveInt


class ContainerTmpfsFullConfig(HomelabBaseModel):
    path: AbsolutePath
    mode: PositiveInt | None = None
    size: PositiveInt | None = None


class ContainerTmpfsConfig(HomelabRootModel[AbsolutePath | ContainerTmpfsFullConfig]):
    def to_args(self) -> docker.ContainerMountArgs:
        root = self.root
        target = root.path if isinstance(root, ContainerTmpfsFullConfig) else root

        mode = root.mode if isinstance(root, ContainerTmpfsFullConfig) else None
        size_bytes = root.size if isinstance(root, ContainerTmpfsFullConfig) else None

        return docker.ContainerMountArgs(
            target=target.as_posix(),
            type="tmpfs",
            tmpfs_options=docker.ContainerMountTmpfsOptionsArgs(
                mode=mode, size_bytes=size_bytes
            ),
        )
