from __future__ import annotations

import typing
from typing import Any

from homelab_extract import GlobalExtract, GlobalExtractFull, GlobalExtractSource
from homelab_extract.dict_ import GlobalExtractDictSource
from homelab_extract.host import GlobalExtractHostSource
from homelab_extract.hostname import GlobalExtractHostnameSource
from homelab_extract.json import GlobalExtractJsonSource
from homelab_extract.kv import GlobalExtractKvSource
from homelab_extract.project import GlobalExtractProjectSource
from homelab_extract.service import ServiceExtract
from homelab_extract.simple import GlobalExtractSimpleSource
from homelab_extract.transform import ExtractTransform
from homelab_extract.vpn import GlobalExtractVpnSource
from homelab_pydantic import AbsolutePath
from pulumi import Output
from pydantic import ValidationError

from . import ExtractorBase
from .container import ContainerExtractor
from .dict_ import GlobalDictSourceExtractor
from .host import GlobalHostSourceExtractor
from .hostname import GlobalHostnameSourceExtractor
from .json import GlobalJsonSourceExtractor
from .kv import GlobalKvSourceExtractor
from .project import GlobalProjectSourceExtractor
from .service import ServiceExtractor, ServiceSourceExtractor
from .simple import GlobalSimpleSourceExtractor
from .transform import ExtractTransformer
from .vpn import GlobalVpnSourceExtractor
from .yaml import GlobalYamlSourceExtractor

if typing.TYPE_CHECKING:
    from ..model.container.volume_path import ContainerVolumePath
    from . import ExtractorArgs


class GlobalSourceExtractor(ExtractorBase[GlobalExtractSource]):
    @property
    def extractor(
        self,
    ) -> (
        GlobalDictSourceExtractor
        | GlobalHostSourceExtractor
        | GlobalHostnameSourceExtractor
        | GlobalJsonSourceExtractor
        | GlobalKvSourceExtractor
        | GlobalProjectSourceExtractor
        | GlobalSimpleSourceExtractor
        | GlobalVpnSourceExtractor
        | GlobalYamlSourceExtractor
    ):
        root = self.root.root
        if isinstance(root, GlobalExtractDictSource):
            return GlobalDictSourceExtractor(root)
        if isinstance(root, GlobalExtractHostSource):
            return GlobalHostSourceExtractor(root)
        if isinstance(root, GlobalExtractHostnameSource):
            return GlobalHostnameSourceExtractor(root)
        if isinstance(root, GlobalExtractJsonSource):
            return GlobalJsonSourceExtractor(root)
        if isinstance(root, GlobalExtractKvSource):
            return GlobalKvSourceExtractor(root)
        if isinstance(root, GlobalExtractProjectSource):
            return GlobalProjectSourceExtractor(root)
        if isinstance(root, GlobalExtractSimpleSource):
            return GlobalSimpleSourceExtractor(root)
        if isinstance(root, GlobalExtractVpnSource):
            return GlobalVpnSourceExtractor(root)
        return GlobalYamlSourceExtractor(root)

    def extract_str(
        self, extractor_args: ExtractorArgs
    ) -> str | Output[str] | dict[str, Output[str]] | dict[Output[str], Any]:
        return self.extractor.extract_str(extractor_args)

    def extract_path(self, extractor_args: ExtractorArgs) -> AbsolutePath:
        return self.extractor.extract_path(extractor_args)

    def extract_volume_path(self, extractor_args: ExtractorArgs) -> ContainerVolumePath:
        return self.extractor.extract_volume_path(extractor_args)


class GlobalFullExtractor(ExtractorBase[GlobalExtractFull]):
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

    def extractor_args(self, extractor_args: ExtractorArgs) -> ExtractorArgs:
        service = self.root.service
        return extractor_args.with_service(
            (
                extractor_args.services.get(
                    service,
                    extractor_args.docker_resource_args.config.services[service],
                )
            )
            if service is not None
            else None
        )

    def extract_str(self, extractor_args: ExtractorArgs) -> Output[str]:
        extractor = self.extractor
        transformer = self.transformer
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
        transformer = self.transformer
        extractor_args = self.extractor_args(extractor_args)

        return transformer.transform_path(extractor.extract_path(extractor_args))

    def extract_volume_path(self, extractor_args: ExtractorArgs) -> ContainerVolumePath:
        extractor = self.extractor
        transformer = self.transformer
        extractor_args = self.extractor_args(extractor_args)

        return transformer.transform_volume_path(
            extractor.extract_volume_path(extractor_args)
        )


class GlobalExtractor(ExtractorBase[GlobalExtract]):
    @classmethod
    def get_extractor(
        cls, source: GlobalExtract
    ) -> GlobalSourceExtractor | GlobalFullExtractor:
        root = source.root
        if isinstance(root, GlobalExtractSource):
            return GlobalSourceExtractor(root)
        if isinstance(root, GlobalExtractFull):
            return GlobalFullExtractor(root)
        return cls.get_extractor(
            GlobalExtract(GlobalExtractFull(extract=ServiceExtract(root)))
        )

    @property
    def extractor(
        self,
    ) -> (
        GlobalSourceExtractor
        | GlobalFullExtractor
        | ServiceSourceExtractor
        | ContainerExtractor
    ):
        return self.get_extractor(self.root)

    def extract_str(self, extractor_args: ExtractorArgs) -> Output[str]:
        root = self.root.root

        if isinstance(root, GlobalExtractFull):
            return GlobalFullExtractor(root).extract_str(extractor_args)
        return ExtractTransformer(ExtractTransform()).transform_string(
            self.extractor.extract_str(extractor_args)
        )

    def extract_str_explicit_transform(
        self, extractor_args: ExtractorArgs
    ) -> str | Output[str] | dict[str, Output[str]] | dict[Output[str], Any]:
        root = self.root.root

        if isinstance(root, GlobalExtractFull):
            return GlobalFullExtractor(root).extract_str(extractor_args)
        return self.extractor.extract_str(extractor_args)

    def extract_path(self, extractor_args: ExtractorArgs) -> AbsolutePath:
        return self.extractor.extract_path(extractor_args)

    def extract_volume_path(self, extractor_args: ExtractorArgs) -> ContainerVolumePath:
        return self.extractor.extract_volume_path(extractor_args)

    @classmethod
    def extract_recursively(cls, data: Any, extractor_args: ExtractorArgs) -> Any:
        if isinstance(data, dict):
            try:
                extract = GlobalExtract(**data)
                return cls(extract).extract_str_explicit_transform(extractor_args)
            except ValidationError:
                return {
                    key: cls.extract_recursively(value, extractor_args)
                    for key, value in data.items()
                }
        elif isinstance(data, list):
            return [cls.extract_recursively(value, extractor_args) for value in data]
        else:
            return data
