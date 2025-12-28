from __future__ import annotations

import typing
from pathlib import PosixPath
from typing import Any

import pulumi_random as random
from homelab_extract import GlobalExtract, GlobalExtractFull, GlobalExtractSource
from homelab_extract.config import GlobalExtractConfigSource
from homelab_extract.dict_ import GlobalExtractDictSource
from homelab_extract.kv import GlobalExtractKvSource
from homelab_extract.plain import GlobalPlainExtractSource
from homelab_extract.project import GlobalExtractProjectSource
from homelab_extract.secret import GlobalExtractSecretSource
from homelab_extract.transform import ExtractTransform
from homelab_pydantic import AbsolutePath, RelativePath
from pulumi import Output
from pydantic import ValidationError

from . import ExtractorBase
from .config import GlobalConfigSourceExtractor
from .dict_ import GlobalDictSourceExtractor
from .host import HostExtractor
from .kv import GlobalKvSourceExtractor
from .plain import GlobalPlainSourceExtractor
from .project import GlobalProjectSourceExtractor
from .secret import GlobalSecretSourceExtractor
from .transform import ExtractTransformer
from .variable import GlobalVariableSourceExtractor

if typing.TYPE_CHECKING:
    from ..model.docker.container.volume_path import ContainerVolumePath
    from . import ExtractorArgs


class GlobalSourceExtractor(ExtractorBase[GlobalExtractSource]):
    @property
    def extractor(
        self,
    ) -> (
        GlobalConfigSourceExtractor
        | GlobalDictSourceExtractor
        | GlobalKvSourceExtractor
        | GlobalPlainSourceExtractor
        | GlobalProjectSourceExtractor
        | GlobalSecretSourceExtractor
        | GlobalVariableSourceExtractor
    ):
        root = self.root.root
        if isinstance(root, GlobalExtractConfigSource):
            return GlobalConfigSourceExtractor(root)
        if isinstance(root, GlobalExtractDictSource):
            return GlobalDictSourceExtractor(root)
        if isinstance(root, GlobalExtractKvSource):
            return GlobalKvSourceExtractor(root)
        if isinstance(root, GlobalPlainExtractSource):
            return GlobalPlainSourceExtractor(root)
        if isinstance(root, GlobalExtractProjectSource):
            return GlobalProjectSourceExtractor(root)
        if isinstance(root, GlobalExtractSecretSource):
            return GlobalSecretSourceExtractor(root)
        return GlobalVariableSourceExtractor(root)

    def extract_str(
        self, extractor_args: ExtractorArgs
    ) -> (
        str
        | Output[str]
        | random.RandomPassword
        | dict[str, Output[str]]
        | dict[Output[str], Any]
    ):
        return self.extractor.extract_str(extractor_args)

    def extract_path(self, extractor_args: ExtractorArgs) -> AbsolutePath:
        return self.extractor.extract_path(extractor_args)

    def extract_volume_path(self, extractor_args: ExtractorArgs) -> ContainerVolumePath:
        return self.extractor.extract_volume_path(extractor_args)


class GlobalFullExtractor(ExtractorBase[GlobalExtractFull]):
    @property
    def extractor(self) -> HostExtractor | GlobalSourceExtractor:
        extract = self.root.extract
        return (
            GlobalSourceExtractor(extract)
            if isinstance(extract, GlobalExtractSource)
            else HostExtractor(extract)
        )

    @property
    def transformer(self) -> ExtractTransformer:
        transform = self.root.transform
        return ExtractTransformer(transform or ExtractTransform())

    def extractor_args(self, extractor_args: ExtractorArgs) -> ExtractorArgs:
        return extractor_args.with_host(extractor_args.get_host(self.root.host))

    def extract_str(
        self, extractor_args: ExtractorArgs
    ) -> (
        str
        | Output[str]
        | random.RandomPassword
        | dict[str, Output[str]]
        | list[Output[str]]
        | dict[Output[str], Any]
    ):
        extractor = self.extractor
        extractor_args = self.extractor_args(extractor_args)

        if self.root.transform:
            transformer = self.transformer
            try:
                value_path = transformer.transform_path(
                    extractor.extract_path(extractor_args)
                ).as_posix()
                return transformer.transform_string(value_path)
            except (TypeError, ValidationError):
                value_str = extractor.extract_str(extractor_args)
                return transformer.transform_string(value_str)
        return extractor.extract_str(extractor_args)

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
            GlobalExtract(GlobalExtractFull(extract=root, transform=None))
        )

    @property
    def extractor(
        self,
    ) -> GlobalSourceExtractor | GlobalFullExtractor:
        return self.get_extractor(self.root)

    def extract_str(self, extractor_args: ExtractorArgs) -> Output[str]:
        return ExtractTransformer(ExtractTransform()).transform_string(
            self.extractor.extract_str(extractor_args)
        )

    def extract_str_explicit_transform(
        self, extractor_args: ExtractorArgs
    ) -> (
        str
        | Output[str]
        | dict[str, Output[str]]
        | dict[Output[str], Any]
        | list[Output[str]]
    ):
        value = self.extractor.extract_str(extractor_args)
        if isinstance(value, random.RandomPassword):
            return ExtractTransformer(ExtractTransform()).transform_string(value)
        return value

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

    @classmethod
    def extract_relative_path(
        cls,
        path: str | GlobalExtract,
        service: str,
        extractor_args: ExtractorArgs,
        current_volume: str | None,
    ) -> RelativePath:
        if isinstance(path, str):
            return RelativePath(PosixPath(path))

        volume_path = cls(path.with_service(service, False)).extract_volume_path(
            extractor_args
        )
        if volume_path.volume != current_volume:
            raise ValueError(
                "Volume ({}) must be the same as current volume ({})".format(
                    volume_path.volume, current_volume
                )
            )
        return volume_path.path
