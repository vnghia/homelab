import socket
from pathlib import Path
from typing import Annotated, ClassVar, Self

import aiofiles
from hatchet_sdk import Context, Depends, EmptyModel
from homelab_pydantic import HomelabBaseModel
from pydantic import PositiveInt, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="HATCHET_WORKER_")

    instance: ClassVar[Self | None] = None

    CONFIG_PATH_PREFIX: ClassVar[Path] = Path("/etc/hatchet/worker")

    DOCKER_EXEC_PREFIX: ClassVar[str] = "exec"

    DOCKER_MODEL_PREFIX: ClassVar[str] = "model"
    DOCKER_NAME_PREFIX: ClassVar[str] = "name"

    log_level: str = "INFO"

    host: str = socket.gethostname()
    hosts: Annotated[list[str], NoDecode] = []

    name: str | None = None
    slots: PositiveInt = 100
    durable_slots: PositiveInt = 1000

    workflow_dir: Path = CONFIG_PATH_PREFIX / "workflow"
    docker_dir: Path = CONFIG_PATH_PREFIX / "docker"
    schedule_dir: Path = CONFIG_PATH_PREFIX / "schedule"
    config_dir: Path = CONFIG_PATH_PREFIX / "config"

    scheduler_dir: Path = CONFIG_PATH_PREFIX / "scheduler"
    scheduler_cron: Annotated[list[str], NoDecode] = ["*/30 * * * *"]

    @field_validator("hosts", mode="before")
    @classmethod
    def decode_hosts(cls, value: str | list[str]) -> list[str]:
        return (
            [host.strip() for host in value.split(",")]
            if isinstance(value, str)
            else value
        )

    @field_validator("scheduler_cron", mode="before")
    @classmethod
    def decode_scheduler_cron(cls, value: str) -> list[str]:
        return (
            [cron.strip() for cron in value.split(",")]
            if isinstance(value, str)
            else value
        )

    @classmethod
    def load(cls) -> Self:
        if not cls.instance:
            cls.instance = cls()
        return cls.instance

    @classmethod
    def dependency(cls, input: EmptyModel, ctx: Context) -> Self:
        return cls.load()

    async def load_service[T: HomelabBaseModel](
        self, service: str, key: str | None, type: type[T]
    ) -> T:
        async with aiofiles.open(
            (self.config_dir / service / (key or service)).with_suffix(".json")
        ) as file:
            return type.model_validate_json(await file.read())


type ConfigDependency = Annotated[Config, Depends(Config.dependency)]
