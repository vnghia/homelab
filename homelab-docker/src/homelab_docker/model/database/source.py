import dataclasses
import urllib.parse

from pulumi import Input, Output
from pydantic import PositiveInt


@dataclasses.dataclass
class DatabaseSourceModel:
    username: Input[str]
    password: Input[str]
    database: Input[str]
    host: Input[str]
    port: Input[PositiveInt]

    def to_url(self, scheme: str, query: dict[str, str] = {}) -> Output[str]:
        return Output.format(
            "{scheme}://{username}:{password}@{host}:{port}/{database}",
            scheme=scheme,
            username=self.username,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database,
        ).apply(
            lambda x: urllib.parse.urlparse(x)
            ._replace(query=urllib.parse.urlencode(query=query))
            .geturl()
        )


@dataclasses.dataclass
class PostgresDatabaseSourceUrlEnvsFactory:
    env: str
    scheme: str = "postgres"
    query: dict[str, str] = dataclasses.field(
        default_factory=lambda: {"sslmode": "disable"}
    )

    def __call__(self, model: DatabaseSourceModel) -> dict[str, Output[str]]:
        return {self.env: model.to_url(self.scheme, self.query)}
