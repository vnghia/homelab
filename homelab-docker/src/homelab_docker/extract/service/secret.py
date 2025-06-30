from __future__ import annotations

import typing

import pulumi_tls as tls
from homelab_extract.service.secret import ServiceExtractSecretSource
from pulumi import Output

from .. import ExtractorBase

if typing.TYPE_CHECKING:
    from ...model.container import ContainerModel
    from ...resource.service import ServiceResourceBase


class ServiceSecretSourceExtractor(ExtractorBase[ServiceExtractSecretSource]):
    def extract_str(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> Output[str] | dict[str, Output[str]]:
        root = self.root
        secret = main_service.secret.get(root.secret)
        if isinstance(secret, tls.PrivateKey):
            return {
                "private_key_pem": secret.private_key_pem,
                "public_key_pem": secret.public_key_pem,
                "private_key_openssh": secret.private_key_openssh,
                "public_key_openssh": secret.public_key_openssh,
            }
        return secret.result
