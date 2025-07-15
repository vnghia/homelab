from homelab_pydantic import HomelabBaseModel
from homelab_pydantic.model import HomelabRootModel
from pydantic import PositiveInt

from .postgres import ServiceDatabasePostgresConfigModel


class ServiceDatabaseInitScriptModel(HomelabBaseModel):
    path: str
    content: str


class ServiceDatabaseConfigModel(HomelabRootModel[ServiceDatabasePostgresConfigModel]):
    pass


class ServiceDatabaseModel(HomelabBaseModel):
    image: str | None = None
    versions: list[PositiveInt] = []
    scripts: list[ServiceDatabaseInitScriptModel] = []
    config: ServiceDatabaseConfigModel | None = None
