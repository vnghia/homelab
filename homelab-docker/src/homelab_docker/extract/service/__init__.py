from __future__ import annotations

import typing

from homelab_extract.service import (
    ServiceExtract,
    ServiceExtractFull,
    ServiceExtractSource,
)
from homelab_extract.service.database import ServiceExtractDatabaseSource
from homelab_extract.service.export import ServiceExtractExportSource
from homelab_extract.service.keepass import ServiceExtractKeepassSource
from homelab_extract.service.secret import ServiceExtractSecretSource
from homelab_pydantic import AbsolutePath
from pulumi import Output
from pydantic import ValidationError

from .. import ExtractorBase
from ..container import ContainerExtractor
from ..transform import ExtractTransformer
from .database import ServiceDatabaseSourceExtractor
from .export import ServiceExportSourceExtractor
from .keepass import ServiceKeepassSourceExtractor
from .secret import ServiceSecretSourceExtractor
from .variable import ServiceVariableSourceExtractor

if typing.TYPE_CHECKING:
    from ...model.container.volume_path import ContainerVolumePath
    from .. import ExtractorArgs


class ServiceSourceExtractor(ExtractorBase[ServiceExtractSource]):
    @property
    def extractor(
        self,
    ) -> (
        ServiceDatabaseSourceExtractor
        | ServiceExportSourceExtractor
        | ServiceKeepassSourceExtractor
        | ServiceSecretSourceExtractor
        | ServiceVariableSourceExtractor
    ):
        root = self.root.root
        if isinstance(root, ServiceExtractDatabaseSource):
            return ServiceDatabaseSourceExtractor(root)
        if isinstance(root, ServiceExtractExportSource):
            return ServiceExportSourceExtractor(root)
        if isinstance(root, ServiceExtractKeepassSource):
            return ServiceKeepassSourceExtractor(root)
        if isinstance(root, ServiceExtractSecretSource):
            return ServiceSecretSourceExtractor(root)
        return ServiceVariableSourceExtractor(root)

    def extract_str(
        self, extractor_args: ExtractorArgs
    ) -> str | Output[str] | dict[str, Output[str]]:
        return self.extractor.extract_str(extractor_args)

    def extract_path(self, extractor_args: ExtractorArgs) -> AbsolutePath:
        return self.extractor.extract_path(extractor_args)

    def extract_volume_path(self, extractor_args: ExtractorArgs) -> ContainerVolumePath:
        return self.extractor.extract_volume_path(extractor_args)


class ServiceFullExtractor(ExtractorBase[ServiceExtractFull]):
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

    def extractor_args(self, extractor_args: ExtractorArgs) -> ExtractorArgs:
        root = self.root

        return extractor_args.with_container(
            extractor_args.get_container(root.container)
            if root.has_container
            else extractor_args._container
            or extractor_args.get_container(root.container)
        )

    def extract_str(self, extractor_args: ExtractorArgs) -> str | Output[str]:
        extractor = self.extractor
        transformer = self.transfomer
        extractor_args = self.extractor_args(extractor_args)

        try:
            value_path = transformer.transform_path(
                extractor.extract_path(extractor_args)
            ).as_posix()
            return transformer.transform_string(value_path)
        except (TypeError, ValidationError):
            value_str = extractor.extract_str(extractor_args)
            return transformer.transform_string(value_str)

    def extract_path(self, extractor_args: ExtractorArgs) -> AbsolutePath:
        extractor = self.extractor
        transformer = self.transfomer
        extractor_args = self.extractor_args(extractor_args)

        return transformer.transform_path(extractor.extract_path(extractor_args))

    def extract_volume_path(self, extractor_args: ExtractorArgs) -> ContainerVolumePath:
        extractor = self.extractor
        transformer = self.transfomer
        extractor_args = self.extractor_args(extractor_args)

        return transformer.transform_volume_path(
            extractor.extract_volume_path(extractor_args)
        )


class ServiceExtractor(ExtractorBase[ServiceExtract]):
    @property
    def container(self) -> str | None:
        root = self.root.root
        return root.container if isinstance(root, ServiceExtractFull) else None

    @classmethod
    def get_extractor(
        cls, source: ServiceExtract
    ) -> ServiceSourceExtractor | ServiceFullExtractor:
        root = source.root
        if isinstance(root, ServiceExtractSource):
            return ServiceSourceExtractor(root)
        if isinstance(root, ServiceExtractFull):
            return ServiceFullExtractor(root)
        return cls.get_extractor(ServiceExtract(ServiceExtractFull(extract=root)))

    @property
    def extractor(
        self,
    ) -> ServiceSourceExtractor | ServiceFullExtractor:
        return self.get_extractor(self.root)

    def extract_str(
        self, extractor_args: ExtractorArgs
    ) -> str | Output[str] | dict[str, Output[str]]:
        return self.extractor.extract_str(extractor_args)

    def extract_path(self, extractor_args: ExtractorArgs) -> AbsolutePath:
        return self.extractor.extract_path(extractor_args)

    def extract_volume_path(self, extractor_args: ExtractorArgs) -> ContainerVolumePath:
        return self.extractor.extract_volume_path(extractor_args)
