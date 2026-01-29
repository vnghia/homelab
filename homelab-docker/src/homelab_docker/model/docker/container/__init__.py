from __future__ import annotations

import dataclasses
import typing
import uuid
from typing import Any, Literal, Mapping, Sequence

import pulumi
import pulumi_docker as docker
from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel
from homelab_pydantic.path import AbsolutePath
from pulumi import (
    Input,
    Output,
    Resource,
    ResourceHook,
    ResourceHookArgs,
    ResourceHookBinding,
    ResourceOptions,
)
from pydantic import Field, PositiveInt

from ....extract.global_ import GlobalExtractor
from ...user import UidGidModel
from .cap import ContainerCapConfig
from .database import ContainerDatabaseConfig
from .docker_socket import ContainerDockerSocketConfig
from .healthcheck import ContainerHealthCheckConfig
from .host import ContainerHostConfig
from .image import ContainerImageModelConfig
from .inherit import ContainerInheritConfig
from .mail import ContainerMailConfig
from .network import (
    ContainerBridgeNetworkArgs,
    ContainerCommonNetworkConfig,
    ContainerNetworkConfig,
)
from .observability import ContainerObservabilityConfig
from .ports import ContainerPortsConfig
from .s3 import ContainerS3Config
from .tmpfs import ContainerTmpfsConfig
from .user import ContainerUserConfig
from .volume import (
    ContainerVolumeConfig,
    ContainerVolumeFullConfig,
    ContainerVolumesConfig,
)
from .wud import ContainerWudConfig

if typing.TYPE_CHECKING:
    from ....extract import ExtractorArgs
    from ....resource.file import FileResource
    from ....resource.host import HostResourceBase


@dataclasses.dataclass
class ContainerNetworkModelBuildArgs:
    hosts: list[ContainerHostConfig] = dataclasses.field(default_factory=list)
    ports: ContainerPortsConfig = dataclasses.field(
        default_factory=ContainerPortsConfig
    )
    bridges: dict[str, ContainerBridgeNetworkArgs] = dataclasses.field(
        default_factory=dict
    )

    def __iadd__(
        self, rhs: ContainerNetworkModelBuildArgs
    ) -> ContainerNetworkModelBuildArgs:
        self.add_hosts(rhs.hosts)
        self.add_ports(rhs.ports)
        self.add_bridges(rhs.bridges)
        return self

    def add_hosts(self, hosts: list[ContainerHostConfig]) -> None:
        self.hosts += hosts

    def add_ports(self, ports: ContainerPortsConfig) -> None:
        self.ports |= ports

    def add_bridges(self, bridges: dict[str, ContainerBridgeNetworkArgs]) -> None:
        self.bridges |= bridges


@dataclasses.dataclass
class ContainerModelBuildArgs:
    opts: ResourceOptions | None = None
    envs: Mapping[str, Input[str]] = dataclasses.field(default_factory=dict)
    volumes: Mapping[str, ContainerVolumeConfig] = dataclasses.field(
        default_factory=dict
    )
    files: Sequence[FileResource] = dataclasses.field(default_factory=list)

    network: ContainerNetworkModelBuildArgs = dataclasses.field(
        default_factory=ContainerNetworkModelBuildArgs
    )

    def add_envs(self, envs: Mapping[str, Input[str]]) -> None:
        self.envs = {**self.envs, **envs}

    def add_volumes(self, volumes: Mapping[str, ContainerVolumeConfig]) -> None:
        self.volumes = {**self.volumes, **volumes}

    def add_files(self, files: Sequence[FileResource]) -> None:
        self.files = [*self.files, *files]

    def add_network(self, network: ContainerNetworkModelBuildArgs) -> None:
        self.network += network


