from pydantic import BaseModel, ConfigDict

from homelab_docker.pydantic.path import AbsolutePath


class Volume(BaseModel):
    model_config = ConfigDict(strict=True)

    path: AbsolutePath
    read_only: bool = False
