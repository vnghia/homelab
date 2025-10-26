import dataclasses

import pulumi_random as random
import pulumi_tls as tls

from .cert.mtls import SecretMTlsResource


@dataclasses.dataclass
class SecretResource:
    secrets: dict[
        str,
        random.RandomUuid
        | random.RandomPassword
        | tls.PrivateKey
        | tls.LocallySignedCert
        | tls.SelfSignedCert
        | SecretMTlsResource,
    ]

    def get_secret(self, key: str) -> random.RandomUuid | random.RandomPassword:
        secret = self.secrets[key]
        if isinstance(secret, (random.RandomUuid, random.RandomPassword)):
            return secret
        raise TypeError("Secret {} is not a valid uuid or password".format(key))

    def get_key(
        self, key: str | None, default: tls.PrivateKey | None
    ) -> tls.PrivateKey:
        if key:
            secret = self.secrets[key]
            if isinstance(secret, tls.PrivateKey):
                return secret
            raise TypeError("Secret {} is not a valid private key".format(key))
        if default:
            return default
        raise ValueError("Either key or default must be provided")

    def get_cert(self, key: str) -> tls.LocallySignedCert | tls.SelfSignedCert:
        secret = self.secrets[key]
        if isinstance(secret, (tls.LocallySignedCert, tls.SelfSignedCert)):
            return secret
        raise TypeError("Secret {} is not a valid certificate".format(key))

    def get_self_signed_cert(
        self, key: str | None, default: tls.SelfSignedCert | None
    ) -> tls.SelfSignedCert:
        if key:
            secret = self.secrets[key]
            if isinstance(secret, tls.SelfSignedCert):
                return secret
            raise TypeError(
                "Secret {} is not a valid self-signed certificate".format(key)
            )
        if default:
            return default
        raise ValueError("Either key or default must be provided")

    def get_mtls(self, key: str) -> SecretMTlsResource:
        secret = self.secrets[key]
        if isinstance(secret, SecretMTlsResource):
            return secret
        raise TypeError("Secret {} is not a valid mTLS resource".format(key))
