from enum import StrEnum, auto

from homelab_pydantic import HomelabBaseModel


class ExtractTransformSecretEncode(StrEnum):
    HEX = auto()


class ExtractTransformSecret(HomelabBaseModel):
    encode: ExtractTransformSecretEncode
