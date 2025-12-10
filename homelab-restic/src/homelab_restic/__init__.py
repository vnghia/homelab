from homelab_pydantic import HomelabBaseModel

from .model import ResticRepositoryModel


class ResticConfig(HomelabBaseModel):
    default: str
    repositories: dict[str, ResticRepositoryModel] = {}

    def __getitem__(self, key: str) -> ResticRepositoryModel:
        return self.repositories[key]
