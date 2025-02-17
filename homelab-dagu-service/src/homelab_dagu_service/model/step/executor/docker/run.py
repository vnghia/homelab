from typing import Any

from homelab_docker.model.container import ContainerModelBuildArgs
from homelab_docker.resource.file.dotenv import DotenvFileResource
from homelab_docker.resource.service import ServiceResourceBase
from pulumi import Input, Output
from pydantic import BaseModel


class DaguDagStepDockerRunExecutorModel(BaseModel):
    model: str | None
    auto_remove: bool = True
    pull: bool = False

    def to_executor_config[T](
        self,
        main_service: ServiceResourceBase[T],
        build_args: ContainerModelBuildArgs | None,
        dotenv: DotenvFileResource | None,
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

        container_config["user"] = model.user
        container_config["entrypoint"] = model.build_entrypoint()
        container_config["labels"] = model.build_labels(
            None,
            main_service.name(),
            build_args,
            main_service.docker_resource_args,
        )
        container_config["env"] = model.build_envs(
            build_args, main_service.docker_resource_args, main_service.args
        ) + (
            ["{key}=${{{key}}}".format(key=key) for key in dotenv.data.keys()]
            if dotenv
            else []
        )

        host_config["binds"] = model.volumes.to_binds(
            main_service.docker_resource_args.volume
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
        host_config["init"] = model.init

        return config | {
            "container": container_config,
            "host": host_config,
            "network": network_config,
        }
