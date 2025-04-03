from enum import StrEnum, auto

from homelab_pydantic import HomelabBaseModel


class ExtractTransformSecretEncode(StrEnum):
    RAW = auto()
    HEX = auto()


class ExtractTransformSecret(HomelabBaseModel):
    encode: ExtractTransformSecretEncode = ExtractTransformSecretEncode.RAW
