from __future__ import annotations

import typing

from homelab_pydantic import HomelabBaseModel
from pulumi import ResourceOptions

if typing.TYPE_CHECKING:
    from .. import ResticService
    from ..resource.profile import ResticProfileResource


class ResticProfileModel(HomelabBaseModel):
    volume: str

    def build_resource(
        self,
        *,
        opts: ResourceOptions | None,
        restic_service: ResticService,
    ) -> ResticProfileResource:
        from ..resource.profile import ResticProfileResource

        return ResticProfileResource(self, opts=opts, restic_service=restic_service)
