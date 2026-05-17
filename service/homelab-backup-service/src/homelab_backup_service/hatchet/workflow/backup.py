from typing import Any, ClassVar, Literal, Self

from hatchet_sdk import Context, DurableContext, Hatchet, ParentCondition
from hatchet_sdk.runnables.workflow import BaseWorkflow, Workflow
from homelab_balite_service.hatchet.workflow import balite
from homelab_barman_service.hatchet.workflow import barman
from homelab_hatchet_tool import constant
from homelab_hatchet_tool.config import Config, ConfigDependency
from homelab_hatchet_tool.docker import Docker
from homelab_pydantic import DatabaseType, HomelabBaseModel
from homelab_restic_service.hatchet.workflow import restic


class HatchetBackupServiceModel(HomelabBaseModel):
    profiles: list[str]
    databases: dict[DatabaseType, dict[str, str]]

    def get_database_profiles(self, type: DatabaseType) -> list[str]:
        return list(self.databases[type].keys())

    def get_database_file_profiles(self, type: DatabaseType) -> list[str]:
        return list(self.databases[type].values())


class HatchetBackupConfig(HomelabBaseModel):
    BACKUP: ClassVar[str] = "backup"
    CONFIG_KEY: ClassVar[str | None] = None

    services: dict[str, HatchetBackupServiceModel]

    @classmethod
    async def load(cls, config: Config) -> Self:
        return await config.load_service(cls.BACKUP, cls.CONFIG_KEY, cls)


class HatchetBackupModel(HomelabBaseModel):
    service: str
    backup: HatchetBackupConfig | None = None


class HatchetBackupServicesModel(HomelabBaseModel):
    services: Literal["all"] | list[str]


