from __future__ import annotations

import typing
from typing import Any

from homelab_extract.host.variable import HostExtractVariableSource
from homelab_pydantic import AbsolutePath
from pulumi import Output

from .. import ExtractorBase

if typing.TYPE_CHECKING:
    from ...model.docker.container.volume_path import ContainerVolumePath
    from .. import ExtractorArgs
    from ..global_ import GlobalExtractor


class HostVariableSourceExtractor(ExtractorBase[HostExtractVariableSource]):
    def get_variable(self, extractor_args: ExtractorArgs) -> GlobalExtractor:
        from ..global_ import GlobalExtractor

        return GlobalExtractor(extractor_args.host_model.variables[self.root.hvariable])

    def extract_str(
        self, extractor_args: ExtractorArgs
    ) -> (
        str
        | Output[str]
        | dict[str, Output[str]]
        | dict[Output[str], Any]
        | list[Output[str]]
    ):
        return self.get_variable(extractor_args).extract_str_explicit_transform(
            extractor_args
        )

    def extract_path(self, extractor_args: ExtractorArgs) -> AbsolutePath:
        return self.get_variable(extractor_args).extract_path(extractor_args)

    def extract_volume_path(self, extractor_args: ExtractorArgs) -> ContainerVolumePath:
        return self.get_variable(extractor_args).extract_volume_path(extractor_args)
