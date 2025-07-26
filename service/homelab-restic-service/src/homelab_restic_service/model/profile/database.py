from __future__ import annotations

import typing

from homelab_docker.model.database.type import DatabaseType
from homelab_pydantic import HomelabBaseModel, RelativePath
from pulumi import ResourceOptions

if typing.TYPE_CHECKING:
    from ... import ResticService
    from ...resource.profile.database import ResticProfileDatabaseResource


class ResticProfileDatabaseModel(HomelabBaseModel):
    type_: DatabaseType
    name: str
    path: RelativePath | None = None

    def build_resource(
        self,
        *,
        opts: ResourceOptions,
        restic_service: ResticService,
    ) -> ResticProfileDatabaseResource:
        from ...resource.profile.database import ResticProfileDatabaseResource

        return ResticProfileDatabaseResource(
            self,
            opts=opts,
            restic_service=restic_service,
        )
