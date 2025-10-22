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
    ) -> Output[str] | random.RandomPassword | dict[str, Output[str]]:
        root = self.root
        secret = extractor_args.service.secret.get(root.secret)

        if isinstance(secret, random.RandomUuid):
            return secret.result
        if isinstance(secret, random.RandomPassword):
            return secret
        raise TypeError("Secret {} is not a valid uuid or password".format(root.secret))
