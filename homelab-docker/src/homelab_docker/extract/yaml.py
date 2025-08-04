from __future__ import annotations

import typing

from homelab_extract.yaml import GlobalExtractYamlSource
from pulumi import Output

from . import ExtractorBase

if typing.TYPE_CHECKING:
    from . import ExtractorArgs


class GlobalYamlSourceExtractor(ExtractorBase[GlobalExtractYamlSource]):
    def extract_str(self, extractor_args: ExtractorArgs) -> Output[str]:
        from ..resource.file.config import JsonDefaultModel, YamlDumper
        from .global_ import GlobalExtractor

        root = self.root
        return (
            Output.json_dumps(
                GlobalExtractor.extract_recursively(root.yaml, extractor_args)
            )
            .apply(JsonDefaultModel.model_validate_json)
            .apply(YamlDumper.dumps)
        )
