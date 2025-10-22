import dataclasses

import pulumi_random as random
import pulumi_tls as tls


@dataclasses.dataclass
class SecretResource:
    secrets: dict[str, random.RandomUuid | random.RandomPassword | tls.PrivateKey]

    def get_secret(self, key: str) -> random.RandomUuid | random.RandomPassword:
        secret = self.secrets[key]
        if isinstance(secret, (random.RandomUuid, random.RandomPassword)):
            return secret
        raise TypeError("Secret {} is not a valid uuid or password".format(key))

    def get_key(self, key: str) -> tls.PrivateKey:
        secret = self.secrets[key]
        if isinstance(secret, tls.PrivateKey):
            return secret
        raise TypeError("Secret {} is not a valid private key".format(key))
