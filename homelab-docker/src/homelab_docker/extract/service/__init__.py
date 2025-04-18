from __future__ import annotations

import typing

import pulumi_random as random
from homelab_extract.service import (
    ServiceExtract,
    ServiceExtractFull,
    ServiceExtractSource,
)
from homelab_extract.service.export import ServiceExtractExportSource
from homelab_extract.service.keepass import ServiceExtractKeepassSource
from homelab_extract.service.secret import ServiceExtractSecretSource
from homelab_extract.transform import ExtractTransform
from homelab_pydantic import AbsolutePath, HomelabRootModel
from pulumi import Output

from ..container import ContainerExtractor
from ..transform import ExtractTransformer
from .export import ServiceExportSourceExtractor
from .keepass import ServiceKeepassSourceExtractor
from .secret import ServiceSecretSourceExtractor
from .variable import ServiceVariableSourceExtractor

if typing.TYPE_CHECKING:
    from ...model.container import ContainerModel
    from ...model.container.volume_path import ContainerVolumePath
    from ...resource.service import ServiceResourceBase


class ServiceSourceExtractor(HomelabRootModel[ServiceExtractSource]):
    @property
    def extractor(
        self,
    ) -> (
        ServiceExportSourceExtractor
        | ServiceKeepassSourceExtractor
        | ServiceSecretSourceExtractor
        | ServiceVariableSourceExtractor
    ):
        root = self.root.root
        if isinstance(root, ServiceExtractExportSource):
            return ServiceExportSourceExtractor(root)
        if isinstance(root, ServiceExtractKeepassSource):
            return ServiceKeepassSourceExtractor(root)
        if isinstance(root, ServiceExtractSecretSource):
            return ServiceSecretSourceExtractor(root)
        return ServiceVariableSourceExtractor(root)

    def extract_str(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> str | Output[str] | random.RandomPassword | random.RandomUuid:
        return self.extractor.extract_str(main_service, model)

    def extract_path(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> AbsolutePath:
        return self.extractor.extract_path(main_service, model)

    def extract_volume_path(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> ContainerVolumePath:
        return self.extractor.extract_volume_path(main_service, model)


class ServiceFullExtractor(HomelabRootModel[ServiceExtractFull]):
    @property
    def extractor(self) -> ServiceSourceExtractor | ContainerExtractor:
        extract = self.root.extract
        return (
            ServiceSourceExtractor(extract)
            if isinstance(extract, ServiceExtractSource)
            else ContainerExtractor(extract)
        )

    @property
    def transfomer(self) -> ExtractTransformer:
        transform = self.root.transform
        return ExtractTransformer(transform)

    def extract_str(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> str | Output[str] | random.RandomPassword:
        extractor = self.extractor
        transformer = self.transfomer

        try:
            value_path = transformer.transform_path(
                extractor.extract_path(main_service, model)
            ).as_posix()
            return transformer.transform_string(value_path)
        except TypeError:
            value_str = extractor.extract_str(main_service, model)
            return transformer.transform_string(value_str)

    def extract_path(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> AbsolutePath:
        extractor = self.extractor
        transformer = self.transfomer

        return transformer.transform_path(extractor.extract_path(main_service, model))

    def extract_volume_path(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> ContainerVolumePath:
        extractor = self.extractor
        transformer = self.transfomer

        return transformer.transform_volume_path(
            extractor.extract_volume_path(main_service, model)
        )


class ServiceExtractor(HomelabRootModel[ServiceExtract]):
    @property
    def container(self) -> str | None:
        root = self.root.root
        return root.container if isinstance(root, ServiceExtractFull) else None

    @property
    def extractor(
        self,
    ) -> ContainerExtractor | ServiceSourceExtractor | ServiceFullExtractor:
        root = self.root.root
        if isinstance(root, ServiceExtractSource):
            return ServiceSourceExtractor(root)
        if isinstance(root, ServiceExtractFull):
            return ServiceFullExtractor(root)
        return ContainerExtractor(root)

    def extract_str(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> str | Output[str] | random.RandomPassword | random.RandomUuid:
        return self.extractor.extract_str(main_service, model)

    def extract_path(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> AbsolutePath:
        return self.extractor.extract_path(main_service, model)

    def extract_volume_path(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> ContainerVolumePath:
        return self.extractor.extract_volume_path(main_service, model)

    def extract_output_str(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> Output[str]:
        return ExtractTransformer(ExtractTransform()).transform_string(
            self.extractor.extract_str(main_service, model)
        )
