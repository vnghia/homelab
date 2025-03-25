from homelab_pydantic import AbsolutePath, HomelabBaseModel, HomelabRootModel


class ContainerTmpfsFullConfig(HomelabBaseModel):
    path: AbsolutePath
    exec: bool = False


class ContainerTmpfsConfig(HomelabRootModel[AbsolutePath | ContainerTmpfsFullConfig]):
    def to_args(self) -> tuple[AbsolutePath, str]:
        root = self.root
        target = root.path if isinstance(root, ContainerTmpfsFullConfig) else root
        option = (
            "exec"
            if isinstance(root, ContainerTmpfsFullConfig) and root.exec
            else "noexec"
        )

        return (target, option)