class ContainerModel(HomelabBaseModel):
    active: bool = True
    oneshot: bool = False
    depends_on: list[str | None] = []
    delete_before_replace: bool = False
    inherit: ContainerInheritConfig = ContainerInheritConfig()

    raw_image: ContainerImageModelConfig | None = Field(None, alias="image")

    cap: ContainerCapConfig = ContainerCapConfig()
    command: list[GlobalExtract] | None = None
    databases: list[ContainerDatabaseConfig] | None = None
    devices: list[AbsolutePath] | None = None
    docker_socket: ContainerDockerSocketConfig | None = None
    entrypoint: list[GlobalExtract] | None = None
    group_adds: list[str | None] | None = None
    healthcheck: ContainerHealthCheckConfig | None = None
    hostname: GlobalExtract | None = None
    hosts: list[ContainerHostConfig] = []
    init: bool | None = None
    mails: list[ContainerMailConfig] | None = None
    network: ContainerNetworkConfig = ContainerNetworkConfig()
    observability: ContainerObservabilityConfig | None = None
    ports: ContainerPortsConfig = ContainerPortsConfig()
    privileged: bool | None = None
    read_only: bool = True
    remove: bool = False
    restart: Literal["unless-stopped"] = "unless-stopped"
    s3: ContainerS3Config | None = None
    security_opts: list[str] = ["no-new-privileges"]
    sysctls: dict[str, str] | None = None
    tmpfs: list[ContainerTmpfsConfig] | None = None
    user: ContainerUserConfig | None = None
    volumes: ContainerVolumesConfig = ContainerVolumesConfig()
    wait: bool = True
    wait_timeout: PositiveInt | None = None
    wud: ContainerWudConfig | None = None

    envs: dict[str, GlobalExtract | None] = {}
    labels: dict[str, GlobalExtract] = {}

    @property
    def image(self) -> ContainerImageModelConfig:
        if not self.raw_image:
            raise ValueError("Image config model is None")
        return self.raw_image

    def to_full(self, extractor_args: ExtractorArgs) -> ContainerModel:
        if "inherit" in self.model_fields_set:
            inherit = self.inherit.to_full()
            models = (
                extractor_args.service.model
                if inherit.service is None
                else extractor_args.host_model.services[inherit.service]
            )
            return models[inherit.container].model_merge(self, override=True)
        return self

    def build_cap(self) -> docker.ContainerCapabilitiesArgs | None:
        return (
            docker.ContainerCapabilitiesArgs(adds=self.cap.add, drops=self.cap.drop)
            if self.cap
            else None
        )

    def build_command(self, extractor_args: ExtractorArgs) -> list[Output[str]] | None:
        return (
            [
                GlobalExtractor(command).extract_str(extractor_args)
                for command in self.command
            ]
            if self.command is not None
            else None
        )

    def build_entrypoint(
        self, extractor_args: ExtractorArgs
    ) -> list[Output[str]] | None:
        return (
            [
                GlobalExtractor(entrypoint).extract_str(extractor_args)
                for entrypoint in self.entrypoint
            ]
            if self.entrypoint is not None
            else None
        )

    def build_group_adds(
        self, extractor_args: ExtractorArgs, user: UidGidModel
    ) -> list[str] | None:
        from ....config.user import UidGidConfig

        group_adds = []
        if self.group_adds:
            group_adds = self.group_adds
        if self.docker_socket and not user.is_root:
            group_adds.append(UidGidConfig.DOCKER_KEY)

        group_ids = [
            str(gid)
            for group in group_adds
            if (gid := extractor_args.host_model.users[group].gid) != user.gid
        ]
        if group_ids:
            return group_ids
        return None

    def build_tmpfs(self, user: UidGidModel) -> dict[str, str] | None:
        return (
            {
                tmpfs[0].as_posix(): tmpfs[1]
                for tmpfs in [tmpfs.to_args(user) for tmpfs in self.tmpfs]
            }
            if self.tmpfs
            else None
        )

    def build_user(self, extractor_args: ExtractorArgs) -> UidGidModel:
        return (
            self.user.model(extractor_args.host_model.users)
            if self.user
            else extractor_args.service.user
        )

    def build_container_user(self, user: UidGidModel) -> str | None:
        return user.container()

    def build_envs(
        self,
        extractor_args: ExtractorArgs,
        build_args: ContainerModelBuildArgs,
    ) -> list[Output[str]]:
        service = extractor_args.service

        additional_envs: dict[str, Input[str]] = {}
        if self.s3:
            additional_envs |= self.s3.build_envs(extractor_args)
        if self.databases:
            for database in self.databases:
                additional_envs |= database.build_envs(service.database)
        if self.mails:
            for mail in self.mails:
                additional_envs |= mail.to_envs(extractor_args)

        return [
            Output.concat(k, "=", v)
            for k, v in sorted(
                (
                    {"TZ": Output.from_input(extractor_args.host_model.timezone)}
                    | {
                        k: Output.from_input(
                            GlobalExtractor(v).extract_str(extractor_args)
                        )
                        for k, v in self.envs.items()
                        if v is not None
                    }
                    | {
                        k: Output.from_input(v)
                        for k, v in (dict(build_args.envs) | additional_envs).items()
                    }
                ).items(),
                key=lambda x: x[0],
            )
        ]

    def build_labels(
        self,
        resource_name: str,
        extractor_args: ExtractorArgs,
        build_args: ContainerModelBuildArgs,
    ) -> dict[Output[str], Output[str]]:
        service = extractor_args.service

        return (
            {
                Output.from_input(k): Output.from_input(v)
                for k, v in (
                    extractor_args.global_resource.project_args.labels
                    | {
                        "dev.dozzle.group": service.name(),
                        "dev.dozzle.name": resource_name,
                        "homelab.host": extractor_args.host.name,
                        "homelab.service": service.name(),
                        "homelab.container": resource_name,
                    }
                    | (
                        self.wud.build_labels(resource_name)
                        if self.wud and not self.oneshot
                        else {}
                    )
                ).items()
            }
            | {
                Output.from_input(k): GlobalExtractor(v).extract_str(extractor_args)
                for k, v in self.labels.items()
            }
            | {file.id: file.hash for file in build_args.files}
        )

    def build_hosts(
        self, extractor_args: ExtractorArgs, build_args: ContainerModelBuildArgs
    ) -> list[docker.ContainerHostArgs] | None:
        network = self.network.root
        if isinstance(network, ContainerCommonNetworkConfig):
            hosts = self.hosts + build_args.network.hosts
            return [host.to_args(extractor_args) for host in hosts] if hosts else None
        return None

    def build_ports(
        self, extractor_args: ExtractorArgs, build_args: ContainerModelBuildArgs
    ) -> Output[list[docker.ContainerPortArgs]]:
        network = self.network.root
        if isinstance(network, ContainerCommonNetworkConfig):
            return self.ports.to_args(extractor_args, build_args)
        return Output.from_input([])

    def build_args(
        self,
        build_args: ContainerModelBuildArgs | None,
        extractor_args: ExtractorArgs,
    ) -> ContainerModelBuildArgs:
        build_args = build_args or ContainerModelBuildArgs()
        files = list(build_args.files)
        for volume, model in self.volumes.volumes.items():
            if isinstance(volume, str) and (
                not isinstance(model.root, ContainerVolumeFullConfig)
                or model.root.bind_file
            ):
                files += extractor_args.host.docker.volume.files[volume]
        build_args.files = files
        return build_args

    @classmethod
    def remove_oneshot_hook(
        cls, args: ResourceHookArgs, host_resource: HostResourceBase
    ) -> None:
        outputs = args.new_outputs
        if not outputs:
            raise RuntimeError("This hook can only be called after resource creation")

        container = outputs["name"]
        if exit_code := int(outputs["exitCode"]):
            raise RuntimeError(
                "Oneshot container {} exists with non-zero status {}. Please manually remove it after investigation".format(
                    container, exit_code
                )
            )

        pulumi.info("Removing oneshot container {}".format(container))
        host_resource.docker_client.containers.get(container).remove(v=True, force=True)

    def build_resource(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions,
        extractor_args: ExtractorArgs,
        build_args: ContainerModelBuildArgs | None,
    ) -> docker.Container:
        extractor_args = extractor_args.with_container(self)
        service = extractor_args.service

        build_args = self.build_args(build_args, extractor_args)
        network_args = self.network.to_args(resource_name, extractor_args, build_args)
        user = self.build_user(extractor_args)

        depends_on: list[Resource] = []
        depends_on.extend(build_args.files)
        if self.databases:
            depends_on.extend(
                service.containers[
                    database.to_container_name(service.database)
                ].resource
                for database in self.databases
            )

        resource_labels = {}
        if (
            digest := self.image.to_build_image_digest(extractor_args.host.docker.image)
        ) is not None:
            resource_labels["image.build.digest"] = digest

        remove_oneshot_hook = (
            ResourceHook(
                name=uuid.uuid4().hex,
                func=lambda args: self.remove_oneshot_hook(args, extractor_args.host),
            )
            if self.oneshot
            else None
        )

        return docker.Container(
            resource_name,
            opts=ResourceOptions.merge(
                opts,
                ResourceOptions.merge(
                    build_args.opts,
                    ResourceOptions(
                        depends_on=depends_on,
                        delete_before_replace=self.delete_before_replace
                        or bool(self.ports)
                        or bool(build_args.network.ports),
                        hooks=ResourceHookBinding(
                            after_create=[remove_oneshot_hook]
                            if remove_oneshot_hook
                            else None
                        ),
                        replace_on_changes=["mounts", "tmpfs", "volumes"],
                        retain_on_delete=self.oneshot,
                    ),
                ),
            ),
            attach=self.oneshot,
            image=self.image.to_image_name(extractor_args.host.docker.image),
            capabilities=self.build_cap(),
            command=self.build_command(extractor_args),
            devices=[
                docker.ContainerDeviceArgs(
                    host_path=device.as_posix(), container_path=device.as_posix()
                )
                for device in self.devices
            ]
            if self.devices
            else None,
            group_adds=self.build_group_adds(extractor_args, user),
            entrypoints=self.build_entrypoint(extractor_args),
            healthcheck=self.healthcheck.to_args(extractor_args)
            if self.healthcheck and not self.oneshot
            else None,
            hostname=GlobalExtractor(self.hostname).extract_str(extractor_args)
            if self.hostname
            else None,
            hosts=self.build_hosts(extractor_args, build_args),
            init=self.init,
            logs=self.oneshot,
            mounts=self.volumes.to_args(self.docker_socket, extractor_args, build_args),
            must_run=not self.oneshot,
            network_mode=network_args.mode,
            networks_advanced=network_args.advanced,
            ports=self.build_ports(extractor_args, build_args),
            privileged=self.privileged,
            read_only=self.read_only,
            rm=self.remove,
            restart="no" if self.oneshot else self.restart,
            security_opts=self.security_opts,
            sysctls=self.sysctls,
            tmpfs=self.build_tmpfs(user),
            user=self.build_container_user(user),
            wait=self.wait if self.healthcheck else False,
            wait_timeout=self.healthcheck.start_period
            if self.healthcheck
            else self.wait_timeout,
            envs=self.build_envs(extractor_args, build_args),
            labels=[
                docker.ContainerLabelArgs(label=k, value=v)
                for k, v in (
                    self.build_labels(resource_name, extractor_args, build_args)
                    | resource_labels
                ).items()
            ],
        )

    def build_docker_py_args(
        self,
        resource_name: str,
        extractor_args: ExtractorArgs,
        build_args: ContainerModelBuildArgs | None,
    ) -> dict[str, Any]:
        kwargs: dict[str, Any] = {"detach": False, "stream": False}
        extractor_args = extractor_args.with_container(self)

        build_args = self.build_args(build_args, extractor_args)
        user = self.build_user(extractor_args)

        kwargs["image"] = self.image.to_image_name(extractor_args.host.docker.image)

        kwargs["user"] = self.build_container_user(user)

        if (entrypoint := self.build_entrypoint(extractor_args)) is not None:
            kwargs["entrypoint"] = entrypoint

        kwargs["labels"] = self.build_labels(resource_name, extractor_args, build_args)

        kwargs["environment"] = self.build_envs(extractor_args, build_args)

        kwargs["mounts"] = [
            {
                "type": arg.type,
                "target": arg.target,
                "read_only": arg.read_only,
                "source": arg.source,
            }
            for arg in self.volumes.to_args(
                self.docker_socket, extractor_args, build_args
            )
        ]

        network_args = self.network.to_args(None, extractor_args, build_args)
        if network_args.advanced:
            kwargs["networking_config"] = {
                network.name: {"aliases": network.aliases}
                for network in network_args.advanced
            }
        elif network_args.mode:
            kwargs["network_mode"] = network_args.mode

        if cap := self.build_cap():
            if cap.adds:
                kwargs["cap_add"] = cap.adds
            if cap.drops:
                kwargs["cap_drop"] = cap.drops

        kwargs["read_only"] = self.read_only
        kwargs["security_opt"] = self.security_opts

        if tmpfses := self.build_tmpfs(user):
            kwargs["tmpfs"] = tmpfses
        if self.init:
            kwargs["init"] = self.init

        return kwargs
