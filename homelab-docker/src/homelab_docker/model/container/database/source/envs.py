from __future__ import annotations

import typing

from pulumi import Output

from ..source import ContainerDatabaseSourceEnvsBase

if typing.TYPE_CHECKING:
    from . import ContainerDatabaseSourceModel


class ContainerDatabaseSourceEnvs(ContainerDatabaseSourceEnvsBase):
    username: str | None = None
    password: str | None = None
    database: str | None = None
    host: str | None = None
    port: str | None = None

    def to_envs(self, model: ContainerDatabaseSourceModel) -> dict[str, Output[str]]:
        return {
            k: Output.from_input(v)
            for k, v in (
                ({self.username: model.username} if self.username else {})
                | ({self.password: model.password} if self.password else {})
                | ({self.database: model.database} if self.database else {})
                | ({self.host: model.host} if self.host else {})
            ).items()
        } | ({self.port: Output.from_input(model.port).apply(str)} if self.port else {})
