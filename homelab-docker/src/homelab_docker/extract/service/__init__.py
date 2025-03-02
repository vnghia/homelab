from __future__ import annotations

import typing

import pulumi_random as random
from homelab_pydantic import AbsolutePath, HomelabBaseModel, HomelabRootModel
from pulumi import Output

from ..container import ContainerExtract
from .secret import ServiceExtractSecretSource

if typing.TYPE_CHECKING:
    from ...model.container.volume_path import ContainerVolumePath
    from ...resource.service import ServiceResourceBase


class ServiceExtractSource(HomelabRootModel[ServiceExtractSecretSource]):
    def extract_str(
        self, main_service: ServiceResourceBase
    ) -> str | Output[str] | random.RandomPassword:
        return self.root.extract_str(main_service)

    def extract_path(self, main_service: ServiceResourceBase) -> AbsolutePath:
        return self.root.extract_path(main_service)

    def extract_volume_path(
        self, main_service: ServiceResourceBase
    ) -> ContainerVolumePath:
        return self.root.extract_volume_path(main_service)


class ServiceExtract(HomelabBaseModel):
    container: str | None = None
    extract: ContainerExtract | ServiceExtractSource

    def extract_str(
        self, main_service: ServiceResourceBase
    ) -> str | Output[str] | random.RandomPassword:
        extract = self.extract

        if isinstance(extract, ContainerExtract):
            return extract.extract_str(main_service.model[self.container], main_service)
        else:
            return extract.extract_str(main_service)

    def extract_path(self, main_service: ServiceResourceBase) -> AbsolutePath:
        extract = self.extract

        if isinstance(extract, ContainerExtract):
            return extract.extract_path(
                main_service.model[self.container], main_service
            )
        else:
            return extract.extract_path(main_service)

    def extract_volume_path(
        self, main_service: ServiceResourceBase
    ) -> ContainerVolumePath:
        extract = self.extract

        if isinstance(extract, ContainerExtract):
            return extract.extract_volume_path(
                main_service.model[self.container], main_service
            )
        else:
            return extract.extract_volume_path(main_service)
