from __future__ import annotations

import typing
from typing import Any

from homelab_pydantic import AbsolutePath, HomelabBaseModel, HomelabRootModel
from pulumi import Output
from pydantic import ValidationError

from .container import ContainerExtract
from .docker import GlobalExtractDockerSource
from .hostname import GlobalExtractHostnameSource
from .name import GlobalExtractNameSource
from .service import ServiceExtract, ServiceExtractSource
from .simple import GlobalExtractSimpleSource
from .transform import ExtractTransform

if typing.TYPE_CHECKING:
    from ..model.container import ContainerModel
    from ..model.container.volume_path import ContainerVolumePath
    from ..resource.service import ServiceResourceBase


class GlobalExtractSource(
    HomelabRootModel[
        GlobalExtractDockerSource
        | GlobalExtractHostnameSource
        | GlobalExtractNameSource
        | GlobalExtractSimpleSource
    ]
):
    def extract_str(
        self, main_service: ServiceResourceBase, _model: ContainerModel | None
    ) -> str | Output[str]:
        return self.root.extract_str(main_service)

    def extract_path(
        self, main_service: ServiceResourceBase, _model: ContainerModel | None
    ) -> AbsolutePath:
        return self.root.extract_path(main_service)

    def extract_volume_path(
        self, main_service: ServiceResourceBase, _model: ContainerModel | None
    ) -> ContainerVolumePath:
        return self.root.extract_volume_path(main_service)


class GlobalExtractFull(HomelabBaseModel):
    service: str | None = None
    extract: ServiceExtract | GlobalExtractSource
    transform: ExtractTransform = ExtractTransform()

    def extract_str(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> Output[str]:
        extract = self.extract
        transform = self.transform
        main_service = (
            main_service.SERVICES[self.service] if self.service else main_service
        )
        model = None if self.service else model

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
        main_service = (
            main_service.SERVICES[self.service] if self.service else main_service
        )
        model = None if self.service else model

        return transform.transform_path(extract.extract_path(main_service, model))

    def extract_volume_path(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> ContainerVolumePath:
        extract = self.extract
        transform = self.transform
        main_service = (
            main_service.SERVICES[self.service] if self.service else main_service
        )
        model = None if self.service else model

        return transform.transform_volume_path(
            extract.extract_volume_path(main_service, model)
        )


class GlobalExtract(
    HomelabRootModel[
        ContainerExtract
        | ServiceExtractSource
        | GlobalExtractSource
        | GlobalExtractFull
    ]
):
    def extract_str(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> Output[str]:
        root = self.root

        if isinstance(root, GlobalExtractFull):
            return root.extract_str(main_service, model)
        else:
            return ExtractTransform().transform_string(
                root.extract_str(main_service, model)
            )

    def extract_path(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> AbsolutePath:
        return self.root.extract_path(main_service, model)

    def extract_volume_path(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> ContainerVolumePath:
        return self.root.extract_volume_path(main_service, model)

    @classmethod
    def extract_recursively(
        cls, data: Any, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> Any:
        if isinstance(data, dict):
            try:
                return cls(**data).extract_str(main_service, model)
            except ValidationError:
                result = {}
                for key, value in data.items():
                    result[key] = cls.extract_recursively(value, main_service, model)
                return result
        elif isinstance(data, list):
            result_list = []
            for value in data:
                result_list.append(cls.extract_recursively(value, main_service, model))
            return result_list
        else:
            return data
