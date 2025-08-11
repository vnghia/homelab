from homelab_pydantic import HomelabBaseModel

from ...model.docker.image import RemoteImageModel
from ...model.docker.image.build import BuildImageModel


class ImageConfig(HomelabBaseModel):
    remote: dict[str, RemoteImageModel] = {}
    build: dict[str, BuildImageModel] = {}
