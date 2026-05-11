from homelab_pydantic import HomelabBaseModel


class HatchetServiceDockerConfig(HomelabBaseModel):
    models: set[str | None] = set()
    names: set[str | None] = set()

    def __bool__(self) -> bool:
        return bool(self.models) or bool(self.names)
