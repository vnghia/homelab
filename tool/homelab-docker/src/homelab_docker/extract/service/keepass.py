from __future__ import annotations

import typing

import pulumi_random as random
from homelab_extract.service.keepass import (
    KeepassInfoSource,
    ServiceExtractKeepassSource,
)
from pulumi import Output

from .. import ExtractorBase

if typing.TYPE_CHECKING:
    from .. import ExtractorArgs


class ServiceKeepassSourceExtractor(ExtractorBase[ServiceExtractKeepassSource]):
    def extract_str(
        self, extractor_args: ExtractorArgs
    ) -> Output[str] | random.RandomPassword:
        root = self.root
        entry = extractor_args.service.keepass[root.keepass]
        match root.info:
            case KeepassInfoSource.USERNAME:
                return entry.username
            case KeepassInfoSource.PASSWORD:
                return entry.password
