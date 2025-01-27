from pathlib import PosixPath

from pydantic import BaseModel, ConfigDict, field_validator

from homelab_docker.container.volume import Volume


class Env(BaseModel):
    model_config = ConfigDict(strict=True)

    volume: str
    path: PosixPath | None = None

    @field_validator("path", mode="after")
    @classmethod
    def check_relative_path(cls, path: PosixPath | None) -> PosixPath | None:
        if path and path.is_absolute():
            raise ValueError("path must be relative")
        return path

    def to_str(self, volumes: dict[str, Volume]) -> str:
        path = volumes[self.volume].path
        return (path / self.path if self.path else path).as_posix()
