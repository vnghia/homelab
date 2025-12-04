from homelab_pydantic import HomelabBaseModel, HomelabRootModel

from .host import ResticHost


class ResticRepository(HomelabBaseModel):
    host: ResticHost

    @property
    def repository(self) -> str:
        return self.host.repository


class ResticConfig(HomelabRootModel[dict[str, ResticRepository]]):
    root: dict[str, ResticRepository] = {}

    def __getitem__(self, key: str) -> ResticRepository:
        return self.root[key]
