from __future__ import annotations

import typing

from homelab_pydantic import AbsolutePath, HomelabBaseModel, HomelabRootModel

from ..volume_path import ContainerVolumePath
from .source import ContainerExtractSource
from .transform import ContainerExtractTransform

if typing.TYPE_CHECKING:
    from ....resource.service import ServiceResourceBase
    from .. import ContainerModel


class ContainerFullExtract(HomelabBaseModel):
    source: ContainerExtractSource
    transform: ContainerExtractTransform = ContainerExtractTransform()

    def extract_str(
        self, model: ContainerModel, main_service: ServiceResourceBase
    ) -> str:
        try:
            value = self.transform.transform_path(
                self.source.extract_path(model, main_service)
            ).as_posix()
        except TypeError:
            value = self.source.extract_str(model, main_service)
        return self.transform.transform_string(value)

    def extract_path(
        self, model: ContainerModel, main_service: ServiceResourceBase
    ) -> AbsolutePath:
        return self.transform.transform_path(
            self.source.extract_path(model, main_service)
        )

    def extract_volume_path(
        self, model: ContainerModel, main_service: ServiceResourceBase
    ) -> ContainerVolumePath:
        return self.transform.transform_volume_path(
            self.source.extract_volume_path(model, main_service)
        )


class ContainerExtract(HomelabRootModel[ContainerFullExtract | ContainerExtractSource]):
    def extract_str(
        self, model: ContainerModel, main_service: ServiceResourceBase
    ) -> str:
        return self.root.extract_str(model, main_service)

    def extract_path(
        self, model: ContainerModel, main_service: ServiceResourceBase
    ) -> AbsolutePath:
        return self.root.extract_path(model, main_service)

    def extract_volume_path(
        self, model: ContainerModel, main_service: ServiceResourceBase
    ) -> ContainerVolumePath:
        return self.root.extract_volume_path(model, main_service)
