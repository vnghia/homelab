import asyncio
import logging
from typing import Any, ClassVar, Self

from hatchet_sdk import (
    ConcurrencyExpression,
    ConcurrencyLimitStrategy,
    Context,
    EmptyModel,
    Hatchet,
)
from hatchet_sdk.runnables.workflow import BaseWorkflow
from homelab_hatchet_tool.config import Config, ConfigDependency
from homelab_hatchet_tool.docker import Docker
from homelab_hatchet_tool.docker.model.exec import DockerContainerExecModel
from homelab_hatchet_tool.docker.model.name import DockerContainerNameConfig
from homelab_hatchet_tool.worker import label
from homelab_pydantic import HomelabBaseModel, docker

logger = logging.getLogger("barman")


class HatchetBarmanConfig(HomelabBaseModel):
    BARMAN: ClassVar[str] = "barman"

    container: str | None
    profiles: dict[str, str]


class HatchetBarmanBackupModel(HomelabBaseModel):
    profile: str


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
                command=[self.BARMAN, "backup", "--wait", profile]
            ),
            name=self.name,
        )

    async def backup(self, context: Context, profile: str) -> None:
        container_name = self.profiles[profile]
        container = await Docker().client.containers.get(container_name)
        container_is_not_running = (
            container_state.status
            if (
                container_state
                := docker.schema.ModelContainerInspectResponse.model_validate(
                    container._container
                ).state
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
                await Docker.exec_container(context, self.build_cron_model())
            await Docker.exec_container(context, self.build_backup_model(profile))
        finally:
            if container_is_not_running:
                logger.info(
                    "Stopping container {} after barman backup".format(container_name)
                )
                await container.stop()


class Barman:
    SERVICE = HatchetBarmanContainerConfig.BARMAN

    @classmethod
    def build_workflows(cls, hatchet: Hatchet) -> list[BaseWorkflow[Any]]:
        @hatchet.task(
            name="{}-cron".format(cls.SERVICE),
            on_crons=["* * * * *"],
            concurrency=[
                ConcurrencyExpression(
                    expression='"{}-cron"'.format(cls.SERVICE),
                    max_runs=1,
                    limit_strategy=ConcurrencyLimitStrategy.GROUP_ROUND_ROBIN,
                )
            ],
            desired_worker_labels=[
                label.DESIRED_HOST_LABEL,
                label.DESIRED_DOCKER_LABEL,
            ],
            default_additional_metadata={label.HOST_LABEL: label.HOST_VALUE},
        )
        async def barman_cron(
            input: EmptyModel, context: Context, config: ConfigDependency
        ) -> None:
            barman_config = await HatchetBarmanContainerConfig.load(config)
            await Docker.exec_container(context, barman_config.build_cron_model())

        barman_backup_workflow = hatchet.workflow(
            name="{}-backup".format(cls.SERVICE),
            input_validator=HatchetBarmanBackupModel,
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
            await barman_config.backup(context, input.profile)

        return [barman_cron, barman_backup_workflow]


build_workflows = Barman.build_workflows
