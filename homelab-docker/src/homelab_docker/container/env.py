from pydantic import BaseModel, ConfigDict

from homelab_docker.container.volume import Volume
from homelab_docker.pydantic.path import RelativePath


class Env(BaseModel):
    model_config = ConfigDict(strict=True)

    volume: str
    path: RelativePath | None = None

    def to_str(self, volumes: dict[str, Volume]) -> str:
        path = volumes[self.volume].path
        return (path / self.path if self.path else path).as_posix()
