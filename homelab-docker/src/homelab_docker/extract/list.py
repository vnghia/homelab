from __future__ import annotations

import typing

from homelab_extract.list_ import GlobalExtractListSource
from pulumi import Output

from . import ExtractorBase

if typing.TYPE_CHECKING:
    from . import ExtractorArgs


class GlobalListSourceExtractor(ExtractorBase[GlobalExtractListSource]):
    def extract_str(self, extractor_args: ExtractorArgs) -> list[Output[str]]:
        from .global_ import GlobalExtractor

        return [
            GlobalExtractor(item).extract_str(extractor_args)
            for item in self.root.list_
        ]
