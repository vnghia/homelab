import binascii
from enum import StrEnum, auto

import pulumi_random as random
from homelab_pydantic import HomelabBaseModel
from pulumi import Output


class ExtractTransformSecretEncode(StrEnum):
    RAW = auto()
    HEX = auto()


class ExtractTransformSecret(HomelabBaseModel):
    encode: ExtractTransformSecretEncode = ExtractTransformSecretEncode.RAW

    def transform(self, value: random.RandomPassword) -> Output[str]:
        match self.encode:
            case ExtractTransformSecretEncode.RAW:
                return value.result
            case ExtractTransformSecretEncode.HEX:
                return value.result.apply(
                    lambda x: binascii.hexlify(x.encode()).decode("ascii")
                )
