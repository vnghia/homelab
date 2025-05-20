from homelab_pydantic import AbsolutePath, HomelabBaseModel, HomelabRootModel
from pydantic import PositiveInt


class ContainerTmpfsFullConfig(HomelabBaseModel):
    path: AbsolutePath
    exec: bool = False
    uid: PositiveInt | None = None
    gid: PositiveInt | None = None


class ContainerTmpfsConfig(HomelabRootModel[AbsolutePath | ContainerTmpfsFullConfig]):
    def to_path(self) -> AbsolutePath:
        root = self.root
        return root.path if isinstance(root, ContainerTmpfsFullConfig) else root

    def to_args(self) -> tuple[AbsolutePath, str]:
        root = (
            self.root
            if isinstance(self.root, ContainerTmpfsFullConfig)
            else ContainerTmpfsFullConfig(path=self.root)
        )

        option = ",".join(
            list(
                filter(
                    bool,
                    [
                        ("exec" if root.exec else "noexec"),
                        ("uid={}".format(root.uid) if root.uid else ""),
                        ("gid={}".format(root.gid) if root.gid else ""),
                    ],
                )
            )
        )

        return (self.to_path(), option)
