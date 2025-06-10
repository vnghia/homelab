from pulumi import Output
from pydantic import NonNegativeInt

from .. import ContainerDatabaseSourceEnvsBase, ContainerDatabaseSourceModel


class ContainerDatabaseRedisSourceUrlEnvs(ContainerDatabaseSourceEnvsBase):
    env: str
    scheme: str = "redis"
    database: NonNegativeInt | None = 0

    def to_envs(self, model: ContainerDatabaseSourceModel) -> dict[str, Output[str]]:
        return {
            self.env: model.__replace__(
                database=str(self.database) if self.database is not None else None
            ).to_url(self.scheme)
        }