class Backup:
    SERVICE = HatchetBackupConfig.BACKUP
    BACKUP_SERVICES = "{}-services".format(SERVICE)

    RESTIC_DEFAULT_BACKUP: ClassVar[restic.HatchetResticBackupModel] = (
        restic.HatchetResticBackupModel()
    )
    BARMAN_DEFAULT_BACKUP: ClassVar[barman.HatchetBarmanBackupModel] = (
        barman.HatchetBarmanBackupModel()
    )
    BALITE_DEFAULT_BACKUP: ClassVar[balite.HatchetBaliteBackupModel] = (
        balite.HatchetBaliteBackupModel()
    )

    _backup_workflow: Workflow[HatchetBackupModel] | None

    @classmethod
    def backup_workflow(cls) -> Workflow[HatchetBackupModel]:
        if not cls._backup_workflow:
            raise RuntimeError(
                "Please call `build_workflows` at least once before accesing this function"
            )
        return cls._backup_workflow

    @classmethod
    async def backup_services(
        cls, backup_config: HatchetBackupConfig, services: list[str]
    ) -> None:
        backup_workflow = cls.backup_workflow()
        await backup_workflow.aio_run_many(
            [
                backup_workflow.create_bulk_run_item(
                    HatchetBackupModel(service=service, backup=backup_config),
                    key=service,
                    additional_metadata=constant.build_labels(service),
                    desired_worker_labels=[
                        constant.DESIRED_HOST_LABEL,
                        constant.DESIRED_DOCKER_LABEL,
                    ],
                )
                for service in services
            ]
        )

    @classmethod
    def build_workflows(cls, hatchet: Hatchet) -> list[BaseWorkflow[Any]]:
        backup_workflow = hatchet.workflow(
            name=cls.SERVICE,
            input_validator=HatchetBackupModel,
            default_additional_metadata=constant.build_labels(cls.SERVICE),
        )

        @backup_workflow.task(
            name="load-config", desired_worker_labels=[constant.DESIRED_HOST_LABEL]
        )
        async def backup_load_config(
            input: HatchetBackupModel,
            context: Context,
            config: ConfigDependency,
        ) -> HatchetBackupServiceModel:
            return (input.backup or (await HatchetBackupConfig.load(config))).services[
                input.service
            ]

        @backup_workflow.task(
            name="load-restic-config",
            parents=[backup_load_config],
            skip_if=[
                ParentCondition(
                    parent=backup_load_config,
                    expression="output.profiles.size() == 0 && output.databases.size() == 0",
                )
            ],
            desired_worker_labels=[constant.DESIRED_HOST_LABEL],
        )
        async def backup_load_restic_config(
            input: HatchetBackupModel, context: Context, config: ConfigDependency
        ) -> restic.HatchetResticModelConfig:
            return await restic.HatchetResticModelConfig.load(config)

        @backup_workflow.durable_task(
            name="backup-file",
            execution_timeout=Docker.DOCKER_TIMEOUT,
            parents=[backup_load_config, backup_load_restic_config],
            skip_if=[
                ParentCondition(
                    parent=backup_load_config,
                    expression="output.profiles.size() == 0",
                )
            ],
        )
        async def backup_file(
            input: HatchetBackupModel, context: DurableContext
        ) -> None:
            backup_config = context.task_output(backup_load_config)
            restic_config = context.task_output(backup_load_restic_config)
            await restic.Restic.backup_profiles(
                restic_config, backup_config.profiles, cls.RESTIC_DEFAULT_BACKUP
            )

        @backup_workflow.task(
            name="load-{}-config".format(DatabaseType.POSTGRES),
            parents=[backup_load_config],
            skip_if=[
                ParentCondition(
                    parent=backup_load_config,
                    expression='!("{}" in output.databases)'.format(
                        DatabaseType.POSTGRES
                    ),
                )
            ],
            desired_worker_labels=[constant.DESIRED_HOST_LABEL],
        )
        async def backup_load_postgres_config(
            input: HatchetBackupModel, context: Context, config: ConfigDependency
        ) -> barman.HatchetBarmanContainerConfig:
            return await barman.HatchetBarmanContainerConfig.load(config)

        @backup_workflow.durable_task(
            name="backup-{}-database".format(DatabaseType.POSTGRES),
            execution_timeout=Docker.DOCKER_TIMEOUT,
            parents=[backup_load_config, backup_load_postgres_config],
            skip_if=[
                ParentCondition(
                    parent=backup_load_config,
                    expression='!("{}" in output.databases)'.format(
                        DatabaseType.POSTGRES
                    ),
                )
            ],
        )
        async def backup_postgres_database(
            input: HatchetBackupModel, context: DurableContext
        ) -> None:
            backup_config = context.task_output(backup_load_config)
            barman_config = context.task_output(backup_load_postgres_config)
            return await barman.Barman.backup_profiles(
                barman_config,
                backup_config.get_database_profiles(DatabaseType.POSTGRES),
                cls.BARMAN_DEFAULT_BACKUP,
            )

        @backup_workflow.durable_task(
            name="backup-{}-database-file".format(DatabaseType.POSTGRES),
            execution_timeout=Docker.DOCKER_TIMEOUT,
            parents=[
                backup_load_config,
                backup_load_restic_config,
                backup_postgres_database,
            ],
            skip_if=[
                ParentCondition(
                    parent=backup_load_config,
                    expression='!("{}" in output.databases)'.format(
                        DatabaseType.POSTGRES
                    ),
                )
            ],
        )
        async def backup_postgres_database_file(
            input: HatchetBackupModel, context: DurableContext
        ) -> None:
            backup_config = context.task_output(backup_load_config)
            restic_config = context.task_output(backup_load_restic_config)
            await restic.Restic.backup_profiles(
                restic_config,
                backup_config.get_database_file_profiles(DatabaseType.POSTGRES),
                cls.RESTIC_DEFAULT_BACKUP,
            )

        @backup_workflow.task(
            name="load-{}-config".format(DatabaseType.SQLITE),
            parents=[backup_load_config],
            skip_if=[
                ParentCondition(
                    parent=backup_load_config,
                    expression='!("{}" in output.databases)'.format(
                        DatabaseType.SQLITE
                    ),
                )
            ],
            desired_worker_labels=[constant.DESIRED_HOST_LABEL],
        )
        async def backup_load_sqlite_config(
            input: HatchetBackupModel, context: Context, config: ConfigDependency
        ) -> balite.HatchetBaliteModelConfig:
            return await balite.HatchetBaliteModelConfig.load(config)

        @backup_workflow.durable_task(
            name="backup-{}-database".format(DatabaseType.SQLITE),
            execution_timeout=Docker.DOCKER_TIMEOUT,
            parents=[backup_load_config, backup_load_sqlite_config],
            skip_if=[
                ParentCondition(
                    parent=backup_load_config,
                    expression='!("{}" in output.databases)'.format(
                        DatabaseType.SQLITE
                    ),
                )
            ],
        )
        async def backup_sqlite_database(
            input: HatchetBackupModel, context: DurableContext
        ) -> None:
            backup_config = context.task_output(backup_load_config)
            balite_config = context.task_output(backup_load_sqlite_config)
            return await balite.Balite.backup_profiles(
                balite_config,
                backup_config.get_database_profiles(DatabaseType.SQLITE),
                cls.BALITE_DEFAULT_BACKUP,
            )

        @backup_workflow.durable_task(
            name="backup-{}-database-file".format(DatabaseType.SQLITE),
            execution_timeout=Docker.DOCKER_TIMEOUT,
            parents=[
                backup_load_config,
                backup_load_restic_config,
                backup_sqlite_database,
            ],
            skip_if=[
                ParentCondition(
                    parent=backup_load_config,
                    expression='!("{}" in output.databases)'.format(
                        DatabaseType.SQLITE
                    ),
                )
            ],
        )
        async def backup_sqlite_database_file(
            input: HatchetBackupModel, context: DurableContext
        ) -> None:
            backup_config = context.task_output(backup_load_config)
            restic_config = context.task_output(backup_load_restic_config)
            await restic.Restic.backup_profiles(
                restic_config,
                backup_config.get_database_file_profiles(DatabaseType.SQLITE),
                cls.RESTIC_DEFAULT_BACKUP,
            )

        @hatchet.durable_task(
            name=cls.BACKUP_SERVICES,
            input_validator=HatchetBackupServicesModel,
            execution_timeout=Docker.DOCKER_TIMEOUT,
            desired_worker_labels=[constant.DESIRED_HOST_LABEL],
            default_additional_metadata=constant.build_labels(cls.SERVICE),
        )
        async def backup_services(
            input: HatchetBackupServicesModel,
            context: DurableContext,
            config: ConfigDependency,
        ) -> None:
            backup_config = await HatchetBackupConfig.load(config)
            await cls.backup_services(
                backup_config,
                (
                    list(backup_config.services.keys())
                    if input.services == "all"
                    else input.services
                ),
            )

        cls._backup_workflow = backup_workflow

        return [cls._backup_workflow, backup_services]


build_workflows = Backup.build_workflows
