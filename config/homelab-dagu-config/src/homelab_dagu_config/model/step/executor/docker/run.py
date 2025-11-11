from typing import Any

from homelab_docker.extract import ExtractorArgs
from homelab_docker.resource.file.dotenv import DotenvFileResource
from homelab_pydantic import HomelabBaseModel
from pulumi import Input


class DaguDagStepDockerRunExecutorModel(HomelabBaseModel):
    model: str | None
    auto_remove: bool = True
    pull: bool = False

    entrypoint: list[str] | None = None

    def to_executor_config(
        self,
        extractor_args: ExtractorArgs,
        dotenvs: list[DotenvFileResource] | None,
    ) -> dict[str, Input[Any]]:
        service = extractor_args.service
        model = service.model[self.model].to_full(extractor_args)

        build_args = model.build_args(service.options[self.model], extractor_args)
        config: dict[str, Any] = {}
        container_config: dict[str, Any] = {}
        host_config: dict[str, Any] = {}
        network_config: dict[str, Any] = {}

        config["autoRemove"] = self.auto_remove
        config["image"] = model.image.to_image_name(extractor_args.host.docker.image)
        config["pull"] = self.pull

        if model.user:
            container_config["user"] = model.user
        entrypoint = (
            self.entrypoint
            if self.entrypoint is not None
            else model.build_entrypoint(extractor_args)
        )
        if entrypoint is not None:
            container_config["entrypoint"] = entrypoint
        container_config["labels"] = model.build_labels(
            None, extractor_args, build_args
        )
        container_config["env"] = model.build_envs(extractor_args, build_args) + (
            sorted(
                [
                    "{key}=${{{key}}}".format(key=key)
                    for dotenv in dotenvs
                    for key in dotenv.envs
                ]
            )
            if dotenvs
            else []
        )

        host_config["binds"] = model.volumes.to_binds(
            model.docker_socket, extractor_args, build_args
        )

        network_args = model.network.to_args(None, extractor_args, build_args)
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
