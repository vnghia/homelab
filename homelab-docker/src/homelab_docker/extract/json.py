from __future__ import annotations

import typing

from homelab_extract.json import GlobalExtractJsonSource
from pulumi import Output

from . import ExtractorBase

if typing.TYPE_CHECKING:
    from . import ExtractorArgs


class GlobalJsonSourceExtractor(ExtractorBase[GlobalExtractJsonSource]):
    def extract_str(self, extractor_args: ExtractorArgs) -> Output[str]:
        from .global_ import GlobalExtractor

        return Output.json_dumps(
            GlobalExtractor.extract_recursively(self.root.json_, extractor_args)
        )
