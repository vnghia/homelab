from __future__ import annotations

import typing

from homelab_extract.service.keepass import (
    KeepassInfoSource,
    ServiceExtractKeepassSource,
)
from pulumi import Output

from .. import ExtractorBase

if typing.TYPE_CHECKING:
    from .. import ExtractorArgs


class ServiceKeepassSourceExtractor(ExtractorBase[ServiceExtractKeepassSource]):
    def extract_str(self, extractor_args: ExtractorArgs) -> Output[str]:
        root = self.root
        entry = extractor_args.service.keepass[root.keepass]
        match root.info:
            case KeepassInfoSource.USERNAME:
                return entry.username
            case KeepassInfoSource.PASSWORD:
                return entry.password
