from __future__ import annotations

import typing

from homelab_extract.service.variable import ServiceExtractVariableSource
from homelab_pydantic import AbsolutePath
from pulumi import Output

from .. import ExtractorBase

if typing.TYPE_CHECKING:
    from ...model.container.volume_path import ContainerVolumePath
    from .. import ExtractorArgs
    from ..global_ import GlobalExtractor


class ServiceVariableSourceExtractor(ExtractorBase[ServiceExtractVariableSource]):
    def get_variable(self, extractor_args: ExtractorArgs) -> GlobalExtractor:
        from ..global_ import GlobalExtractor

        return GlobalExtractor(
            extractor_args.service_model.variables[self.root.variable]
        )

    def extract_str(self, extractor_args: ExtractorArgs) -> str | Output[str]:
        return self.get_variable(extractor_args).extract_str(extractor_args)

    def extract_path(self, extractor_args: ExtractorArgs) -> AbsolutePath:
        return self.get_variable(extractor_args).extract_path(extractor_args)

    def extract_volume_path(self, extractor_args: ExtractorArgs) -> ContainerVolumePath:
        return self.get_variable(extractor_args).extract_volume_path(extractor_args)
