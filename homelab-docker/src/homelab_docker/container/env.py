from typing import Any, Self

from pydantic import BaseModel, ConfigDict, ModelWrapValidatorHandler, model_validator

from homelab_docker.container.volume import Volume
from homelab_docker.pydantic.path import RelativePath


class Full(BaseModel):
    model_config = ConfigDict(strict=True)

    volume: str
    path: RelativePath | None = None

    def to_str(self, volumes: dict[str, Volume]) -> str:
        path = volumes[self.volume].to_path()
        return (path / self.path if self.path else path).as_posix()


class Env(BaseModel):
    env: str | Full

    @model_validator(mode="wrap")
    @classmethod
    def wrap(cls, data: Any, handler: ModelWrapValidatorHandler[Self]) -> Self:
        return handler({"env": data})

    def to_str(self, volumes: dict[str, Volume]) -> str:
        env = self.env
        return env.to_str(volumes) if isinstance(env, Full) else env
