from __future__ import annotations

import typing

from homelab_pydantic import AbsolutePath, HomelabBaseModel, HomelabRootModel
from pulumi import Output

from .docker import GlobalExtractDockerSource
from .hostname import GlobalExtractHostnameSource
from .service import ServiceExtract
from .transform import ExtractTransform

if typing.TYPE_CHECKING:
    from ..model.container.volume_path import ContainerVolumePath
    from ..resource.service import ServiceResourceBase


class GlobalExtractSource(
    HomelabRootModel[GlobalExtractDockerSource | GlobalExtractHostnameSource]
):
    def extract_str(self, main_service: ServiceResourceBase) -> str | Output[str]:
        return self.root.extract_str(main_service)

    def extract_path(self, main_service: ServiceResourceBase) -> AbsolutePath:
        return self.root.extract_path(main_service)

    def extract_volume_path(
        self, main_service: ServiceResourceBase
    ) -> ContainerVolumePath:
        return self.root.extract_volume_path(main_service)


class GlobalExtract(HomelabBaseModel):
    service: str | None = None
    extract: ServiceExtract | GlobalExtractSource
    transform: ExtractTransform = ExtractTransform()

    def extract_str(self, main_service: ServiceResourceBase) -> Output[str]:
        extract = self.extract
        transform = self.transform
        main_service = (
            main_service.SERVICES[self.service] if self.service else main_service
        )

        try:
            value_path = transform.transform_path(
                extract.extract_path(main_service)
            ).as_posix()
            return transform.transform_string(value_path)
        except TypeError:
            value_str = extract.extract_str(main_service)
            return transform.transform_string(value_str)

    def extract_path(self, main_service: ServiceResourceBase) -> AbsolutePath:
        extract = self.extract
        transform = self.transform
        main_service = (
            main_service.SERVICES[self.service] if self.service else main_service
        )

        return transform.transform_path(extract.extract_path(main_service))

    def extract_volume_path(
        self, main_service: ServiceResourceBase
    ) -> ContainerVolumePath:
        extract = self.extract
        transform = self.transform
        main_service = (
            main_service.SERVICES[self.service] if self.service else main_service
        )

        return transform.transform_volume_path(
            extract.extract_volume_path(main_service)
        )
