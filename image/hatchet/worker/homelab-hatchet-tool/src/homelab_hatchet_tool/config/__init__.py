from pathlib import Path
from typing import ClassVar, Self

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="HATCHET_WORKER_")

    instance: ClassVar[Self | None] = None

    CONFIG_PATH_PREFIX: ClassVar[Path] = Path("/etc/hatchet/worker")
    DOCKER_RUN_PREFIX: ClassVar[str] = "run"

    debug: bool = False
    workflow_dir: Path = CONFIG_PATH_PREFIX / "workflow"
    docker_dir: Path = CONFIG_PATH_PREFIX / "docker"

    @classmethod
    def load(cls) -> Self:
        if not cls.instance:
            cls.instance = cls()
        return cls.instance
