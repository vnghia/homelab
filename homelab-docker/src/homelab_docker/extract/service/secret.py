from __future__ import annotations

import typing

import pulumi_random as random
import pulumi_tls as tls
from homelab_extract.service.secret import ServiceExtractSecretSource
from pulumi import Output

from .. import ExtractorBase

if typing.TYPE_CHECKING:
    from .. import ExtractorArgs


class ServiceSecretSourceExtractor(ExtractorBase[ServiceExtractSecretSource]):
    def extract_str(
        self, extractor_args: ExtractorArgs
    ) -> Output[str] | random.RandomPassword | dict[str, Output[str]]:
        root = self.root
        secret = extractor_args.service.secret.get(root.secret)
        if isinstance(secret, tls.PrivateKey):
            return {
                "private_key_pem": secret.private_key_pem,
                "public_key_pem": secret.public_key_pem,
                "private_key_openssh": secret.private_key_openssh,
                "public_key_openssh": secret.public_key_openssh,
            }
        if isinstance(secret, random.RandomUuid):
            return secret.result
        return secret
