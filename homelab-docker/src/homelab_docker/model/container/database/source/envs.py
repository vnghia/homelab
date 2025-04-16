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

    superuser_password: str | None = None

    def to_envs(self, model: ContainerDatabaseSourceModel) -> dict[str, Output[str]]:
        superuser_password_env = {}
        if self.superuser_password:
            if not model.superuser_password:
                raise ValueError(
                    "Superuser password is not configured for this database"
                )
            superuser_password_env[self.superuser_password] = model.superuser_password

        return {
            k: Output.from_input(v)
            for k, v in (
                ({self.username: model.username} if self.username else {})
                | ({self.password: model.password} if self.password else {})
                | ({self.database: model.database} if self.database else {})
                | ({self.host: model.host} if self.host else {})
                | superuser_password_env
            ).items()
        } | ({self.port: Output.from_input(model.port).apply(str)} if self.port else {})
