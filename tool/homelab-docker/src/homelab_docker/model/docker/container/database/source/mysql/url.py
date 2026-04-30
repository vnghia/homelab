from pulumi import Output

from .. import ContainerDatabaseSourceEnvsBase, ContainerDatabaseSourceModel


class ContainerDatabaseMysqlSourceUrlEnvs(ContainerDatabaseSourceEnvsBase):
    env: str
    scheme: str = "mysql"
    query: dict[str, str] = {}

    def to_envs(self, model: ContainerDatabaseSourceModel) -> dict[str, Output[str]]:
        return {self.env: model.to_url(self.scheme, self.query)}
