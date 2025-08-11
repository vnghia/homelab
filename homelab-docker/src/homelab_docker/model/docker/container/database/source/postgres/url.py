from pulumi import Output

from .. import ContainerDatabaseSourceEnvsBase, ContainerDatabaseSourceModel


class ContainerDatabasePostgresSourceUrlEnvs(ContainerDatabaseSourceEnvsBase):
    env: str
    scheme: str = "postgres"
    query: dict[str, str] = {"sslmode": "disable"}

    def to_envs(self, model: ContainerDatabaseSourceModel) -> dict[str, Output[str]]:
        return {self.env: model.to_url(self.scheme, self.query)}
