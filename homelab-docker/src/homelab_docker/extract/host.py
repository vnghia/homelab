from __future__ import annotations

import typing

from homelab_extract.host import GlobalExtractHostSource, HostInfoSource

from . import ExtractorBase

if typing.TYPE_CHECKING:
    from . import ExtractorArgs


class GlobalHostSourceExtractor(ExtractorBase[GlobalExtractHostSource]):
    def extract_str(self, extractor_args: ExtractorArgs) -> str:
        root = self.root
        host = extractor_args.docker_resource_args.config.host
        match root.host:
            case HostInfoSource.USER:
                return host.user
            case HostInfoSource.ADDRESS:
                return host.address
