from __future__ import annotations

import typing

import pulumi_random as random
from homelab_pydantic import AbsolutePath, HomelabBaseModel, HomelabRootModel
from pulumi import Output

from ..container import ContainerExtract
from ..transform import ExtractTransform
from .export import ServiceExtractExportSource
from .keepass import ServiceExtractKeepassSource
from .secret import ServiceExtractSecretSource
from .variable import ServiceExtractVariableSource

if typing.TYPE_CHECKING:
    from ...model.container import ContainerModel
    from ...model.container.volume_path import ContainerVolumePath
    from ...resource.service import ServiceResourceBase


class ServiceExtractSource(
    HomelabRootModel[
        ServiceExtractExportSource
        | ServiceExtractKeepassSource
        | ServiceExtractSecretSource
        | ServiceExtractVariableSource
    ]
):
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


class ServiceExtractFull(HomelabBaseModel):
    container: str | None = None
    extract: ContainerExtract | ServiceExtractSource
    transform: ExtractTransform = ExtractTransform()

    def extract_str(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> str | Output[str] | random.RandomPassword:
        extract = self.extract
        transform = self.transform

        try:
            value_path = transform.transform_path(
                extract.extract_path(main_service, model)
            ).as_posix()
            return transform.transform_string(value_path)
        except TypeError:
            value_str = extract.extract_str(main_service, model)
            return transform.transform_string(value_str)

    def extract_path(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> AbsolutePath:
        extract = self.extract
        transform = self.transform

        return transform.transform_path(extract.extract_path(main_service, model))

    def extract_volume_path(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> ContainerVolumePath:
        extract = self.extract
        transform = self.transform

        return transform.transform_volume_path(
            extract.extract_volume_path(main_service, model)
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

    def extract_output_str(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> Output[str]:
        return ExtractTransform().transform_string(
            self.root.extract_str(main_service, model)
        )
