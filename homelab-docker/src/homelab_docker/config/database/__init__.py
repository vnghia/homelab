from typing import Self

from homelab_pydantic import HomelabRootModel
from pydantic import model_validator

from ...model.database.postgres import PostgresDatabaseModel
from ...model.database.type import DatabaseType


class DatabaseConfig(
    HomelabRootModel[dict[DatabaseType, dict[str | None, PostgresDatabaseModel]]]
):
    @model_validator(mode="after")
    def set_none_key(self) -> Self:
        return self.model_construct(
            root={
                type_: {type_.get_key(name): model for name, model in config.items()}
                for type_, config in self.root.items()
            }
        )
