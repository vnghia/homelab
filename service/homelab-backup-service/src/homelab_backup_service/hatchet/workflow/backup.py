from typing import Any, ClassVar, Literal, Self

from hatchet_sdk import Context, Hatchet, ParentCondition
from hatchet_sdk.runnables.workflow import BaseWorkflow
from homelab_balite_service.hatchet.workflow import balite
from homelab_barman_service.hatchet.workflow import barman
from homelab_hatchet_tool import label
from homelab_hatchet_tool.config import Config, ConfigDependency
from homelab_hatchet_tool.docker import Docker
from homelab_pydantic import DatabaseType, HomelabBaseModel
from homelab_restic_service.hatchet.workflow import restic


class HatchetBackupModel(HomelabBaseModel):
    profiles: list[str]
    databases: dict[DatabaseType, dict[str, str]]

    def get_database_profiles(self, type: DatabaseType) -> list[str]:
        return list(self.databases[type].keys())

    def get_database_file_profiles(self, type: DatabaseType) -> list[str]:
        return list(self.databases[type].values())


class HatchetBackupConfig(HomelabBaseModel):
    BACKUP: ClassVar[str] = "backup"
    CONFIG_KEY: ClassVar[str | None] = None

    services: dict[str, HatchetBackupModel]

    @classmethod
    async def load(cls, config: Config) -> Self:
        return await config.load_service(cls.BACKUP, cls.CONFIG_KEY, cls)


class HatchetBackupServiceModel(HomelabBaseModel):
    service: str
    backup: HatchetBackupConfig | None = None


class HatchetBackupServicesModel(HomelabBaseModel):
    services: Literal["all"] | list[str]


