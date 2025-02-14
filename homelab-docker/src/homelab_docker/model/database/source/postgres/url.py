import typing

from pulumi import Output
from pydantic import BaseModel

if typing.TYPE_CHECKING:
    from .. import DatabaseSourceModel


class PostgresDatabaseSourceUrlEnvs(BaseModel):
    env: str
    scheme: str = "postgres"
    query: dict[str, str] = {"sslmode": "disable"}

    def to_envs(self, model: "DatabaseSourceModel") -> dict[str, Output[str]]:
        return {self.env: model.to_url(self.scheme, self.query)}
