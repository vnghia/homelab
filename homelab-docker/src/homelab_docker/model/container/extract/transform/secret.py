import binascii
from enum import StrEnum, auto

import pulumi_random as random
from homelab_pydantic import HomelabBaseModel
from pulumi import Output


class ContainerExtractTransformSecretEncode(StrEnum):
    RAW = auto()
    HEX = auto()


class ContainerExtractTransformSecret(HomelabBaseModel):
    encode: ContainerExtractTransformSecretEncode = (
        ContainerExtractTransformSecretEncode.RAW
    )

    def transform(self, value: random.RandomPassword) -> Output[str]:
        match self.encode:
            case ContainerExtractTransformSecretEncode.RAW:
                return value.result
            case ContainerExtractTransformSecretEncode.HEX:
                return value.result.apply(
                    lambda x: binascii.hexlify(x.encode()).decode("ascii")
                )
