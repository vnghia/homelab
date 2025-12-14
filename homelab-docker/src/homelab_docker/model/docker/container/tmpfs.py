from __future__ import annotations

import typing

from homelab_pydantic import AbsolutePath, HomelabBaseModel, HomelabRootModel

if typing.TYPE_CHECKING:
    from .user import ContainerUserConfig


class ContainerTmpfsFullConfig(HomelabBaseModel):
    path: AbsolutePath
    exec: bool = False


class ContainerTmpfsConfig(HomelabRootModel[AbsolutePath | ContainerTmpfsFullConfig]):
    def to_path(self) -> AbsolutePath:
        root = self.root
        return root.path if isinstance(root, ContainerTmpfsFullConfig) else root

    def to_args(self, user: ContainerUserConfig | None) -> tuple[AbsolutePath, str]:
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
                        ("uid={}".format(user.uid) if user else ""),
                        ("gid={}".format(user.gid) if user else ""),
                    ],
                )
            )
        )

        return (self.to_path(), option)
