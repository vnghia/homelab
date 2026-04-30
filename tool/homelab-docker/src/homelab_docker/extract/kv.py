from __future__ import annotations

import typing

from homelab_extract.kv import GlobalExtractKvSource
from pulumi import Output

from . import ExtractorBase

if typing.TYPE_CHECKING:
    from . import ExtractorArgs


class GlobalKvSourceExtractor(ExtractorBase[GlobalExtractKvSource]):
    def extract_str(self, extractor_args: ExtractorArgs) -> dict[str, Output[str]]:
        from .global_ import GlobalExtractor

        root = self.root
        return {
            key: GlobalExtractor(value).extract_str(extractor_args)
            for key, value in root.kv.items()
        }
