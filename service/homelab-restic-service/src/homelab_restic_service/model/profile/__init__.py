from __future__ import annotations

import typing
from typing import ClassVar

from homelab_docker.model.docker.volume import LocalVolumeModel
from homelab_pydantic import HomelabBaseModel
from pulumi import ResourceOptions

from ...config.volume import ResticVolumeConfig

if typing.TYPE_CHECKING:
    from ... import ResticService
    from ...resource.profile import ResticProfileResource


class ResticProfileModel(HomelabBaseModel):
    DEFAULT_VOLUME_MODEL: ClassVar[LocalVolumeModel] = LocalVolumeModel()

    volume: ResticVolumeConfig
    tags: list[str] = []

    def build_resource(
        self,
        *,
        opts: ResourceOptions,
        restic_service: ResticService,
    ) -> ResticProfileResource:
        from ...resource.profile import ResticProfileResource

        return ResticProfileResource(self, opts=opts, restic_service=restic_service)
