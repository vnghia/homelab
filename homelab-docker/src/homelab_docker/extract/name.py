from __future__ import annotations

import typing

from homelab_extract.name import GlobalExtractNameSource
from pulumi import Output

from . import ExtractorBase

if typing.TYPE_CHECKING:
    from . import ExtractorArgs


class GlobalNameSourceExtractor(ExtractorBase[GlobalExtractNameSource]):
    def extract_str(self, extractor_args: ExtractorArgs) -> Output[str]:
        return extractor_args.service.containers[self.root.name].name
