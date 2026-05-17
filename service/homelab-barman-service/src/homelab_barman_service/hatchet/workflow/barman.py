import asyncio
import datetime
import logging
from typing import Any, ClassVar, Iterable, Self

from hatchet_sdk import Context, EmptyModel, Hatchet
from hatchet_sdk.runnables.workflow import BaseWorkflow, Standalone
from homelab_hatchet_tool import constant
from homelab_hatchet_tool.config import Config, ConfigDependency
from homelab_hatchet_tool.docker import Docker
from homelab_hatchet_tool.docker.model.exec import DockerContainerExecModel
from homelab_hatchet_tool.docker.model.name import DockerContainerNameConfig
from homelab_pydantic import HomelabBaseModel, docker

logger = logging.getLogger("barman")


class HatchetBarmanConfig(HomelabBaseModel):
    BARMAN: ClassVar[str] = "barman"
    BARMAN_CMD: ClassVar[str] = BARMAN

    container: str | None
    profiles: dict[str, str]


class HatchetBarmanBackupModel(HomelabBaseModel):
    def build_backup_cmd(self, profile: str) -> list[str]:
        return [HatchetBarmanConfig.BARMAN_CMD, "backup", "--wait", profile]


class HatchetBarmanContainerConfig(HomelabBaseModel):
    BARMAN: ClassVar[str] = "barman"
    CONFIG_KEY: ClassVar[None] = None

    name: str
    profiles: dict[str, str]

    @classmethod
    async def load(cls, config: Config) -> Self:
        raw_config = await config.load_service(
            cls.BARMAN, cls.CONFIG_KEY, HatchetBarmanConfig
        )
        return cls(
            name=(await DockerContainerNameConfig(service=cls.BARMAN).load(config))[
                raw_config.container
            ],
            profiles=raw_config.profiles,
        )

    def resolve_profiles(self, keys: Iterable[str]) -> set[str]:
        if constant.INPUT_ALL in keys:
            return set(self.profiles.keys())
        return set(keys)

    def build_cron_model(self) -> DockerContainerExecModel:
        return DockerContainerExecModel(
            exec=docker.ContainerExecModel(
                command=[HatchetBarmanConfig.BARMAN_CMD, "cron", "--keep-descriptors"]
            ),
            name=self.name,
        )

    def build_backup_model(
        self, profile: str, model: HatchetBarmanBackupModel
    ) -> DockerContainerExecModel:
        return DockerContainerExecModel(
            exec=docker.ContainerExecModel(command=model.build_backup_cmd(profile)),
            name=self.name,
        )


class HatchetBarmanBaseInputModel(HomelabBaseModel):
    profiles: str | set[str]
    barman: HatchetBarmanContainerConfig | None = None

    def iterable(self) -> set[str]:
        return {self.profiles} if isinstance(self.profiles, str) else self.profiles


class HatchetBarmanBackupInputModel(HatchetBarmanBaseInputModel):
    backup: HatchetBarmanBackupModel = HatchetBarmanBackupModel()


class Barman:
    SERVICE = HatchetBarmanContainerConfig.BARMAN

    SCHEDULE_TIMEOUT = datetime.timedelta(hours=6)
    CONCURRENCY = 5

    _barman_backup_workflow: Standalone[HatchetBarmanBackupInputModel, None] | None = (
        None
    )

    @classmethod
    def barman_backup_workflow(
        cls,
    ) -> Standalone[HatchetBarmanBackupInputModel, None]:
        if not cls._barman_backup_workflow:
            raise RuntimeError(
                "Please call `build_workflows` at least once before accesing this function"
            )
        return cls._barman_backup_workflow

    @classmethod
    async def backup_profile(
        cls,
        context: Context,
        barman_config: HatchetBarmanContainerConfig,
        profile: str,
        backup: HatchetBarmanBackupModel,
    ) -> None:
        container_name = barman_config.profiles[profile]
        container = await Docker.client().containers.get(container_name)
        container_is_not_running = (
            container_state.status
            if (
                container_state := docker.schema.ContainerState.model_validate(
                    container._container["State"]
                )
            )
            else None
        ) != docker.schema.ContainerStateStatus.RUNNING

        try:
            if container_is_not_running:
                logger.info(
                    "Starting container {} for barman backup".format(container_name)
                )
                await container.start()
                await asyncio.sleep(30)
                await Docker.exec_container(context, barman_config.build_cron_model())
            await Docker.exec_container(
                context,
                barman_config.build_backup_model(profile, backup),
            )
        finally:
            if container_is_not_running:
                logger.info(
                    "Stopping container {} after barman backup".format(container_name)
                )
                await container.stop()

    @classmethod
    async def backup_profiles(
        cls,
        barman_config: HatchetBarmanContainerConfig,
        profiles: Iterable[str],
        backup: HatchetBarmanBackupModel,
    ) -> None:
        barman_backup_workflow = cls.barman_backup_workflow()
        await barman_backup_workflow.aio_run_many(
            [
                barman_backup_workflow.create_bulk_run_item(
                    HatchetBarmanBackupInputModel(
                        profiles=profile, backup=backup, barman=barman_config
                    ),
                    key=profile,
                    additional_metadata=constant.build_labels(cls.SERVICE)
                    | {"{}-profile".format(cls.SERVICE): profile},
                    desired_worker_labels=[
                        constant.DESIRED_HOST_LABEL,
                        constant.DESIRED_DOCKER_LABEL,
                    ],
                )
                for profile in profiles
            ]
        )

    @classmethod
    def build_workflows(cls, hatchet: Hatchet) -> list[BaseWorkflow[Any]]:
        @hatchet.task(
            name="{}-cron".format(cls.SERVICE),
            on_crons=["* * * * *"],
            concurrency=1,
            desired_worker_labels=[
                constant.DESIRED_HOST_LABEL,
                constant.DESIRED_DOCKER_LABEL,
            ],
            default_additional_metadata=constant.build_labels(cls.SERVICE),
        )
        async def barman_cron(
            input: EmptyModel, context: Context, config: ConfigDependency
        ) -> None:
            barman_config = await HatchetBarmanContainerConfig.load(config)
            await Docker.exec_container(context, barman_config.build_cron_model())

        @hatchet.task(
            name="{}-backup".format(cls.SERVICE),
            input_validator=HatchetBarmanBackupInputModel,
            schedule_timeout=cls.SCHEDULE_TIMEOUT,
            execution_timeout=Docker.DOCKER_TIMEOUT,
            concurrency=cls.CONCURRENCY,
            desired_worker_labels=[
                constant.DESIRED_HOST_LABEL,
                constant.DESIRED_DOCKER_LABEL,
            ],
            default_additional_metadata=constant.build_labels(cls.SERVICE),
        )
        async def barman_backup(
            input: HatchetBarmanBackupInputModel,
            context: Context,
            config: ConfigDependency,
        ) -> None:
            barman_config = input.barman or (
                await HatchetBarmanContainerConfig.load(config)
            )
            if isinstance(input.profiles, str) and input.barman:
                return await cls.backup_profile(
                    context, barman_config, input.profiles, input.backup
                )
            return await cls.backup_profiles(
                barman_config,
                barman_config.resolve_profiles(input.iterable()),
                input.backup,
            )

        cls._barman_backup_workflow = barman_backup

        return [barman_cron, cls._barman_backup_workflow]


build_workflows = Barman.build_workflows
