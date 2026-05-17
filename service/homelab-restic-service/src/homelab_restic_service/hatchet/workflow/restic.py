import datetime
import logging
from typing import Any, ClassVar, Iterable, Self

from hatchet_sdk import Context, Hatchet
from hatchet_sdk.runnables.workflow import BaseWorkflow, Standalone
from homelab_hatchet_tool import constant
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

    repository: str
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
    groups: dict[str, set[str]]
    profiles: dict[str, HatchetResticProfileModel]


class HatchetResticConfig(HomelabBaseModel):
    container: str | None
    restic: HatchetResticModel


class HatchetResticBackupModel(HomelabBaseModel):
    def build_cmd(self, profile: str) -> list[str]:
        return ["-n", profile, "backup"]


class HatchetResticCheckModel(HomelabBaseModel):
    read_data: bool | str = False

    def build_cmd(self, profile: str) -> list[str]:
        return [
            "-n",
            profile,
            "check",
            (
                "--read-data={}".format(str(self.read_data).lower())
                if isinstance(self.read_data, bool)
                else "--read-data-subset={}".format(self.read_data)
            ),
        ]


class HatchetResticForgetModel(HomelabBaseModel):
    prune: bool = False

    def build_cmd(self, profile: str) -> list[str]:
        return ["-n", profile, "forget", "--prune={}".format(str(self.prune).lower())]


class HatchetResticPruneModel(HomelabBaseModel):
    def build_cmd(self, profile: str) -> list[str]:
        return ["-n", profile, "prune"]


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

    def resolve_profiles(self, keys: Iterable[str]) -> set[str]:
        if constant.INPUT_ALL in keys:
            return set(self.restic.profiles.keys())

        profiles: set[str] = set()
        for key in keys:
            if key in self.restic.profiles:
                profiles.add(key)
            elif key in self.restic.groups:
                profiles |= self.resolve_profiles(self.restic.groups[key])
            else:
                logger.error("Could not resolve restic key {}".format(key))
        return profiles

    def resolve_repositories(self, keys: Iterable[str]) -> set[str]:
        if constant.INPUT_ALL in keys:
            return self.resolve_repositories(self.restic.profiles.keys())

        repositories: set[str] = set()
        for key in keys:
            if key in self.restic.profiles:
                repositories.add(self.restic.profiles[key].repository)
            elif key in self.restic.groups:
                repositories |= self.resolve_repositories(self.restic.groups[key])
            else:
                logger.error("Could not resolve restic key {}".format(key))
        return repositories

    def build_model(
        self, profile: str | None, read_only: bool, cmd: list[str]
    ) -> docker.ContainerCreationModel:
        profile_mount = (
            self.restic.profiles[profile].to_mount(read_only) if profile else None
        )
        return self.model.model_copy(
            update={"cmd": cmd}
            | (
                {
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
                    )
                }
                if profile_mount
                else {}
            )
        )

    def build_backup_model(
        self, profile: str, model: HatchetResticBackupModel
    ) -> DockerContainerRunModel:
        return DockerContainerRunModel(
            creation=self.build_model(profile, True, model.build_cmd(profile)),
            name_prefix=add_namespace(self.RESTIC, profile),
        )

    def build_check_model(
        self, profile: str, model: HatchetResticCheckModel
    ) -> DockerContainerRunModel:
        return DockerContainerRunModel(
            creation=self.build_model(profile, True, model.build_cmd(profile)),
            name_prefix=add_namespace(self.RESTIC, profile),
        )

    def build_forget_model(
        self, profile: str, model: HatchetResticForgetModel
    ) -> DockerContainerRunModel:
        return DockerContainerRunModel(
            creation=self.build_model(None, True, model.build_cmd(profile)),
            name_prefix=add_namespace(self.RESTIC, profile),
        )

    def build_prune_model(
        self, profile: str, model: HatchetResticPruneModel
    ) -> DockerContainerRunModel:
        return DockerContainerRunModel(
            creation=self.build_model(None, True, model.build_cmd(profile)),
            name_prefix=add_namespace(self.RESTIC, profile),
        )


