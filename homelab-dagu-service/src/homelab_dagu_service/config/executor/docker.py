import dataclasses
from typing import Any, Self

import deepmerge
import pulumi_docker as docker
from homelab_docker.model.container.model import (
    ContainerModel,
    ContainerModelBuildArgs,
    ContainerModelGlobalArgs,
    ContainerModelServiceArgs,
)
from pulumi import Output


@dataclasses.dataclass
class DaguDagDockerExecutorConfig:
    config: dict[str, Any]
    container_config: dict[str, Any]
    host_config: dict[str, Any]
    network_config: dict[str, Any]
    additional_config: dict[str, Any]

    @classmethod
    def from_container_model(
        cls,
        resource_name: str,
        container_model: ContainerModel,
        *,
        service_name: str,
        global_args: ContainerModelGlobalArgs,
        service_args: ContainerModelServiceArgs | None,
        build_args: ContainerModelBuildArgs | None,
        containers: dict[str, docker.Container],
        additional_config: dict[str, Any] | None = None,
    ) -> Self:
        build_args = build_args or ContainerModelBuildArgs()
        config: dict[str, Any] = {}
        container_config: dict[str, Any] = {}
        host_config: dict[str, Any] = {}
        network_config: dict[str, Any] = {}
        additional_config = additional_config or {"autoRemove": True, "pull": False}

        config["image"] = container_model.image.to_image_id(
            global_args.docker_resource.image
        )

        if container_model.user:
            container_config["user"] = container_model.user
        command = container_model.build_command()
        if command:
            container_config["cmd"] = command

        entrypoint = container_model.build_entrypoint()
        if entrypoint:
            container_config["entrypoint"] = entrypoint
        container_config["labels"] = container_model.build_labels(
            resource_name, service_name, global_args, build_args
        )
        container_config["env"] = container_model.build_envs(
            global_args, service_args, build_args
        )

        host_config["binds"] = container_model.volumes.to_binds(
            global_args.docker_resource.volume
        )

        network_args = container_model.network.to_args(
            resource_name, global_args.docker_resource.network, containers
        )
        if network_args.advanced:
            network_config["endpointsConfig"] = {
                network.name: {"aliases": network.aliases}
                for network in network_args.advanced
            }
        elif network_args.mode:
            host_config["networkMode"] = network_args.mode
        if container_model.capabilities:
            host_config["capAdd"] = container_model.capabilities

        host_config["readonlyRootfs"] = container_model.read_only
        mounts = container_model.build_tmpfs()
        if mounts:
            host_config["mounts"] = [
                {"type": mount.type, "target": mount.target}
                | (
                    {
                        "tmpfsOptions": {
                            "sizeBytes": Output.from_input(mount.tmpfs_options).apply(
                                lambda x: x.size_bytes
                            )
                        }
                    }
                    if mount.tmpfs_options
                    else {}
                )
                for mount in mounts
            ]
        if container_model.init:
            host_config["init"] = container_model.init

        return cls(
            config=config,
            container_config=container_config,
            host_config=host_config,
            network_config=network_config,
            additional_config=additional_config,
        )

    def to_hang_executor(self) -> Self:
        return self.__class__(
            config=self.config,
            container_config=self.container_config | {"entrypoint": ["/bin/sleep"]},
            host_config=self.host_config,
            network_config=self.network_config,
            additional_config=self.additional_config,
        )

    def to_executor(self) -> dict[str, Any]:
        return {
            "type": "docker",
            "config": deepmerge.always_merger.merge(
                self.config
                | {
                    "container": self.container_config,
                    "host": self.host_config,
                    "network": self.network_config,
                },
                self.additional_config,
            ),
        }
