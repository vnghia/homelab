import datetime
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

logger = logging.getLogger("restic")


class HatchetResticProfileModel(HomelabBaseModel):
    VOLUME_OPTIONS: ClassVar[docker.schema.ModelMountVolumeOptions] = (
        docker.schema.ModelMountVolumeOptions.model_validate({"no_copy": True})
    )

    volume: str
    path: AbsolutePath

    def to_mount(self, read_only: bool) -> docker.schema.ModelMount:
        return docker.schema.ModelMount.model_validate(
            {
                "type": "volume",
                "target": self.path.as_posix(),
                "source": self.volume,
                "read_only": read_only,
                "volume_options": self.VOLUME_OPTIONS,
            }
        )


class HatchetResticModel(HomelabBaseModel):
    groups: dict[str, list[str]]
    profiles: dict[str, HatchetResticProfileModel]


class HatchetResticConfig(HomelabBaseModel):
    container: str | None
    restic: HatchetResticModel


class HatchetResticBackupModel(HomelabBaseModel):
    def build_backup_cmd(self, profile: str) -> list[str]:
        return ["-n", profile, "backup"]


class HatchetResticModelConfig(HomelabBaseModel):
    RESTIC: ClassVar[str] = "restic"
    CONFIG_KEY: ClassVar[str | None] = None

    model: docker.ContainerCreationModel
    restic: HatchetResticModel

    @classmethod
    async def load(cls, config: Config) -> Self:
        raw_config = await config.load_service(
            cls.RESTIC, cls.CONFIG_KEY, HatchetResticConfig
        )
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
        return self.model.model_copy(
            update={
                "host_config": self.model.host_config.model_copy(
                    update={
                        "mounts": [
                            *(self.model.host_config.mounts or []),
                            profile_mount,
                        ],
                    }
                )
                if self.model.host_config
                else docker.schema.ModelHostConfig.model_validate(
                    {"mounts": [profile_mount]}
                ),
                "cmd": cmd,
            }
        )

    def build_backup_model(
        self, profile: str, model: HatchetResticBackupModel
    ) -> DockerContainerRunModel:
        return DockerContainerRunModel(
            creation=self.build_model(profile, True, model.build_backup_cmd(profile)),
            name_prefix=add_namespace(self.RESTIC, profile),
        )


class HatchetResticBackupInputModel(HomelabBaseModel):
    profiles: str | list[str]
    backup: HatchetResticBackupModel = HatchetResticBackupModel()
    restic: HatchetResticModelConfig | None = None


class Restic:
    SERVICE = HatchetResticModelConfig.RESTIC

    SCHEDULE_TIMEOUT = datetime.timedelta(hours=6)
    CONCURRENCY = 5

    _restic_backup_workflow: Standalone[HatchetResticBackupInputModel, None] | None

    @classmethod
    def restic_backup_workflow(
        cls,
    ) -> Standalone[HatchetResticBackupInputModel, None]:
        if not cls._restic_backup_workflow:
            raise RuntimeError(
                "Please call `build_workflows` at least once before accesing this function"
            )
        return cls._restic_backup_workflow

    @classmethod
    async def backup_profiles(
        cls,
        restic_config: HatchetResticModelConfig,
        profiles: list[str],
        backup: HatchetResticBackupModel,
    ) -> None:
        restic_backup_workflow = cls.restic_backup_workflow()
        await restic_backup_workflow.aio_run_many(
            [
                restic_backup_workflow.create_bulk_run_item(
                    HatchetResticBackupInputModel(
                        profiles=profile, backup=backup, restic=restic_config
                    ),
                    key=profile,
                    additional_metadata=label.build_labels(cls.SERVICE)
                    | {"{}-profile".format(cls.SERVICE): profile},
                    desired_worker_labels=[
                        label.DESIRED_HOST_LABEL,
                        label.DESIRED_DOCKER_LABEL,
                    ],
                )
                for profile in profiles
            ],
        )

    @classmethod
    def build_workflows(cls, hatchet: Hatchet) -> list[BaseWorkflow[Any]]:
        @hatchet.task(
            name="{}-backup".format(cls.SERVICE),
            input_validator=HatchetResticBackupInputModel,
            schedule_timeout=cls.SCHEDULE_TIMEOUT,
            execution_timeout=Docker.DOCKER_TIMEOUT,
            concurrency=cls.CONCURRENCY,
            desired_worker_labels=[
                label.DESIRED_HOST_LABEL,
                label.DESIRED_DOCKER_LABEL,
            ],
            default_additional_metadata=label.build_labels(cls.SERVICE),
        )
        async def restic_backup(
            input: HatchetResticBackupInputModel,
            context: Context,
            config: ConfigDependency,
        ) -> None:
            restic_config = input.restic or (
                await HatchetResticModelConfig.load(config)
            )
            if isinstance(input.profiles, str):
                await Docker.run_container(
                    context,
                    restic_config.build_backup_model(input.profiles, input.backup),
                )
                return None
            return await cls.backup_profiles(
                restic_config,
                restic_config.resolve_profiles(input.profiles),
                input.backup,
            )

        cls._restic_backup_workflow = restic_backup

        return [cls._restic_backup_workflow]


build_workflows = Restic.build_workflows
