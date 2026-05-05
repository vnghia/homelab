from pathlib import Path
from typing import ClassVar, Self

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="HATCHET_WORKER_")

    CONFIG_PATH_PREFIX: ClassVar[Path] = Path("/etc/hatchet/worker")

    debug: bool = False
    workflow_dir: Path = CONFIG_PATH_PREFIX / "workflow"

    @classmethod
    def load(cls) -> Self:
        return cls()
