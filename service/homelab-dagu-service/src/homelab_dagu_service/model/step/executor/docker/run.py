from typing import Any

from homelab_docker.model.container import ContainerModelBuildArgs
from homelab_docker.resource.file.dotenv import DotenvFileResource
from homelab_docker.resource.service import ServiceResourceBase
from homelab_pydantic import HomelabBaseModel
from pulumi import Input, Output


class DaguDagStepDockerRunExecutorModel(HomelabBaseModel):
    model: str | None
    auto_remove: bool = True
    pull: bool = False

    entrypoint: list[str] | None = None

    def to_executor_config[T](
        self,
        main_service: ServiceResourceBase[T],
        build_args: ContainerModelBuildArgs | None,
        dotenvs: list[DotenvFileResource] | None,
    ) -> dict[str, Input[Any]]:
        build_args = build_args or ContainerModelBuildArgs()
        model = main_service.get_container_model(self.model)

        config: dict[str, Any] = {}
        container_config: dict[str, Any] = {}
        host_config: dict[str, Any] = {}
        network_config: dict[str, Any] = {}

        config["autoRemove"] = self.auto_remove
        config["image"] = model.image.to_image_id(
            main_service.docker_resource_args.image
        )
        config["pull"] = self.pull

        if model.user:
            container_config["user"] = model.user
        entrypoint = (
            self.entrypoint if self.entrypoint is not None else model.build_entrypoint()
        )
        if entrypoint is not None:
            container_config["entrypoint"] = entrypoint
        container_config["labels"] = model.build_labels(
            None,
            main_service.name(),
            build_args,
            main_service.docker_resource_args,
        )
        container_config["env"] = model.build_envs(
            build_args, main_service.docker_resource_args, main_service.args
        ) + (
            sum(
                [
                    ["{key}=${{{key}}}".format(key=key) for key in dotenv.envs.keys()]
                    for dotenv in dotenvs
                ],
                [],
            )
            if dotenvs
            else []
        )

        host_config["binds"] = model.volumes.to_binds(
            model.docker_socket, build_args, main_service.docker_resource_args
        )

        network_args = model.network.to_args(
            None, main_service.docker_resource_args.network, main_service.args
        )
        if network_args.advanced:
            network_config["endpointsConfig"] = {
                network.name: {"aliases": network.aliases}
                for network in network_args.advanced
            }
        elif network_args.mode:
            host_config["networkMode"] = network_args.mode
        if model.capabilities:
            host_config["capAdd"] = model.capabilities
        host_config["readonlyRootfs"] = model.read_only

        mounts = model.build_tmpfs()
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
        if model.init:
            host_config["init"] = model.init

        return config | {
            "container": container_config,
            "host": host_config,
            "network": network_config,
        }
