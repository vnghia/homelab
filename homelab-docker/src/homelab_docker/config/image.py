from homelab_pydantic import HomelabBaseModel

from ..model.image import RemoteImageModel
from ..model.image.build import BuildImageModel


class ImageConfig(HomelabBaseModel):
    remote: dict[str, RemoteImageModel]
    build: dict[str, BuildImageModel]
