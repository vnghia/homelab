from homelab_pydantic import HomelabBaseModel
from pydantic import PositiveInt


class ServiceDatabaseModel(HomelabBaseModel):
    image: str | None = None
    versions: list[PositiveInt] = []
