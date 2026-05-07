from pathlib import Path
from typing import ClassVar, Self

from hatchet_sdk import DesiredWorkerLabel, WorkerLabelComparator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="HATCHET_WORKER_")

    instance: ClassVar[Self | None] = None

    CONFIG_PATH_PREFIX: ClassVar[Path] = Path("/etc/hatchet/worker")
    DOCKER_RUN_PREFIX: ClassVar[str] = "run"

    HOST_LABEL: ClassVar[str] = "host"

    worker_host_label: ClassVar[DesiredWorkerLabel | None] = None

    log_level: str = "INFO"

    host: str
    name: str | None = None
    workflow_dir: Path = CONFIG_PATH_PREFIX / "workflow"
    docker_dir: Path = CONFIG_PATH_PREFIX / "docker"

    @classmethod
    def load(cls) -> Self:
        if not cls.instance:
            cls.instance = cls()  # type: ignore
        return cls.instance

    @classmethod
    def get_worker_host_label(cls) -> DesiredWorkerLabel:
        if not cls.worker_host_label:
            cls.worker_host_label = DesiredWorkerLabel(
                key=cls.HOST_LABEL,
                value=cls.load().host,
                comparator=WorkerLabelComparator.EQUAL,
                required=True,
            )
        return cls.worker_host_label
