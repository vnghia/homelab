from __future__ import annotations

import typing

from homelab_extract.config import GlobalExtractConfigFormat, GlobalExtractConfigSource
from pulumi import Output

from . import ExtractorBase

if typing.TYPE_CHECKING:
    from . import ExtractorArgs


class GlobalConfigSourceExtractor(ExtractorBase[GlobalExtractConfigSource]):
    def extract_str(self, extractor_args: ExtractorArgs) -> Output[str]:
        from ..resource.file.config import JsonDefaultModel, YamlDumper
        from .global_ import GlobalExtractor

        json_data = Output.json_dumps(
            GlobalExtractor.extract_recursively(self.root.data, extractor_args)
        )

        match self.root.format:
            case GlobalExtractConfigFormat.JSON:
                return json_data
            case GlobalExtractConfigFormat.YAML:
                return json_data.apply(JsonDefaultModel.model_validate_json).apply(
                    YamlDumper.dumps
                )
