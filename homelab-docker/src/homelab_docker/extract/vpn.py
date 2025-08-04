from __future__ import annotations

import typing

from homelab_extract.vpn import GlobalExtractVpnSource
from pulumi import Output

from . import ExtractorBase

if typing.TYPE_CHECKING:
    from . import ExtractorArgs


class GlobalVpnSourceExtractor(ExtractorBase[GlobalExtractVpnSource]):
    def extract_str(self, extractor_args: ExtractorArgs) -> Output[str]:
        return Output.from_input(
            str(extractor_args.docker_resource_args.config.vpn_.ports[self.root.port])
        )
