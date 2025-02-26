from __future__ import annotations

import typing

from homelab_pydantic import AbsolutePath, HomelabBaseModel, HomelabRootModel
from pulumi import Output

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
    ) -> Output[str]:
        try:
            value_path = self.transform.transform_path(
                self.source.extract_path(model, main_service)
            ).as_posix()
            return self.transform.transform_string(value_path)
        except TypeError:
            value_str = self.source.extract_str(model, main_service)
            return self.transform.transform_string(value_str)

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
    ) -> Output[str]:
        root = self.root
        if isinstance(root, ContainerFullExtract):
            return root.extract_str(model, main_service)
        else:
            return ContainerExtractTransform().transform_string(
                root.extract_str(model, main_service)
            )

    def extract_path(
        self, model: ContainerModel, main_service: ServiceResourceBase
    ) -> AbsolutePath:
        return self.root.extract_path(model, main_service)

    def extract_volume_path(
        self, model: ContainerModel, main_service: ServiceResourceBase
    ) -> ContainerVolumePath:
        return self.root.extract_volume_path(model, main_service)