class Backup:
    SERVICE = HatchetBackupConfig.BACKUP
    BACKUP_SERVICES = "{}-services".format(SERVICE)

    @classmethod
    def build_workflows(cls, hatchet: Hatchet) -> list[BaseWorkflow[Any]]:
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
            return (input.backup or (await HatchetBackupConfig.load(config))).services[
                input.service
            ]

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
            await restic.Restic.backup_profiles(restic_config, backup_config.profiles)

        @backup_service_workflow.task(
            name="load-{}-config".format(DatabaseType.POSTGRES),
            desired_worker_labels=[label.DESIRED_HOST_LABEL],
        )
        async def backup_service_load_postgres_config(
            input: HatchetBackupServiceModel, context: Context, config: ConfigDependency
        ) -> barman.HatchetBarmanContainerConfig:
            return await barman.HatchetBarmanContainerConfig.load(config)

        @backup_service_workflow.task(
            name="backup-service-{}-database".format(DatabaseType.POSTGRES),
            execution_timeout=Docker.DOCKER_TIMEOUT,
            parents=[backup_service_load_config, backup_service_load_postgres_config],
            desired_worker_labels=[
                label.DESIRED_HOST_LABEL,
                label.DESIRED_DOCKER_LABEL,
            ],
            skip_if=[
                ParentCondition(
                    parent=backup_service_load_config,
                    expression='!("{}" in output.databases)'.format(
                        DatabaseType.POSTGRES
                    ),
                )
            ],
        )
        async def backup_service_postgres_database(
            input: HatchetBackupServiceModel, context: Context
        ) -> None:
            backup_config = context.task_output(backup_service_load_config)
            barman_config = context.task_output(backup_service_load_postgres_config)
            return await barman.Barman.backup_profiles(
                barman_config,
                backup_config.get_database_profiles(DatabaseType.POSTGRES),
            )

        # TODO: Use durable_task after worker affinity is stable
        @backup_service_workflow.task(
            name="backup-service-{}-database-file".format(DatabaseType.POSTGRES),
            execution_timeout=Docker.DOCKER_TIMEOUT,
            parents=[
                backup_service_load_config,
                backup_service_load_restic_config,
                backup_service_postgres_database,
            ],
            skip_if=[
                ParentCondition(
                    parent=backup_service_load_config,
                    expression='!("{}" in output.databases)'.format(
                        DatabaseType.POSTGRES
                    ),
                )
            ],
        )
        async def backup_service_postgres_database_file(
            input: HatchetBackupServiceModel, context: Context
        ) -> None:
            backup_config = context.task_output(backup_service_load_config)
            restic_config = context.task_output(backup_service_load_restic_config)
            await restic.Restic.backup_profiles(
                restic_config,
                backup_config.get_database_file_profiles(DatabaseType.POSTGRES),
            )

        @backup_service_workflow.task(
            name="load-{}-config".format(DatabaseType.SQLITE),
            desired_worker_labels=[label.DESIRED_HOST_LABEL],
        )
        async def backup_service_load_sqlite_config(
            input: HatchetBackupServiceModel, context: Context, config: ConfigDependency
        ) -> balite.HatchetBaliteModelConfig:
            return await balite.HatchetBaliteModelConfig.load(config)

        @backup_service_workflow.task(
            name="backup-service-{}-database".format(DatabaseType.SQLITE),
            execution_timeout=Docker.DOCKER_TIMEOUT,
            parents=[backup_service_load_config, backup_service_load_sqlite_config],
            desired_worker_labels=[
                label.DESIRED_HOST_LABEL,
                label.DESIRED_DOCKER_LABEL,
            ],
            skip_if=[
                ParentCondition(
                    parent=backup_service_load_config,
                    expression='!("{}" in output.databases)'.format(
                        DatabaseType.SQLITE
                    ),
                )
            ],
        )
        async def backup_service_sqlite_database(
            input: HatchetBackupServiceModel, context: Context
        ) -> None:
            backup_config = context.task_output(backup_service_load_config)
            balite_config = context.task_output(backup_service_load_sqlite_config)
            return await balite.Balite.backup_profiles(
                balite_config, backup_config.get_database_profiles(DatabaseType.SQLITE)
            )

        # TODO: Use durable_task after worker affinity is stable
        @backup_service_workflow.task(
            name="backup-service-{}-database-file".format(DatabaseType.SQLITE),
            execution_timeout=Docker.DOCKER_TIMEOUT,
            parents=[
                backup_service_load_config,
                backup_service_load_restic_config,
                backup_service_sqlite_database,
            ],
            skip_if=[
                ParentCondition(
                    parent=backup_service_load_config,
                    expression='!("{}" in output.databases)'.format(
                        DatabaseType.SQLITE
                    ),
                )
            ],
        )
        async def backup_service_sqlite_database_file(
            input: HatchetBackupServiceModel, context: Context
        ) -> None:
            backup_config = context.task_output(backup_service_load_config)
            restic_config = context.task_output(backup_service_load_restic_config)
            await restic.Restic.backup_profiles(
                restic_config,
                backup_config.get_database_file_profiles(DatabaseType.SQLITE),
            )

        @hatchet.task(
            name=cls.BACKUP_SERVICES,
            input_validator=HatchetBackupServicesModel,
            execution_timeout=Docker.DOCKER_TIMEOUT,
            desired_worker_labels=[label.DESIRED_HOST_LABEL],
            default_additional_metadata=label.build_labels(cls.SERVICE),
        )
        async def backup_services(
            input: HatchetBackupServicesModel,
            context: Context,
            config: ConfigDependency,
        ) -> None:
            backup_config = await HatchetBackupConfig.load(config)
            await backup_service_workflow.aio_run_many(
                [
                    backup_service_workflow.create_bulk_run_item(
                        HatchetBackupServiceModel(
                            service=service, backup=backup_config
                        ),
                        key=service,
                        additional_metadata=label.build_labels(cls.SERVICE),
                        desired_worker_labels=[label.DESIRED_HOST_LABEL],
                    )
                    for service in (
                        list(backup_config.services.keys())
                        if input.services == "all"
                        else input.services
                    )
                ]
            )

        return [backup_service_workflow, backup_services]


build_workflows = Backup.build_workflows
