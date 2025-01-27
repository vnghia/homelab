from pathlib import PosixPath

from pydantic import BaseModel, ConfigDict, PositiveInt

from homelab_docker.pydantic.path import AbsolutePath


class Tmpfs(BaseModel):
    model_config = ConfigDict(strict=True)

    path: AbsolutePath = PosixPath("/tmp")
    size: PositiveInt | None = None
