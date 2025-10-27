from __future__ import annotations

import typing

from homelab_extract.service.vpn import ServiceExtractVpnSource
from pulumi import Output

from .. import ExtractorBase

if typing.TYPE_CHECKING:
    from .. import ExtractorArgs


class ServiceVpnSourceExtractor(ExtractorBase[ServiceExtractVpnSource]):
    def extract_str(self, extractor_args: ExtractorArgs) -> Output[str]:
        return Output.from_input(
            str(extractor_args.service_model.vpn_.root.root.ports[self.root.port])
        )
