from __future__ import annotations

import typing

from homelab_pydantic import HomelabBaseModel
from pulumi import Output

if typing.TYPE_CHECKING:
    from .. import ContainerDatabaseSourceModel


class ContainerPostgresDatabaseSourceUrlEnvs(HomelabBaseModel):
    env: str
    scheme: str = "postgres"
    query: dict[str, str] = {"sslmode": "disable"}

    def to_envs(self, model: ContainerDatabaseSourceModel) -> dict[str, Output[str]]:
        return {self.env: model.to_url(self.scheme, self.query)}
