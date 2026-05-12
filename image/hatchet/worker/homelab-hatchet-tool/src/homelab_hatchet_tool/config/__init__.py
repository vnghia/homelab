import socket
from pathlib import Path
from typing import ClassVar, Self

import aiofiles
from homelab_pydantic import HomelabBaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="HATCHET_WORKER_")

    instance: ClassVar[Self | None] = None

    CONFIG_PATH_PREFIX: ClassVar[Path] = Path("/etc/hatchet/worker")

    DOCKER_EXEC_PREFIX: ClassVar[str] = "exec"

    DOCKER_MODEL_PREFIX: ClassVar[str] = "model"
    DOCKER_NAME_PREFIX: ClassVar[str] = "name"

    log_level: str = "INFO"

    host: str = socket.gethostname()
    name: str | None = None
    workflow_dir: Path = CONFIG_PATH_PREFIX / "workflow"
    docker_dir: Path = CONFIG_PATH_PREFIX / "docker"
    schedule_dir: Path = CONFIG_PATH_PREFIX / "schedule"
    config_dir: Path = CONFIG_PATH_PREFIX / "config"

    @classmethod
    def load(cls) -> Self:
        if not cls.instance:
            cls.instance = cls()
        return cls.instance

    async def load_service[T: HomelabBaseModel](self, service: str, type: type[T]) -> T:
        async with aiofiles.open(
            (self.config_dir / service).with_suffix(".json")
        ) as file:
            return type.model_validate_json(await file.read())
