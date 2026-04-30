from __future__ import annotations

import typing

from homelab_extract.service.key import ServiceExtractKeySource
from pulumi import Output

from .. import ExtractorBase

if typing.TYPE_CHECKING:
    from .. import ExtractorArgs


class ServiceKeySourceExtractor(ExtractorBase[ServiceExtractKeySource]):
    def extract_str(
        self, extractor_args: ExtractorArgs
    ) -> Output[str] | dict[str, Output[str]]:
        root = self.root
        key = extractor_args.service.secret.get_key(root.key)

        data = {
            "private_pem": key.private_key_pem,
            "public_pem": key.public_key_pem,
            "private_openssh": key.private_key_openssh,
            "public_openssh": key.public_key_openssh,
        }
        return data[root.info] if root.info else data
