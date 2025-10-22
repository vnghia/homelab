from __future__ import annotations

import typing

import pulumi_random as random
from homelab_extract.service.secret import ServiceExtractSecretSource
from pulumi import Output

from .. import ExtractorBase

if typing.TYPE_CHECKING:
    from .. import ExtractorArgs


class ServiceSecretSourceExtractor(ExtractorBase[ServiceExtractSecretSource]):
    def extract_str(
        self, extractor_args: ExtractorArgs
    ) -> Output[str] | random.RandomPassword:
        root = self.root
        secret = extractor_args.service.secret.get_secret(root.secret)

        if isinstance(secret, random.RandomUuid):
            return secret.result
        return secret
