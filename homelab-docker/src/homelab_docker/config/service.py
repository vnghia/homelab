from abc import abstractmethod

from pydantic import BaseModel

from homelab_docker.config.database import DatabaseConfig


class ServiceConfigBase(BaseModel):
    @property
    @abstractmethod
    def databases(self) -> dict[str, DatabaseConfig]:
        pass
