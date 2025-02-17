import pulumi_docker as docker
from homelab_pydantic import AbsolutePath, HomelabBaseModel
from pydantic import PositiveInt, RootModel


class ContainerTmpfsFullConfig(HomelabBaseModel):
    path: AbsolutePath
    size: PositiveInt | None = None


class ContainerTmpfsConfig(RootModel[AbsolutePath | ContainerTmpfsFullConfig]):
    def to_args(self) -> docker.ContainerMountArgs:
        root = self.root
        target = root.path if isinstance(root, ContainerTmpfsFullConfig) else root
        size = root.size if isinstance(root, ContainerTmpfsFullConfig) else None
        return docker.ContainerMountArgs(
            target=target.as_posix(),
            type="tmpfs",
            tmpfs_options=docker.ContainerMountTmpfsOptionsArgs(size_bytes=size),
        )
