import logging
from typing import Any, ClassVar, Self

from hatchet_sdk import Context, Hatchet
from hatchet_sdk.runnables.workflow import BaseWorkflow
from homelab_hatchet_tool import label
from homelab_hatchet_tool.config import Config, ConfigDependency
from homelab_hatchet_tool.docker import Docker
from homelab_hatchet_tool.docker.model.run import (
    DockerContainerRunConfig,
    DockerContainerRunModel,
)
from homelab_pydantic import AbsolutePath, HomelabBaseModel, add_namespace, docker

logger = logging.getLogger("balite")


class HatchetBaliteProfileModel(HomelabBaseModel):
    VOLUME_OPTIONS: ClassVar[docker.schema.ModelMountVolumeOptions] = (
        docker.schema.ModelMountVolumeOptions.model_validate({"no_copy": True})
    )

    source_volume: str
    source_path: AbsolutePath
    destination_volume: str
    destination_path: AbsolutePath

    def to_mounts(self, read_only: bool) -> list[docker.schema.ModelMount]:
        return [
            docker.schema.ModelMount.model_validate(
                {
                    "type": "volume",
                    "target": self.source_path.as_posix(),
                    "source": self.source_volume,
                    "read_only": read_only,
                    "volume_options": self.VOLUME_OPTIONS,
                }
            ),
            docker.schema.ModelMount.model_validate(
                {
                    "type": "volume",
                    "target": self.destination_path.as_posix(),
                    "source": self.destination_volume,
                    "read_only": not read_only,
                    "volume_options": self.VOLUME_OPTIONS,
                }
            ),
        ]


class HatchetBaliteModel(HomelabBaseModel):
    groups: dict[str, list[str]]
    profiles: dict[str, HatchetBaliteProfileModel]


class HatchetBaliteConfig(HomelabBaseModel):
    container: str | None
    balite: HatchetBaliteModel


class HatchetBaliteBackupModel(HomelabBaseModel):
    profiles: list[str]

    @classmethod
    def build_cmd(cls, profile: str) -> list[str]:
        return ["backup", profile]


class HatchetBaliteModelConfig(HomelabBaseModel):
    BALITE: ClassVar[str] = "balite"
    BALITE_CMD: ClassVar[str] = "homelab-balite"
    CONFIG_KEY: ClassVar[str | None] = None

    model: docker.ContainerCreationModel
    balite: HatchetBaliteModel

    @classmethod
    async def load(cls, config: Config) -> Self:
        raw_config = await config.load_service(
            cls.BALITE, cls.CONFIG_KEY, HatchetBaliteConfig
        )
        model = await DockerContainerRunConfig(
            service=cls.BALITE, container=raw_config.container
        ).load(config)
        return cls(model=model.creation, balite=raw_config.balite)

    def resolve_profiles(self, keys: list[str]) -> list[str]:
        profiles: list[str] = []
        for key in keys:
            if key in self.balite.profiles:
                profiles.append(key)
            elif key in self.balite.groups:
                profiles += self.resolve_profiles(self.balite.groups[key])
            else:
                logger.error("Could not resolve balite key {}".format(key))
        return profiles

    def build_model(
        self, profile: str, read_only: bool, cmd: list[str]
    ) -> docker.ContainerCreationModel:
        profile_mounts = self.balite.profiles[profile].to_mounts(read_only)
        return self.model.model_copy(
            update={
                "host_config": self.model.host_config.model_copy(
                    update={
                        "mounts": (self.model.host_config.mounts or []) + profile_mounts
                    }
                )
                if self.model.host_config
                else docker.schema.ModelHostConfig.model_validate(
                    {"mounts": profile_mounts}
                ),
                "cmd": cmd,
            }
        )

    def build_backup_model(self, profile: str) -> DockerContainerRunModel:
        return DockerContainerRunModel(
            creation=self.build_model(
                profile,
                True,
                [self.BALITE_CMD, *HatchetBaliteBackupModel.build_cmd(profile)],
            ),
            name_prefix=add_namespace(self.BALITE, profile),
        )


class Balite:
    SERVICE = HatchetBaliteModelConfig.BALITE

    @classmethod
    async def backup_profiles(
        cls, balite_config: HatchetBaliteModelConfig, profiles: list[str]
    ) -> None:
        docker_run_model_workflow = Docker.docker_run_model_workflow()
        await docker_run_model_workflow.aio_run_many(
            [
                docker_run_model_workflow.create_bulk_run_item(
                    balite_config.build_backup_model(profile),
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
        balite_backup_workflow = hatchet.workflow(
            name="{}-backup".format(cls.SERVICE),
            input_validator=HatchetBaliteBackupModel,
            default_additional_metadata=label.build_labels(cls.SERVICE),
        )

        @balite_backup_workflow.task(
            name="load-config",
            desired_worker_labels=[label.DESIRED_HOST_LABEL],
        )
        async def balite_backup_load_config(
            input: HatchetBaliteBackupModel, context: Context, config: ConfigDependency
        ) -> HatchetBaliteModelConfig:
            return await HatchetBaliteModelConfig.load(config)

        # TODO: Use durable_task after worker affinity is stable
        @balite_backup_workflow.task(
            name="backup",
            execution_timeout=Docker.DOCKER_TIMEOUT,
            parents=[balite_backup_load_config],
        )
        async def balite_backup(
            input: HatchetBaliteBackupModel, context: Context
        ) -> None:
            balite_config = context.task_output(balite_backup_load_config)
            await cls.backup_profiles(
                balite_config, balite_config.resolve_profiles(input.profiles)
            )

        return [balite_backup_workflow]


build_workflows = Balite.build_workflows
