from __future__ import annotations

import typing

from homelab_extract.id import GlobalExtractIdSource
from pulumi import Output

from . import ExtractorBase

if typing.TYPE_CHECKING:
    from . import ExtractorArgs


class GlobalIdSourceExtractor(ExtractorBase[GlobalExtractIdSource]):
    def extract_str(self, extractor_args: ExtractorArgs) -> Output[str]:
        return extractor_args.service.containers[self.root.id].id
