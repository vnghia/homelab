from __future__ import annotations

import typing
from typing import Any

from homelab_extract.dict_ import GlobalExtractDictSource
from pulumi import Output

from . import ExtractorBase

if typing.TYPE_CHECKING:
    from . import ExtractorArgs


class GlobalDictSourceExtractor(ExtractorBase[GlobalExtractDictSource]):
    def extract_str(self, extractor_args: ExtractorArgs) -> dict[Output[str], Any]:
        from .global_ import GlobalExtractor

        root = self.root
        return {
            GlobalExtractor(key).extract_str(
                extractor_args
            ): GlobalExtractor.extract_recursively(value, extractor_args)
            for [key, value] in root.dict_
        }
