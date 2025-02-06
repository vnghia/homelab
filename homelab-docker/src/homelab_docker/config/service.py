from abc import abstractmethod

from pydantic import BaseModel

from homelab_docker.model.database import DatabaseModel


class ServiceConfigBase(BaseModel):
    @property
    @abstractmethod
    def databases(self) -> dict[str, DatabaseModel]:
        pass
