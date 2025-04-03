from __future__ import annotations

import typing
from typing import Any

from homelab_extract import GlobalExtract, GlobalExtractFull, GlobalExtractSource
from homelab_extract.docker import GlobalExtractDockerSource
from homelab_extract.hostname import GlobalExtractHostnameSource
from homelab_extract.id import GlobalExtractIdSource
from homelab_extract.json import GlobalExtractJsonSource
from homelab_extract.name import GlobalExtractNameSource
from homelab_extract.service import ServiceExtractSource
from homelab_extract.simple import GlobalExtractSimpleSource
from homelab_extract.transform import ExtractTransform
from homelab_pydantic import AbsolutePath, HomelabRootModel
from pulumi import Output
from pydantic import ValidationError

from .container import ContainerExtractor
from .docker import GlobalDockerSourceExtractor
from .hostname import GlobalHostnameSourceExtractor
from .id import GlobalIdSourceExtractor
from .json import GlobalJsonSourceExtractor
from .name import GlobalNameSourceExtractor
from .service import ServiceExtractor, ServiceSourceExtractor
from .simple import GlobalSimpleSourceExtractor
from .transform import ExtractTransformer
from .vpn import GlobalVpnSourceExtractor

if typing.TYPE_CHECKING:
    from ..model.container import ContainerModel
    from ..model.container.volume_path import ContainerVolumePath
    from ..resource.service import ServiceResourceBase


class GlobalSourceExtractor(HomelabRootModel[GlobalExtractSource]):
    @property
    def extractor(
        self,
    ) -> (
        GlobalDockerSourceExtractor
        | GlobalHostnameSourceExtractor
        | GlobalIdSourceExtractor
        | GlobalJsonSourceExtractor
        | GlobalNameSourceExtractor
        | GlobalSimpleSourceExtractor
        | GlobalVpnSourceExtractor
    ):
        root = self.root.root
        if isinstance(root, GlobalExtractDockerSource):
            return GlobalDockerSourceExtractor(root)
        elif isinstance(root, GlobalExtractHostnameSource):
            return GlobalHostnameSourceExtractor(root)
        elif isinstance(root, GlobalExtractIdSource):
            return GlobalIdSourceExtractor(root)
        elif isinstance(root, GlobalExtractJsonSource):
            return GlobalJsonSourceExtractor(root)
        elif isinstance(root, GlobalExtractNameSource):
            return GlobalNameSourceExtractor(root)
        elif isinstance(root, GlobalExtractSimpleSource):
            return GlobalSimpleSourceExtractor(root)
        else:
            return GlobalVpnSourceExtractor(root)

    def extract_str(
        self, main_service: ServiceResourceBase, _model: ContainerModel | None
    ) -> str | Output[str]:
        return self.extractor.extract_str(main_service)

    def extract_path(
        self, main_service: ServiceResourceBase, _model: ContainerModel | None
    ) -> AbsolutePath:
        return self.extractor.extract_path(main_service)

    def extract_volume_path(
        self, main_service: ServiceResourceBase, _model: ContainerModel | None
    ) -> ContainerVolumePath:
        return self.extractor.extract_volume_path(main_service)


class GlobalFullExtractor(HomelabRootModel[GlobalExtractFull]):
    @property
    def extractor(self) -> ServiceExtractor | GlobalSourceExtractor:
        extract = self.root.extract
        return (
            GlobalSourceExtractor(extract)
            if isinstance(extract, GlobalExtractSource)
            else ServiceExtractor(extract)
        )

    @property
    def transformer(self) -> ExtractTransformer:
        transform = self.root.transform
        return ExtractTransformer(transform)

    def extract_str(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> Output[str]:
        root = self.root
        extractor = self.extractor
        transformer = self.transformer

        main_service = (
            main_service.SERVICES[root.service] if root.service else main_service
        )
        model = None if root.service else model

        try:
            value_path = transformer.transform_path(
                extractor.extract_path(main_service, model)
            ).as_posix()
            return transformer.transform_string(value_path)
        except (TypeError, ValidationError):
            value_str = extractor.extract_str(main_service, model)
            return transformer.transform_string(value_str)

    def extract_path(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> AbsolutePath:
        root = self.root
        extractor = self.extractor
        transformer = self.transformer

        main_service = (
            main_service.SERVICES[root.service] if root.service else main_service
        )
        model = None if root.service else model

        return transformer.transform_path(extractor.extract_path(main_service, model))

    def extract_volume_path(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> ContainerVolumePath:
        root = self.root
        extractor = self.extractor
        transformer = self.transformer

        main_service = (
            main_service.SERVICES[root.service] if root.service else main_service
        )
        model = None if root.service else model

        return transformer.transform_volume_path(
            extractor.extract_volume_path(main_service, model)
        )


class GlobalExtractor(HomelabRootModel[GlobalExtract]):
    @property
    def extractor(
        self,
    ) -> (
        GlobalSourceExtractor
        | GlobalFullExtractor
        | ServiceSourceExtractor
        | ContainerExtractor
    ):
        root = self.root.root
        if isinstance(root, GlobalExtractSource):
            return GlobalSourceExtractor(root)
        elif isinstance(root, GlobalExtractFull):
            return GlobalFullExtractor(root)
        elif isinstance(root, ServiceExtractSource):
            return ServiceSourceExtractor(root)
        else:
            return ContainerExtractor(root)

    def extract_str(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> Output[str]:
        root = self.root.root

        if isinstance(root, GlobalExtractFull):
            return GlobalFullExtractor(root).extract_str(main_service, model)
        else:
            return ExtractTransformer(ExtractTransform()).transform_string(
                self.extractor.extract_str(main_service, model)
            )

    def extract_path(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> AbsolutePath:
        return self.extractor.extract_path(main_service, model)

    def extract_volume_path(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> ContainerVolumePath:
        return self.extractor.extract_volume_path(main_service, model)

    @classmethod
    def extract_recursively(
        cls, data: Any, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> Any:
        if isinstance(data, dict):
            try:
                extract = GlobalExtract(**data)
                return cls(extract).extract_str(main_service, model)
            except ValidationError:
                return {
                    key: cls.extract_recursively(value, main_service, model)
                    for key, value in data.items()
                }
        elif isinstance(data, list):
            return [
                cls.extract_recursively(value, main_service, model) for value in data
            ]
        else:
            return data
