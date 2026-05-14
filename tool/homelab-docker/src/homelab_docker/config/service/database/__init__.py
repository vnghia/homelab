from homelab_pydantic import DatabaseType, HomelabRootModel
from pydantic import model_validator

from ....model.service.database import ServiceDatabaseModel


class ServiceDatabaseConfig(
    HomelabRootModel[dict[DatabaseType, dict[str | None, ServiceDatabaseModel]]]
):
    @model_validator(mode="after")
    def set_none_key(self) -> ServiceDatabaseConfig:
        return self.__class__.model_construct(
            root={
                type_: {type_.get_key(name): model for name, model in config.items()}
                for type_, config in self.root.items()
            }
        )
