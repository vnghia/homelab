from homelab_docker.model.database.type import DatabaseType
from homelab_pydantic import HomelabRootModel


class ResticDatabaseConfig(HomelabRootModel[dict[DatabaseType, str]]):
    root: dict[DatabaseType, str] = {}

    def find(self, volume: str) -> DatabaseType | None:
        root = self.root
        for type_, name in root.items():
            if name == volume:
                return type_
        return None
