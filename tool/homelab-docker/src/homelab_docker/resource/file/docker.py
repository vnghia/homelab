from typing import Any

from homelab_pydantic import docker as schema
from pulumi import Output, ResourceOptions

from ...extract import ExtractorArgs
from ...model.docker.container.volume_path import ContainerVolumePath
from ...model.file import FilePermissionModel
from ...model.user import UidGidModel
from .config import ConfigFileResource, JsonDumper


class DockerContainerCreationModelResource(
    ConfigFileResource[schema.ContainerCreationModel],
    module="docker",
    name="ContainerCreation",
):
    validator = schema.ContainerCreationModel
    dumper = JsonDumper[schema.ContainerCreationModel]

    def __init__(
        self,
        container: str | None,
        *,
        opts: ResourceOptions,
        volume_path: ContainerVolumePath,
        permission: UidGidModel | FilePermissionModel,
        extractor_args: ExtractorArgs,
    ) -> None:
        service = extractor_args.service
        model = service.model[container].to_full(extractor_args)

        build_args = model.build_args(service.options[container], extractor_args)
        user = model.build_user(extractor_args)

        config: dict[str, Any] = {}
        host_config: dict[str, Any] = {}
        network_config: dict[str, Any] = {}

        config["Image"] = model.image.to_image_name(extractor_args.host.docker.image)
        config["User"] = model.build_container_user(user)
        config["Entrypoint"] = model.build_entrypoint(extractor_args)
        config["Cmd"] = model.build_command(extractor_args)
        config["Labels"] = model.build_labels(
            service.container_full_names[container],
            extractor_args,
            build_args,
        )
        config["Env"] = model.build_envs(extractor_args, build_args)

        host_config["Mounts"] = [
            {
                "Target": mount_arg.target,
                "Source": mount_arg.source,
                "Type": mount_arg.type,
                "ReadOnly": mount_arg.read_only,
                "BindOptions": Output.from_input(mount_arg.bind_options).apply(
                    lambda options: {"Propagation": options.propagation}
                )
                if mount_arg.bind_options
                else None,
                "VolumeOptions": Output.from_input(mount_arg.volume_options).apply(
                    lambda options: {
                        "NoCopy": options.no_copy,
                        "DriverConfig": options.driver_options,
                        "Subpath": options.subpath,
                    }
                )
                if mount_arg.volume_options
                else None,
                "TmpfsOptions": Output.from_input(mount_arg.tmpfs_options).apply(
                    lambda options: {
                        "Mode": options.mode,
                        "SizeBytes": options.size_bytes,
                    }
                )
                if mount_arg.tmpfs_options
                else None,
            }
            for mount_arg in model.volumes.to_args(
                model.docker_socket, extractor_args, build_args
            )
        ]

        network_args = model.network.to_args(None, extractor_args, build_args)
        if network_args.advanced:
            network_config["EndpointsConfig"] = {
                network.name: {"Aliases": network.aliases}
                for network in network_args.advanced
            }
        elif network_args.mode:
            host_config["NetworkMode"] = network_args.mode

        if cap := model.build_cap():
            if cap.adds:
                host_config["CapAdd"] = cap.adds
            if cap.drops:
                host_config["CapDrop"] = cap.drops

        host_config["ReadonlyRootfs"] = model.read_only
        host_config["SecurityOpt"] = model.security_opts

        if tmpfses := model.build_tmpfs(user):
            host_config["Tmpfs"] = tmpfses
        if model.init:
            host_config["Init"] = model.init

        if group_adds := model.build_group_adds(extractor_args, user):
            host_config["GroupAdd"] = group_adds

        config["HostConfig"] = host_config
        config["NetworkingConfig"] = network_config

        super().__init__(
            service.add_service_name(container),
            opts=opts,
            volume_path=volume_path,
            data=config,
            permission=permission,
            extractor_args=extractor_args,
        )
