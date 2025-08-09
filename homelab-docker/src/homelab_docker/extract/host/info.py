from __future__ import annotations

import typing

from homelab_extract.host.info import HostExtractInfoSource, HostInfoSource

from .. import ExtractorBase

if typing.TYPE_CHECKING:
    from .. import ExtractorArgs


class HostInfoSourceExtractor(ExtractorBase[HostExtractInfoSource]):
    def extract_str(self, extractor_args: ExtractorArgs) -> str:
        hinfo = self.root.hinfo
        host = extractor_args.docker_resource_args.config.host
        match hinfo:
            case HostInfoSource.USER:
                return host.user
            case HostInfoSource.ADDRESS:
                return host.address
            case HostInfoSource.TIMEZONE:
                return host.timezone