class HatchetResticBaseInputModel(HomelabBaseModel):
    profiles: str | set[str]
    restic: HatchetResticModelConfig | None = None


class HatchetResticBackupInputModel(HatchetResticBaseInputModel):
    backup: HatchetResticBackupModel = HatchetResticBackupModel()


class HatchetResticCheckInputModel(HatchetResticBaseInputModel):
    check: HatchetResticCheckModel = HatchetResticCheckModel()


class HatchetResticForgetInputModel(HatchetResticBaseInputModel):
    forget: HatchetResticForgetModel = HatchetResticForgetModel()


class HatchetResticPruneInputModel(HatchetResticBaseInputModel):
    prune: HatchetResticPruneModel = HatchetResticPruneModel()


class Restic:
    SERVICE = HatchetResticModelConfig.RESTIC

    SCHEDULE_TIMEOUT = datetime.timedelta(hours=6)
    CONCURRENCY = 5

    _restic_backup_workflow: Standalone[HatchetResticBackupInputModel, None] | None
    _restic_check_workflow: Standalone[HatchetResticCheckInputModel, None] | None
    _restic_forget_workflow: Standalone[HatchetResticForgetInputModel, None] | None
    _restic_prune_workflow: Standalone[HatchetResticPruneInputModel, None] | None

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
    def restic_check_workflow(
        cls,
    ) -> Standalone[HatchetResticCheckInputModel, None]:
        if not cls._restic_check_workflow:
            raise RuntimeError(
                "Please call `build_workflows` at least once before accesing this function"
            )
        return cls._restic_check_workflow

    @classmethod
    def restic_forget_workflow(
        cls,
    ) -> Standalone[HatchetResticForgetInputModel, None]:
        if not cls._restic_forget_workflow:
            raise RuntimeError(
                "Please call `build_workflows` at least once before accesing this function"
            )
        return cls._restic_forget_workflow

    @classmethod
    def restic_prune_workflow(
        cls,
    ) -> Standalone[HatchetResticPruneInputModel, None]:
        if not cls._restic_prune_workflow:
            raise RuntimeError(
                "Please call `build_workflows` at least once before accesing this function"
            )
        return cls._restic_prune_workflow

    @classmethod
    async def backup_profiles(
        cls,
        restic_config: HatchetResticModelConfig,
        profiles: Iterable[str],
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
                    additional_metadata=constant.build_labels(cls.SERVICE)
                    | {"{}-profile".format(cls.SERVICE): profile},
                    desired_worker_labels=[
                        constant.DESIRED_HOST_LABEL,
                        constant.DESIRED_DOCKER_LABEL,
                    ],
                )
                for profile in profiles
            ],
        )

    @classmethod
    async def check_profiles(
        cls,
        restic_config: HatchetResticModelConfig,
        profiles: Iterable[str],
        check: HatchetResticCheckModel,
    ) -> None:
        restic_check_workflow = cls.restic_check_workflow()
        await restic_check_workflow.aio_run_many(
            [
                restic_check_workflow.create_bulk_run_item(
                    HatchetResticCheckInputModel(
                        profiles=profile, check=check, restic=restic_config
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
            ],
        )

    @classmethod
    async def forget_profiles(
        cls,
        restic_config: HatchetResticModelConfig,
        profiles: Iterable[str],
        forget: HatchetResticForgetModel,
    ) -> None:
        restic_forget_workflow = cls.restic_forget_workflow()
        await restic_forget_workflow.aio_run_many(
            [
                restic_forget_workflow.create_bulk_run_item(
                    HatchetResticForgetInputModel(
                        profiles=profile, forget=forget, restic=restic_config
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
            ],
        )

    @classmethod
    async def prune_profiles(
        cls,
        restic_config: HatchetResticModelConfig,
        profiles: Iterable[str],
        prune: HatchetResticPruneModel,
    ) -> None:
        restic_prune_workflow = cls.restic_prune_workflow()
        await restic_prune_workflow.aio_run_many(
            [
                restic_prune_workflow.create_bulk_run_item(
                    HatchetResticPruneInputModel(
                        profiles=profile, prune=prune, restic=restic_config
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
                constant.DESIRED_HOST_LABEL,
                constant.DESIRED_DOCKER_LABEL,
            ],
            default_additional_metadata=constant.build_labels(cls.SERVICE),
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

        @hatchet.task(
            name="{}-check".format(cls.SERVICE),
            input_validator=HatchetResticCheckInputModel,
            schedule_timeout=cls.SCHEDULE_TIMEOUT,
            execution_timeout=Docker.DOCKER_TIMEOUT,
            concurrency=cls.CONCURRENCY,
            desired_worker_labels=[
                constant.DESIRED_HOST_LABEL,
                constant.DESIRED_DOCKER_LABEL,
            ],
            default_additional_metadata=constant.build_labels(cls.SERVICE),
        )
        async def restic_check(
            input: HatchetResticCheckInputModel,
            context: Context,
            config: ConfigDependency,
        ) -> None:
            restic_config = input.restic or (
                await HatchetResticModelConfig.load(config)
            )
            if isinstance(input.profiles, str):
                await Docker.run_container(
                    context,
                    restic_config.build_check_model(input.profiles, input.check),
                )
                return None
            return await cls.check_profiles(
                restic_config,
                # Because checking is a repository-wise operations,
                # we need to run it on a repository basic.
                restic_config.resolve_repositories(input.profiles),
                input.check,
            )

        @hatchet.task(
            name="{}-forget".format(cls.SERVICE),
            input_validator=HatchetResticForgetInputModel,
            schedule_timeout=cls.SCHEDULE_TIMEOUT,
            execution_timeout=Docker.DOCKER_TIMEOUT,
            concurrency=cls.CONCURRENCY,
            desired_worker_labels=[
                constant.DESIRED_HOST_LABEL,
                constant.DESIRED_DOCKER_LABEL,
            ],
            default_additional_metadata=constant.build_labels(cls.SERVICE),
        )
        async def restic_forget(
            input: HatchetResticForgetInputModel,
            context: Context,
            config: ConfigDependency,
        ) -> None:
            restic_config = input.restic or (
                await HatchetResticModelConfig.load(config)
            )
            if isinstance(input.profiles, str):
                await Docker.run_container(
                    context,
                    restic_config.build_forget_model(input.profiles, input.forget),
                )
                return None
            return await cls.forget_profiles(
                restic_config,
                restic_config.resolve_profiles(input.profiles),
                input.forget,
            )

        @hatchet.task(
            name="{}-prune".format(cls.SERVICE),
            input_validator=HatchetResticPruneInputModel,
            schedule_timeout=cls.SCHEDULE_TIMEOUT,
            execution_timeout=Docker.DOCKER_TIMEOUT,
            concurrency=cls.CONCURRENCY,
            desired_worker_labels=[
                constant.DESIRED_HOST_LABEL,
                constant.DESIRED_DOCKER_LABEL,
            ],
            default_additional_metadata=constant.build_labels(cls.SERVICE),
        )
        async def restic_prune(
            input: HatchetResticPruneInputModel,
            context: Context,
            config: ConfigDependency,
        ) -> None:
            restic_config = input.restic or (
                await HatchetResticModelConfig.load(config)
            )
            if isinstance(input.profiles, str):
                await Docker.run_container(
                    context,
                    restic_config.build_prune_model(input.profiles, input.prune),
                )
                return None
            return await cls.prune_profiles(
                restic_config,
                # Because pruning is a repository-wise operations,
                # we need to run it on a repository basic.
                restic_config.resolve_repositories(input.profiles),
                input.prune,
            )

        cls._restic_backup_workflow = restic_backup
        cls._restic_check_workflow = restic_check
        cls._restic_forget_workflow = restic_forget
        cls._restic_prune_workflow = restic_prune

        return [
            cls._restic_backup_workflow,
            cls._restic_check_workflow,
            cls._restic_forget_workflow,
            cls._restic_prune_workflow,
        ]


build_workflows = Restic.build_workflows
