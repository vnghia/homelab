from abc import abstractmethod

from homelab_pydantic import HomelabBaseModel

from ..config.database import DatabaseConfig


class ServiceConfigBase(HomelabBaseModel):
    @property
    @abstractmethod
    def databases(self) -> dict[str, DatabaseConfig]:
        pass
