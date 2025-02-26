from pydantic import PositiveInt

from homelab_docker.model.database.type import DatabaseType

from ....model.container.database.source import ContainerDatabaseSourceModel


class ServiceDatabaseSourceConfig(
    dict[
        DatabaseType, dict[str | None, dict[PositiveInt, ContainerDatabaseSourceModel]]
    ]
):
    pass
