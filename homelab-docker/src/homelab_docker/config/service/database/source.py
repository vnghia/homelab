from pydantic import PositiveInt

from ....model.container.database.source import ContainerDatabaseSourceModel
from ....model.database.type import DatabaseType
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
