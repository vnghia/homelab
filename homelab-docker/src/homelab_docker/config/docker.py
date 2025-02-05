from pydantic import BaseModel

from homelab_docker.config.image import Image


class Docker(BaseModel):
    images: Image
