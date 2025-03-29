from __future__ import annotations

import typing
from pathlib import PosixPath

from homelab_docker.model.database.type import DatabaseType
from homelab_docker.model.volume import LocalVolumeModel
from homelab_pydantic import HomelabBaseModel, RelativePath
from pulumi import ResourceOptions

from . import ResticProfileModel

if typing.TYPE_CHECKING:
    from .. import ResticService
    from ..resource.profile import ResticProfileResource


class ResticProfileDatabaseModel(HomelabBaseModel):
    type_: DatabaseType
    name: str

    def build_resource(
        self,
        *,
        opts: ResourceOptions | None,
        restic_service: ResticService,
    ) -> ResticProfileResource:
        from ..config.volume import ResticVolumeConfig
        from ..resource.profile import ResticProfileResource

        return ResticProfileResource(
            ResticProfileModel(
                volume=ResticVolumeConfig(
                    name=self.name,
                    model=LocalVolumeModel(),
                    relative=RelativePath(PosixPath(self.type_)) / self.name,
                ),
                tags=[self.type_.value],
            ),
            opts=opts,
            restic_service=restic_service,
        )
