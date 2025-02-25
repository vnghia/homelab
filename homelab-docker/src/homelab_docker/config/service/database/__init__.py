from typing import Self

from homelab_pydantic import HomelabRootModel
from pydantic import model_validator

from ....model.database.type import DatabaseType
from ....model.service.database.postgres import ServicePostgresDatabaseModel


class ServiceDatabaseConfig(
    HomelabRootModel[dict[DatabaseType, dict[str | None, ServicePostgresDatabaseModel]]]
):
    @model_validator(mode="after")
    def set_none_key(self) -> Self:
        return self.model_construct(
            root={
                type_: {type_.get_key(name): model for name, model in config.items()}
                for type_, config in self.root.items()
            }
        )
