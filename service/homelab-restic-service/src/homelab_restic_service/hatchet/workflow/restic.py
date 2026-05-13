import copy
import logging
from typing import Any, ClassVar, Self

from hatchet_sdk import Context, Hatchet
from hatchet_sdk.runnables.workflow import BaseWorkflow
from homelab_hatchet_tool.config import Config, ConfigDependency
from homelab_hatchet_tool.docker import Docker
from homelab_hatchet_tool.docker.model.run import (
    DockerContainerRunConfig,
    DockerContainerRunModel,
)
from homelab_hatchet_tool.worker import label
from homelab_pydantic import AbsolutePath, HomelabBaseModel, add_namespace, docker

logger = logging.getLogger("restic")


class HatchetResticProfileModel(HomelabBaseModel):
    volume: str
    path: AbsolutePath

    def to_mount(self, read_only: bool) -> docker.schema.ModelMount:
        return docker.schema.ModelMount.model_construct(
            type="volume",
            target=self.path.as_posix(),
            source=self.volume,
            read_only=read_only,
            volume_options=docker.schema.ModelMountVolumeOptions.model_construct(
                no_copy=True
            ),
        )


class HatchetResticModel(HomelabBaseModel):
    groups: dict[str, list[str]]
    profiles: dict[str, HatchetResticProfileModel]


class HatchetResticConfig(HomelabBaseModel):
    container: str | None
    restic: HatchetResticModel


class HatchetResticModelConfig(HomelabBaseModel):
    RESTIC: ClassVar[str] = "restic"

    model: docker.ContainerCreationModel
    restic: HatchetResticModel

    @classmethod
    async def load(cls, config: Config) -> Self:
        raw_config = await config.load_service(cls.RESTIC, HatchetResticConfig)
        model = await DockerContainerRunConfig(
            service=cls.RESTIC, container=raw_config.container
        ).load(config)
        return cls(model=model.creation, restic=raw_config.restic)

    def resolve_profiles(self, keys: list[str]) -> list[str]:
        profiles: list[str] = []
        for key in keys:
            if key in self.restic.profiles:
                profiles.append(key)
            elif key in self.restic.groups:
                profiles += self.resolve_profiles(self.restic.groups[key])
            else:
                logger.error("Could not resolve restic key {}".format(key))
        return profiles

    def build_model(
        self, profile: str, read_only: bool, cmd: list[str]
    ) -> docker.ContainerCreationModel:
        profile_mount = self.restic.profiles[profile].to_mount(read_only)
        return copy.replace(
            self.model,
            host_config=(
                copy.replace(
                    self.model.host_config,
                    mounts=[*(self.model.host_config.mounts or []), profile_mount],
                )
                if self.model.host_config
                else docker.schema.ModelHostConfig.model_construct(
                    mounts=[profile_mount]
                )
            ),
            cmd=cmd,
            labels={},
        )


class HatchetResticBackupModel(HomelabBaseModel):
    profiles: list[str]

    @classmethod
    def build_cmd(cls, profile: str) -> list[str]:
        return ["-n", profile, "backup"]


class Restic:
    SERVICE = HatchetResticModelConfig.RESTIC

    @classmethod
    def build_workflows(cls, hatchet: Hatchet) -> list[BaseWorkflow[Any]]:
        docker_run_model_workflow = Docker.docker_run_model_workflow()

        restic_backup_workflow = hatchet.workflow(
            name="{}-backup".format(cls.SERVICE),
            input_validator=HatchetResticBackupModel,
        )

        @restic_backup_workflow.task(
            name="load-config",
            desired_worker_labels=[label.DESIRED_HOST_LABEL],
        )
        async def restic_load_config(
            input: HatchetResticBackupModel, context: Context, config: ConfigDependency
        ) -> HatchetResticModelConfig:
            return await HatchetResticModelConfig.load(config)

        # TODO: Use durable_task after worker affinity is stable
        @restic_backup_workflow.task(
            name="backup",
            execution_timeout=Docker.DOCKER_TIMEOUT,
            parents=[restic_load_config],
        )
        async def restic_backup(
            input: HatchetResticBackupModel, context: Context
        ) -> None:
            restic_config = context.task_output(restic_load_config)
            await docker_run_model_workflow.aio_run_many(
                [
                    docker_run_model_workflow.create_bulk_run_item(
                        DockerContainerRunModel(
                            creation=restic_config.build_model(
                                profile, True, input.build_cmd(profile)
                            ),
                            name_prefix=add_namespace(cls.SERVICE, profile),
                        ),
                        key=profile,
                    )
                    for profile in restic_config.resolve_profiles(input.profiles)
                ]
            )

        return [restic_backup_workflow]


build_workflows = Restic.build_workflows
