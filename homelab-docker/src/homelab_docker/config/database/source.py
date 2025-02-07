import dataclasses

from pydantic import PositiveInt

from homelab_docker.model.database.source import DatabaseSourceModel


@dataclasses.dataclass
class DatabaseSourceConfig:
    postgres: dict[str | None, dict[PositiveInt, DatabaseSourceModel]]
