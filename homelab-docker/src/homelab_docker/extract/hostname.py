from __future__ import annotations

import typing

from homelab_extract.hostname import GlobalExtractHostnameSource

from . import ExtractorBase

if typing.TYPE_CHECKING:
    from . import ExtractorArgs


class GlobalHostnameSourceExtractor(ExtractorBase[GlobalExtractHostnameSource]):
    def extract_str(self, extractor_args: ExtractorArgs) -> str:
        return self.root.to_hostname(
            extractor_args.hostnames, extractor_args.host.name()
        )
