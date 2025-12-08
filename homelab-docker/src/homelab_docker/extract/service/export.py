from __future__ import annotations

import typing

from homelab_extract.service.export import ServiceExtractExportSource
from pulumi import Output

from .. import ExtractorBase

if typing.TYPE_CHECKING:
    from .. import ExtractorArgs


class ServiceExportSourceExtractor(ExtractorBase[ServiceExtractExportSource]):
    def extract_str(
        self, extractor_args: ExtractorArgs
    ) -> Output[str] | list[Output[str]]:
        root = self.root
        return extractor_args.service.exports[root.export]
