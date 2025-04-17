from homelab_pydantic import HomelabBaseModel
from pydantic import PositiveInt


class ServiceDatabaseInitScriptModel(HomelabBaseModel):
    path: str
    content: str


class ServiceDatabaseModel(HomelabBaseModel):
    image: str | None = None
    versions: list[PositiveInt] = []
    scripts: list[ServiceDatabaseInitScriptModel] = []
