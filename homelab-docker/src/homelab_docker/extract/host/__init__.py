from __future__ import annotations

import typing

import pulumi_random as random
from homelab_extract.host import HostExtract, HostExtractFull, HostExtractSource
from homelab_extract.host.info import HostExtractInfoSource
from homelab_extract.host.network import HostExtractNetworkSource
from homelab_pydantic import AbsolutePath
from pulumi import Output
from pydantic import IPvAnyNetwork, ValidationError

from .. import ExtractorBase
from ..service import ServiceExtractor
from ..transform import ExtractTransformer
from .info import HostInfoSourceExtractor
from .network import HostNetworkSourceExtractor
from .variable import HostVariableSourceExtractor

if typing.TYPE_CHECKING:
    from ...model.docker.container.volume_path import ContainerVolumePath
    from .. import ExtractorArgs


class HostSourceExtractor(ExtractorBase[HostExtractSource]):
    @property
    def extractor(
        self,
    ) -> (
        HostInfoSourceExtractor
        | HostNetworkSourceExtractor
        | HostVariableSourceExtractor
    ):
        root = self.root.root
        if isinstance(root, HostExtractInfoSource):
            return HostInfoSourceExtractor(root)
        if isinstance(root, HostExtractNetworkSource):
            return HostNetworkSourceExtractor(root)
        return HostVariableSourceExtractor(root)

    def extract_str(
        self, extractor_args: ExtractorArgs
    ) -> str | Output[str] | dict[str, Output[str]] | list[Output[IPvAnyNetwork]]:
        return self.extractor.extract_str(extractor_args)

    def extract_path(self, extractor_args: ExtractorArgs) -> AbsolutePath:
        return self.extractor.extract_path(extractor_args)

    def extract_volume_path(self, extractor_args: ExtractorArgs) -> ContainerVolumePath:
        return self.extractor.extract_volume_path(extractor_args)


class HostFullExtractor(ExtractorBase[HostExtractFull]):
    @property
    def extractor(self) -> ServiceExtractor | HostSourceExtractor:
        extract = self.root.extract
        return (
            HostSourceExtractor(extract)
            if isinstance(extract, HostExtractSource)
            else ServiceExtractor(extract)
        )

    @property
    def transfomer(self) -> ExtractTransformer | None:
        transform = self.root.transform
        return ExtractTransformer(transform) if transform else None

    def extractor_args(self, extractor_args: ExtractorArgs) -> ExtractorArgs:
        return extractor_args.with_service(
            extractor_args.get_service(self.root.service)
        )

    def extract_str(
        self, extractor_args: ExtractorArgs
    ) -> (
        str
        | Output[str]
        | random.RandomPassword
        | dict[str, Output[str]]
        | list[Output[IPvAnyNetwork]]
    ):
        extractor = self.extractor
        transformer = self.transfomer
        extractor_args = self.extractor_args(extractor_args)

        try:
            value_path = extractor.extract_path(extractor_args)
            result_path: str | Output[str] | None = None
            if transformer:
                value_path = transformer.transform_path(value_path)
                result_path = transformer.transform_string(value_path.as_posix())
            else:
                result_path = value_path.as_posix()
            return result_path
        except (TypeError, ValidationError):
            result_str = extractor.extract_str(extractor_args)
            if transformer:
                result_str = transformer.transform_string(result_str)
            return result_str

    def extract_path(self, extractor_args: ExtractorArgs) -> AbsolutePath:
        extractor = self.extractor
        transformer = self.transfomer
        extractor_args = self.extractor_args(extractor_args)

        value = extractor.extract_path(extractor_args)
        if transformer:
            value = transformer.transform_path(value)
        return value

    def extract_volume_path(self, extractor_args: ExtractorArgs) -> ContainerVolumePath:
        extractor = self.extractor
        transformer = self.transfomer
        extractor_args = self.extractor_args(extractor_args)

        value = extractor.extract_volume_path(extractor_args)
        if transformer:
            value = transformer.transform_volume_path(value)
        return value


class HostExtractor(ExtractorBase[HostExtract]):
    @classmethod
    def get_extractor(
        cls, source: HostExtract
    ) -> HostSourceExtractor | HostFullExtractor:
        root = source.root
        if isinstance(root, HostExtractSource):
            return HostSourceExtractor(root)
        if isinstance(root, HostExtractFull):
            return HostFullExtractor(root)
        return cls.get_extractor(HostExtract(HostExtractFull(extract=root)))

    @property
    def extractor(
        self,
    ) -> HostSourceExtractor | HostFullExtractor:
        return self.get_extractor(self.root)

    def extract_str(
        self, extractor_args: ExtractorArgs
    ) -> (
        str
        | Output[str]
        | random.RandomPassword
        | dict[str, Output[str]]
        | list[Output[IPvAnyNetwork]]
    ):
        return self.extractor.extract_str(extractor_args)

    def extract_path(self, extractor_args: ExtractorArgs) -> AbsolutePath:
        return self.extractor.extract_path(extractor_args)

    def extract_volume_path(self, extractor_args: ExtractorArgs) -> ContainerVolumePath:
        return self.extractor.extract_volume_path(extractor_args)
