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
        database_env = {}
        if self.database:
            if not model.database:
                raise ValueError("Database is not configured for this database")
            database_env[self.database] = model.database

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
                | ({self.host: model.host} if self.host else {})
                | database_env
                | superuser_password_env
            ).items()
        } | ({self.port: Output.from_input(model.port).apply(str)} if self.port else {})
