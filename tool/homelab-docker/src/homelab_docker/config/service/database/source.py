from homelab_pydantic import DatabaseType
from pydantic import PositiveInt

from ....model.docker.container.database.source import ContainerDatabaseSourceModel
from ....model.service.database import ServiceDatabaseConfigModel


class ServiceDatabaseSourceConfig(
    dict[
        DatabaseType,
        dict[
            str | None,
            dict[
                PositiveInt,
                tuple[ContainerDatabaseSourceModel, ServiceDatabaseConfigModel | None],
            ],
        ],
    ]
):
    pass
