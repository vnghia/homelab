from typing import Any, ClassVar, Self

from hatchet_sdk import Context, Hatchet
from hatchet_sdk.runnables.workflow import BaseWorkflow
from homelab_hatchet_tool.config import Config, ConfigDependency
from homelab_hatchet_tool.docker import Docker
from homelab_hatchet_tool.worker import label
from homelab_pydantic import DatabaseType, HomelabBaseModel


class HatchetBackupServiceModel(HomelabBaseModel):
    profiles: list[str]
    databases: dict[DatabaseType, list[str]]


class HatchetBackupConfig(HomelabBaseModel):
    BACKUP: ClassVar[str] = "backup"

    services: dict[str, HatchetBackupServiceModel]

    @classmethod
    async def load(cls, config: Config) -> Self:
        return await config.load_service(cls.BACKUP, cls)


class HatchetBackupServiceConfig(HomelabBaseModel):
    service: str


class Backup:
    SERVICE = HatchetBackupConfig.BACKUP

    @classmethod
    def build_workflows(cls, hatchet: Hatchet) -> list[BaseWorkflow[Any]]:
        docker_run_model_workflow = Docker.docker_run_model_workflow()

        backup_service_workflow = hatchet.workflow(
            name="{}-service".format(cls.SERVICE),
            input_validator=HatchetBackupServiceConfig,
        )

        @backup_service_workflow.task(
            name="load-config",
            desired_worker_labels=[label.DESIRED_HOST_LABEL],
        )
        async def backup_load_config(
            input: HatchetBackupServiceConfig,
            context: Context,
            config: ConfigDependency,
        ) -> HatchetBackupServiceModel:
            return (await HatchetBackupConfig.load(config)).services[input.service]

        return [backup_service_workflow]
