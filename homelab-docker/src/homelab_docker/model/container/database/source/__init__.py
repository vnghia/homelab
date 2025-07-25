import dataclasses
import json
import urllib.parse
from abc import abstractmethod

from homelab_pydantic import HomelabBaseModel, HomelabRootModel
from pulumi import Input, Output
from pydantic import PositiveInt


@dataclasses.dataclass
class ContainerDatabaseSourceModel:
    username: Input[str]
    password: Input[str]
    database: Input[str] | None
    host: Input[str]
    port: Input[PositiveInt]

    superuser_password: Input[str] | None

    def to_url(self, scheme: str, query: dict[str, str] | None = None) -> Output[str]:
        if query is None:
            query = {}
        return (
            Output.format(
                "{scheme}://{username}:{password}@{host}:{port}/{database}",
                scheme=scheme,
                username=self.username,
                password=self.password,
                host=self.host,
                port=self.port,
                database=self.database,
            )
            if self.database
            else Output.format(
                "{scheme}://{username}:{password}@{host}:{port}",
                scheme=scheme,
                username=self.username,
                password=self.password,
                host=self.host,
                port=self.port,
            )
        ).apply(
            lambda x: urllib.parse.urlparse(x)
            ._replace(query=urllib.parse.urlencode(query=query))
            .geturl()
        )

    def to_kv(self, query: dict[str, str] | None = None) -> Output[str]:
        if query is None:
            query = {}
        return Output.json_dumps(
            {
                "user": self.username,
                "password": self.password,
                "host": self.host,
                "port": self.port,
                "dbname": self.database,
            }
        ).apply(
            lambda x: " ".join(
                "{}={}".format(k, v) for k, v in (json.loads(x) | query).items()
            )
        )


class ContainerDatabaseSourceEnvsBase(HomelabBaseModel):
    @abstractmethod
    def to_envs(self, model: ContainerDatabaseSourceModel) -> dict[str, Output[str]]:
        pass


class ContainerDatabaseSourceEnvsRootBase[T: ContainerDatabaseSourceEnvsBase](
    HomelabRootModel[T]
):
    def to_envs(self, model: ContainerDatabaseSourceModel) -> dict[str, Output[str]]:
        return self.root.to_envs(model)
