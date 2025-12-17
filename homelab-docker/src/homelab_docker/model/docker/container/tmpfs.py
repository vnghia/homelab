from homelab_pydantic import AbsolutePath, HomelabBaseModel, HomelabRootModel

from ...user import UidGidModel


class ContainerTmpfsFullConfig(HomelabBaseModel):
    path: AbsolutePath
    exec: bool = False


class ContainerTmpfsConfig(HomelabRootModel[AbsolutePath | ContainerTmpfsFullConfig]):
    def to_path(self) -> AbsolutePath:
        root = self.root
        return root.path if isinstance(root, ContainerTmpfsFullConfig) else root

    def to_args(self, user: UidGidModel) -> tuple[AbsolutePath, str]:
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
                        ("uid={}".format(user.uid)),
                        ("gid={}".format(user.gid)),
                    ],
                )
            )
        )

        return (self.to_path(), option)
