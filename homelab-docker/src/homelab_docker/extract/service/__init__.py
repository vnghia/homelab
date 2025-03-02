from __future__ import annotations

import typing

import pulumi_random as random
from homelab_pydantic import AbsolutePath, HomelabBaseModel, HomelabRootModel
from pulumi import Output

from ..container import ContainerExtract
from .secret import ServiceExtractSecretSource
from .variable import ServiceExtractVariableSource

if typing.TYPE_CHECKING:
    from ...model.container import ContainerModel
    from ...model.container.volume_path import ContainerVolumePath
    from ...resource.service import ServiceResourceBase


class ServiceExtractSource(
    HomelabRootModel[ServiceExtractSecretSource | ServiceExtractVariableSource]
):
    def extract_str(
        self, main_service: ServiceResourceBase, _model: ContainerModel | None
    ) -> str | Output[str] | random.RandomPassword:
        return self.root.extract_str(main_service)

    def extract_path(
        self, main_service: ServiceResourceBase, _model: ContainerModel | None
    ) -> AbsolutePath:
        return self.root.extract_path(main_service)

    def extract_volume_path(
        self, main_service: ServiceResourceBase, _model: ContainerModel | None
    ) -> ContainerVolumePath:
        return self.root.extract_volume_path(main_service)


class ServiceExtractFull(HomelabBaseModel):
    container: str | None = None
    extract: ContainerExtract | ServiceExtractSource

    def extract_str(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> str | Output[str] | random.RandomPassword:
        return self.extract.extract_str(
            main_service, model or main_service.model[self.container]
        )

    def extract_path(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> AbsolutePath:
        return self.extract.extract_path(
            main_service, model or main_service.model[self.container]
        )

    def extract_volume_path(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> ContainerVolumePath:
        return self.extract.extract_volume_path(
            main_service, model or main_service.model[self.container]
        )


class ServiceExtract(
    HomelabRootModel[ContainerExtract | ServiceExtractSource | ServiceExtractFull]
):
    @property
    def container(self) -> str | None:
        root = self.root

        return root.container if isinstance(root, ServiceExtractFull) else None

    def extract_str(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> str | Output[str] | random.RandomPassword:
        return self.root.extract_str(main_service, model)

    def extract_path(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> AbsolutePath:
        return self.root.extract_path(main_service, model)

    def extract_volume_path(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> ContainerVolumePath:
        return self.root.extract_volume_path(main_service, model)
