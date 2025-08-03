import functools
import operator
from typing import Any

from homelab_docker.resource.file.dotenv import DotenvFileResource
from homelab_docker.resource.service import ServiceResourceBase
from homelab_pydantic import HomelabBaseModel
from pulumi import Input


class DaguDagStepDockerRunExecutorModel(HomelabBaseModel):
    model: str | None
    auto_remove: bool = True
    pull: bool = False

    entrypoint: list[str] | None = None

    def to_executor_config(
        self,
        main_service: ServiceResourceBase,
        dotenvs: list[DotenvFileResource] | None,
    ) -> dict[str, Input[Any]]:
        model = main_service.model[self.model].to_full(main_service)

        build_args = main_service.options[self.model]
        config: dict[str, Any] = {}
        container_config: dict[str, Any] = {}
        host_config: dict[str, Any] = {}
        network_config: dict[str, Any] = {}

        config["autoRemove"] = self.auto_remove
        config["image"] = model.image.to_image_name(
            main_service.docker_resource_args.image
        )
        config["pull"] = self.pull

        if model.user:
            container_config["user"] = model.user
        entrypoint = (
            self.entrypoint
            if self.entrypoint is not None
            else model.build_entrypoint(main_service)
        )
        if entrypoint is not None:
            container_config["entrypoint"] = entrypoint
        container_config["labels"] = model.build_labels(None, main_service, build_args)
        container_config["env"] = model.build_envs(main_service, build_args) + (
            sorted(
                functools.reduce(
                    operator.iadd,
                    [
                        ["{key}=${{{key}}}".format(key=key) for key in dotenv.envs]
                        for dotenv in dotenvs
                    ],
                    [],
                )
            )
            if dotenvs
            else []
        )

        host_config["binds"] = model.volumes.to_binds(
            model.docker_socket, main_service, model, build_args
        )

        network_args = model.network.to_args(None, main_service, build_args)
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

        tmpfses = model.build_tmpfs()
        if tmpfses:
            host_config["tmpfs"] = tmpfses
        if model.init:
            host_config["init"] = model.init

        return config | {
            "container": container_config,
            "host": host_config,
            "network": network_config,
        }
