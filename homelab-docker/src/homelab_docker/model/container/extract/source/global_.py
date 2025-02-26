from __future__ import annotations

import typing

from homelab_pydantic import AbsolutePath, HomelabBaseModel
from pydantic import Field

from ...volume_path import ContainerVolumePath

if typing.TYPE_CHECKING:
    from .....resource.service import ServiceResourceBase
    from ... import ContainerModel


class ContainerExtractGlobalSource(HomelabBaseModel):
    global_: str = Field(alias="global")

    def extract_str(
        self, _model: ContainerModel, main_service: ServiceResourceBase
    ) -> str:
        return self.global_.format(
            timezone=main_service.docker_resource_args.timezone,
            **{
                k.strip("pulumi."): v
                for k, v in main_service.docker_resource_args.project_labels.items()
            },
        )

    def extract_path(
        self, _model: ContainerModel, _main_service: ServiceResourceBase
    ) -> AbsolutePath:
        raise TypeError("Can not extract path from global source")

    def extract_volume_path(
        self, _model: ContainerModel, _main_service: ServiceResourceBase
    ) -> ContainerVolumePath:
        raise TypeError("Can not extract volume path from global source")
