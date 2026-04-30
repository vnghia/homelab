from homelab_pydantic import HomelabBaseModel


class ContainerCapConfig(HomelabBaseModel):
    add: list[str] | None = None
    drop: list[str] | None = ["ALL"]

    def __bool__(self) -> bool:
        return bool(self.add) or bool(self.drop)
