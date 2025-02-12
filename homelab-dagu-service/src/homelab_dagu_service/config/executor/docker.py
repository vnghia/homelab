from typing import Any, Self

import pulumi_docker as docker
from homelab_docker.model.container.model import (
    ContainerModel,
    ContainerModelBuildArgs,
    ContainerModelGlobalArgs,
    ContainerModelServiceArgs,
)
from pulumi import Output
from pydantic import RootModel


class DaguDagDockerExecutorConfig(RootModel[dict[str, Any]]):
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
        additional: dict[str, Any] = {},
    ) -> Self:
        build_args = build_args or ContainerModelBuildArgs()
        config: dict[str, Any] = {}

        if container_model.user:
            config["user"] = container_model.user
        command = container_model.build_command()
        if command:
            config["cmd"] = command
        config["image"] = container_model.image.to_image_id(
            global_args.docker_resource.image
        )
        entrypoint = container_model.build_entrypoint()
        if entrypoint:
            config["entrypoint"] = entrypoint
        config["labels"] = container_model.build_labels(
            resource_name, service_name, global_args, build_args
        )

        host_config: dict[str, Any] = {}

        host_config["env"] = container_model.build_envs(
            global_args, service_args, build_args
        )
        host_config["binds"] = container_model.volumes.to_binds(
            global_args.docker_resource.volume
        )
        network_args = container_model.network.to_args(
            resource_name, global_args.docker_resource.network, containers
        )
        if network_args.advanced:
            networking_config: dict[str, Any] = {
                "endpointsConfig": {
                    network.name: {"aliases": network.aliases}
                    for network in network_args.advanced
                }
            }
            config["networking"] = networking_config
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

        config["host"] = host_config

        return cls(config | additional)

    def to_executor(self) -> dict[str, Any]:
        return {
            "type": "docker",
            "config": self.root,
        }
