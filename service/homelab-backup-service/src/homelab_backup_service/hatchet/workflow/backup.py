from typing import Any, ClassVar, Self

from hatchet_sdk import Context, Hatchet
from hatchet_sdk.runnables.workflow import BaseWorkflow
from homelab_hatchet_tool import label
from homelab_hatchet_tool.config import Config, ConfigDependency
from homelab_hatchet_tool.docker import Docker
from homelab_pydantic import DatabaseType, HomelabBaseModel
from homelab_restic_service.hatchet.workflow import restic


class HatchetBackupModel(HomelabBaseModel):
    profiles: list[str]
    databases: dict[DatabaseType, list[str]]


class HatchetBackupConfig(HomelabBaseModel):
    BACKUP: ClassVar[str] = "backup"

    services: dict[str, HatchetBackupModel]

    @classmethod
    async def load(cls, config: Config) -> Self:
        return await config.load_service(cls.BACKUP, cls)


class HatchetBackupServiceModel(HomelabBaseModel):
    service: str


class Backup:
    SERVICE = HatchetBackupConfig.BACKUP

    @classmethod
    def build_workflows(cls, hatchet: Hatchet) -> list[BaseWorkflow[Any]]:
        docker_run_model_workflow = Docker.docker_run_model_workflow()

        backup_service_workflow = hatchet.workflow(
            name="{}-service".format(cls.SERVICE),
            input_validator=HatchetBackupServiceModel,
            default_additional_metadata=label.build_labels(cls.SERVICE),
        )

        @backup_service_workflow.task(
            name="load-config", desired_worker_labels=[label.DESIRED_HOST_LABEL]
        )
        async def backup_service_load_config(
            input: HatchetBackupServiceModel,
            context: Context,
            config: ConfigDependency,
        ) -> HatchetBackupModel:
            return (await HatchetBackupConfig.load(config)).services[input.service]

        @backup_service_workflow.task(
            name="load-restic-config",
            desired_worker_labels=[label.DESIRED_HOST_LABEL],
        )
        async def backup_service_load_restic_config(
            input: HatchetBackupServiceModel,
            context: Context,
            config: ConfigDependency,
        ) -> restic.HatchetResticModelConfig:
            return await restic.HatchetResticModelConfig.load(config)

        # TODO: Use durable_task after worker affinity is stable
        @backup_service_workflow.task(
            name="backup-service-file",
            execution_timeout=Docker.DOCKER_TIMEOUT,
            parents=[backup_service_load_config, backup_service_load_restic_config],
        )
        async def backup_service_file(
            input: HatchetBackupServiceModel, context: Context
        ) -> None:
            backup_config = context.task_output(backup_service_load_config)
            restic_config = context.task_output(backup_service_load_restic_config)

            await docker_run_model_workflow.aio_run_many(
                [
                    docker_run_model_workflow.create_bulk_run_item(
                        restic_config.build_backup_model(profile),
                        key=profile,
                        desired_worker_labels=[
                            label.DESIRED_HOST_LABEL,
                            label.DESIRED_DOCKER_LABEL,
                        ],
                    )
                    for profile in backup_config.profiles
                ]
            )

        return [backup_service_workflow]


build_workflows = Backup.build_workflows
