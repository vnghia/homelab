from __future__ import annotations

import typing
from typing import Never

from homelab_pydantic import HomelabBaseModel
from pydantic import Field

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
                k.removeprefix("pulumi."): v
                for k, v in main_service.docker_resource_args.project_labels.items()
            },
        )

    def extract_path(
        self, _model: ContainerModel, _main_service: ServiceResourceBase
    ) -> Never:
        raise TypeError("Can not extract path from global source")

    def extract_volume_path(
        self, _model: ContainerModel, _main_service: ServiceResourceBase
    ) -> Never:
        raise TypeError("Can not extract volume path from global source")
