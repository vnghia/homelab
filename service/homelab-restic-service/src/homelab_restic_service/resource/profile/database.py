from __future__ import annotations

import typing
from pathlib import PosixPath

from homelab_docker.model.volume import LocalVolumeModel
from homelab_pydantic import RelativePath
from pulumi import ResourceOptions

from ...config.volume import ResticVolumeConfig
from ...model.profile import ResticProfileModel
from ...model.profile.database import ResticProfileDatabaseModel
from . import ResticProfileResource

if typing.TYPE_CHECKING:
    from ... import ResticService


class ResticProfileDatabaseResource(
    ResticProfileResource, module="restic", name="Profile"
):
    def __init__(
        self,
        model: ResticProfileDatabaseModel,
        *,
        opts: ResourceOptions | None,
        restic_service: ResticService,
    ):
        self.type_ = model.type_

        super().__init__(
            ResticProfileModel(
                volume=ResticVolumeConfig(
                    name=model.name,
                    model=LocalVolumeModel(),
                    relative=RelativePath(PosixPath(model.type_)) / model.name,
                ),
                tags=[model.type_.value],
            ),
            opts=opts,
            restic_service=restic_service,
        )
