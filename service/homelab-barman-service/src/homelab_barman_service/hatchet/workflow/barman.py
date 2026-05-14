import asyncio
import logging
from typing import Any, ClassVar, Self

from hatchet_sdk import Context, EmptyModel, Hatchet
from hatchet_sdk.runnables.workflow import BaseWorkflow, Standalone
from homelab_hatchet_tool import label
from homelab_hatchet_tool.config import Config, ConfigDependency
from homelab_hatchet_tool.docker import Docker
from homelab_hatchet_tool.docker.model.exec import DockerContainerExecModel
from homelab_hatchet_tool.docker.model.name import DockerContainerNameConfig
from homelab_pydantic import HomelabBaseModel, docker

logger = logging.getLogger("barman")


class HatchetBarmanConfig(HomelabBaseModel):
    BARMAN: ClassVar[str] = "barman"

    container: str | None
    profiles: dict[str, str]


class HatchetBarmanBackupModel(HomelabBaseModel):
    profiles: list[str]

    @classmethod
    def build_cmd(cls, profile: str) -> list[str]:
        return ["backup", "--wait", profile]


class HatchetBarmanContainerConfig(HomelabBaseModel):
    BARMAN: ClassVar[str] = "barman"

    name: str
    profiles: dict[str, str]

    @classmethod
    async def load(cls, config: Config) -> Self:
        raw_config = await config.load_service(cls.BARMAN, HatchetBarmanConfig)
        return cls(
            name=(await DockerContainerNameConfig(service=cls.BARMAN).load(config))[
                raw_config.container
            ],
            profiles=raw_config.profiles,
        )

    def build_cron_model(self) -> DockerContainerExecModel:
        return DockerContainerExecModel(
            exec=docker.ContainerExecModel(
                command=[self.BARMAN, "cron", "--keep-descriptors"]
            ),
            name=self.name,
        )

    def build_backup_model(self, profile: str) -> DockerContainerExecModel:
        return DockerContainerExecModel(
            exec=docker.ContainerExecModel(
                command=[self.BARMAN, *HatchetBarmanBackupModel.build_cmd(profile)]
            ),
            name=self.name,
        )


class HatchetBarmanBackupProfileModel(HomelabBaseModel):
    config: HatchetBarmanContainerConfig
    profile: str


class Barman:
    SERVICE = HatchetBarmanContainerConfig.BARMAN

    _barman_backup_model_workflow: (
        Standalone[HatchetBarmanBackupProfileModel, None] | None
    ) = None

    @classmethod
    def barman_backup_model_workflow(
        cls,
    ) -> Standalone[HatchetBarmanBackupProfileModel, None]:
        if not cls._barman_backup_model_workflow:
            raise RuntimeError(
                "Please call `build_workflows` at least once before accesing this function"
            )
        return cls._barman_backup_model_workflow

    @classmethod
    async def backup_profile(
        cls, context: Context, model: HatchetBarmanBackupProfileModel
    ) -> None:
        container_name = model.config.profiles[model.profile]
        container = await Docker().client.containers.get(container_name)
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
                await Docker.exec_container(context, model.config.build_cron_model())
            await Docker.exec_container(
                context, model.config.build_backup_model(model.profile)
            )
        finally:
            if container_is_not_running:
                logger.info(
                    "Stopping container {} after barman backup".format(container_name)
                )
                await container.stop()

    @classmethod
    async def backup_profiles(
        cls, barman_config: HatchetBarmanContainerConfig, profiles: list[str]
    ) -> None:
        barman_backup_model_workflow = cls.barman_backup_model_workflow()
        await barman_backup_model_workflow.aio_run_many(
            [
                barman_backup_model_workflow.create_bulk_run_item(
                    HatchetBarmanBackupProfileModel(
                        config=barman_config, profile=profile
                    ),
                    key=profile,
                    additional_metadata=label.build_labels(cls.SERVICE),
                    desired_worker_labels=[
                        label.DESIRED_HOST_LABEL,
                        label.DESIRED_DOCKER_LABEL,
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
                label.DESIRED_HOST_LABEL,
                label.DESIRED_DOCKER_LABEL,
            ],
            default_additional_metadata=label.build_labels(cls.SERVICE),
        )
        async def barman_cron(
            input: EmptyModel, context: Context, config: ConfigDependency
        ) -> None:
            barman_config = await HatchetBarmanContainerConfig.load(config)
            await Docker.exec_container(context, barman_config.build_cron_model())

        @hatchet.task(
            name="{}-backup-model".format(cls.SERVICE),
            input_validator=HatchetBarmanBackupProfileModel,
            execution_timeout=Docker.DOCKER_TIMEOUT,
            desired_worker_labels=[
                label.DESIRED_HOST_LABEL,
                label.DESIRED_DOCKER_LABEL,
            ],
            default_additional_metadata=label.build_labels(cls.SERVICE),
        )
        async def barman_backup_model(
            input: HatchetBarmanBackupProfileModel, context: Context
        ) -> None:
            return await cls.backup_profile(context, input)

        barman_backup_workflow = hatchet.workflow(
            name="{}-backup".format(cls.SERVICE),
            input_validator=HatchetBarmanBackupModel,
            default_additional_metadata=label.build_labels(cls.SERVICE),
        )

        @barman_backup_workflow.task(
            name="load-config",
            desired_worker_labels=[label.DESIRED_HOST_LABEL],
        )
        async def barman_backup_load_config(
            input: HatchetBarmanBackupModel, context: Context, config: ConfigDependency
        ) -> HatchetBarmanContainerConfig:
            return await HatchetBarmanContainerConfig.load(config)

        @barman_backup_workflow.task(
            name="backup",
            execution_timeout=Docker.DOCKER_TIMEOUT,
            parents=[barman_backup_load_config],
            desired_worker_labels=[
                label.DESIRED_HOST_LABEL,
                label.DESIRED_DOCKER_LABEL,
            ],
        )
        async def barman_backup(
            input: HatchetBarmanBackupModel, context: Context
        ) -> None:
            barman_config = context.task_output(barman_backup_load_config)
            return await cls.backup_profiles(barman_config, input.profiles)

        cls._barman_backup_model_workflow = barman_backup_model

        return [barman_cron, barman_backup_model, barman_backup_workflow]


build_workflows = Barman.build_workflows
