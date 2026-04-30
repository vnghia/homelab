from homelab_pydantic import HomelabBaseModel

from .path import ExtractTransformPath
from .secret import ExtractTransformSecret
from .string import ExtractTransformString


class ExtractTransform(HomelabBaseModel):
    path: ExtractTransformPath = ExtractTransformPath()
    string: ExtractTransformString = ExtractTransformString()
    secret: ExtractTransformSecret | None = None
