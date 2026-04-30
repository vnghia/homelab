import pulumi_random as random
import pulumi_tls as tls
from homelab_extract.plain import PlainArgs
from pulumi import ComponentResource, ResourceOptions

from ..config import SecretConfig
from ..model.base import SecretOutput
from .cert.mtls import SecretMTlsResource


class SecretResource(ComponentResource):
    RESOURCE_NAME = "secret"

    def __init__(
        self,
        config: SecretConfig,
        *,
        opts: ResourceOptions,
        name: str,
        plain_args: PlainArgs,
    ) -> None:
        super().__init__(self.RESOURCE_NAME, name, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.secrets: dict[
            str,
            SecretOutput
            | random.RandomPassword
            | tls.PrivateKey
            | tls.LocallySignedCert
            | tls.SelfSignedCert
            | SecretMTlsResource,
        ] = {}

        for secret_name, secret_model in config.root.items():
            model = secret_model.root
            if model.active:
                self.secrets[secret_name] = model.build_resource(
                    secret_name,
                    opts=self.child_opts,
                    resource=self,
                    plain_args=plain_args,
                )

        self.register_outputs({})

    def get_secret(self, key: str) -> SecretOutput | random.RandomPassword:
        secret = self.secrets[key]
        if isinstance(secret, (SecretOutput, random.RandomPassword)):
            return secret
        raise TypeError(
            "Secret {} is not a valid secret output or password".format(key)
        )

    def get_key(
        self, key: str | None, default: tls.PrivateKey | None = None
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
        self, key: str | None, default: tls.SelfSignedCert | None = None
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
