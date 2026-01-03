from enum import StrEnum, auto

from homelab_pydantic import HomelabBaseModel


class ExtractTransformSecretEncode(StrEnum):
    HEX = auto()
    BASE32 = auto()
    BASE64 = auto()
    BCRYPT = auto()


class ExtractTransformSecret(HomelabBaseModel):
    encode: ExtractTransformSecretEncode
