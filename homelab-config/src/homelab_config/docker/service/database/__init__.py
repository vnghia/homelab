from pydantic import BaseModel, ConfigDict

from homelab_config.docker.service.database.postgres import Postgres


class Database(BaseModel):
    model_config = ConfigDict(strict=True)

    postgres: dict[str, Postgres] = {}
