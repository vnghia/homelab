from __future__ import annotations

import typing

from homelab_extract.service.mtls import ServiceExtractMTlsSource
from pulumi import Output

from .. import ExtractorBase

if typing.TYPE_CHECKING:
    from .. import ExtractorArgs


class ServiceMTlsSourceExtractor(ExtractorBase[ServiceExtractMTlsSource]):
    def extract_str(
        self, extractor_args: ExtractorArgs
    ) -> Output[str] | dict[str, Output[str]]:
        root = self.root
        mtls = extractor_args.service.secret.get_mtls(root.mtls)
        if root.info:
            return mtls.get_info(root.info)
        return mtls.to_dict()
