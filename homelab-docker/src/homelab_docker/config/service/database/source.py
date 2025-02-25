import dataclasses

from pydantic import PositiveInt

from ....model.container.database.source import ContainerDatabaseSourceModel


@dataclasses.dataclass
class ServiceDatabaseSourceConfig:
    postgres: dict[str | None, dict[PositiveInt, ContainerDatabaseSourceModel]]
