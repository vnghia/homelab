from __future__ import annotations

import typing

from homelab_extract.host.info import HostExtractInfoSource, HostInfoSource

from .. import ExtractorBase

if typing.TYPE_CHECKING:
    from .. import ExtractorArgs


class HostInfoSourceExtractor(ExtractorBase[HostExtractInfoSource]):
    def extract_str(self, extractor_args: ExtractorArgs) -> str:
        hinfo = self.root.hinfo
        host = extractor_args.host_model
        match hinfo:
            case HostInfoSource.USER:
                return host.access.user
            case HostInfoSource.ADDRESS:
                return host.access.address
            case HostInfoSource.TIMEZONE:
                return host.timezone
