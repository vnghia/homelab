import binascii

import pulumi_random as random
from homelab_extract.transform.secret import (
    ExtractTransformSecret,
    ExtractTransformSecretEncode,
)
from homelab_pydantic import HomelabRootModel
from pulumi import Output


class ExtractSecretTransformer(HomelabRootModel[ExtractTransformSecret]):
    def transform(self, value: random.RandomPassword) -> Output[str]:
        root = self.root
        match root.encode:
            case ExtractTransformSecretEncode.RAW:
                return value.result
            case ExtractTransformSecretEncode.HEX:
                return value.result.apply(
                    lambda x: binascii.hexlify(x.encode()).decode("ascii")
                )
