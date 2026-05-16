import logging
from typing import Any, ClassVar, Self

from hatchet_sdk import Context, Hatchet
from hatchet_sdk.runnables.workflow import BaseWorkflow, Standalone
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

    @classmethod
    def build_backup_cmd(cls, profile: str) -> list[str]:
        return [cls.BALITE_CMD, "backup", profile]

    def build_backup_model(self, profile: str) -> DockerContainerRunModel:
        return DockerContainerRunModel(
            creation=self.build_model(profile, True, self.build_backup_cmd(profile)),
            name_prefix=add_namespace(self.BALITE, profile),
        )


class HatchetBaliteBackupModel(HomelabBaseModel):
    profiles: str | list[str]
    balite: HatchetBaliteModelConfig | None = None


class Balite:
    SERVICE = HatchetBaliteModelConfig.BALITE

    _balite_backup_workflow: Standalone[HatchetBaliteBackupModel, None] | None

    @classmethod
    def balite_backup_workflow(cls) -> Standalone[HatchetBaliteBackupModel, None]:
        if not cls._balite_backup_workflow:
            raise RuntimeError(
                "Please call `build_workflows` at least once before accesing this function"
            )
        return cls._balite_backup_workflow

    @classmethod
    async def backup_profiles(
        cls, balite_config: HatchetBaliteModelConfig, profiles: list[str]
    ) -> None:
        balite_backup_workflow = cls.balite_backup_workflow()
        await balite_backup_workflow.aio_run_many(
            [
                balite_backup_workflow.create_bulk_run_item(
                    HatchetBaliteBackupModel(profiles=profile, balite=balite_config),
                    key=profile,
                    additional_metadata=label.build_labels(cls.SERVICE)
                    | {"{}-profile".format(cls.SERVICE): profile},
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
            name="{}-backup".format(cls.SERVICE),
            input_validator=HatchetBaliteBackupModel,
            execution_timeout=Docker.DOCKER_TIMEOUT,
            concurrency=5,
            desired_worker_labels=[
                label.DESIRED_HOST_LABEL,
                label.DESIRED_DOCKER_LABEL,
            ],
            default_additional_metadata=label.build_labels(cls.SERVICE),
        )
        async def balite_backup(
            input: HatchetBaliteBackupModel, context: Context, config: ConfigDependency
        ) -> None:
            balite_config = input.balite or (
                await HatchetBaliteModelConfig.load(config)
            )
            if isinstance(input.profiles, str):
                await Docker.run_container(
                    context, balite_config.build_backup_model(input.profiles)
                )
                return None
            return await cls.backup_profiles(
                balite_config, balite_config.resolve_profiles(input.profiles)
            )

        cls._balite_backup_workflow = balite_backup

        return [cls._balite_backup_workflow]


build_workflows = Balite.build_workflows
