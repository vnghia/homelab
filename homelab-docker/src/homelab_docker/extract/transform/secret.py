import base64
import binascii

from homelab_extract.transform.secret import (
    ExtractTransformSecret,
    ExtractTransformSecretEncode,
)
from homelab_pydantic import HomelabRootModel
from pulumi import Input, Output


class ExtractSecretTransformer(HomelabRootModel[ExtractTransformSecret]):
    def transform(self, value: Input[str]) -> Output[str]:
        root = self.root
        match root.encode:
            case ExtractTransformSecretEncode.HEX:
                return Output.from_input(value).apply(
                    lambda x: binascii.hexlify(x.encode()).decode("ascii")
                )
            case ExtractTransformSecretEncode.BASE32:
                return Output.from_input(value).apply(
                    lambda x: base64.b32encode(x.encode()).decode()
                )
