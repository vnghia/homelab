from __future__ import annotations

import typing
import uuid
from typing import ClassVar, Literal

import pulumi
import pulumi_docker as docker
from homelab_backup.config.volume import BackupVolumeConfig
from homelab_pydantic import AbsolutePath, HomelabBaseModel
from pulumi import ResourceHook, ResourceHookArgs, ResourceHookBinding, ResourceOptions

from ...client import DockerClient

if typing.TYPE_CHECKING:
    from ...resource.host import HostResourceBase
    from ..user import UidGidModel


class LocalVolumeModel(HomelabBaseModel):
    VOLUME_MOUNT: ClassVar[str] = "/mnt/volume"

    active: bool = True
    backup: Literal[False] | BackupVolumeConfig = BackupVolumeConfig()

    bind: AbsolutePath | None = None
    labels: dict[str, str] = {}

    @classmethod
    def get_service(cls, name: str) -> str:
        return name.split("-", maxsplit=1)[0]

    @classmethod
    def change_ownership_hook(
        cls, args: ResourceHookArgs, host_resource: HostResourceBase, user: UidGidModel
    ) -> None:
        outputs = args.new_outputs
        if not outputs:
            raise RuntimeError("This hook can only be called after resource creation")

        volume = outputs["name"]
        pulumi.info("Changing ownership of volume {} to {}".format(volume, user))
        host_resource.docker_client.containers.run(
            image=DockerClient.UTILITY_IMAGE,
            command=["chown", "-R", user.container(), "."],
            detach=False,
            network_mode="none",
            remove=True,
            volumes={volume: {"bind": cls.VOLUME_MOUNT, "mode": "rw"}},
            working_dir=cls.VOLUME_MOUNT,
        )

    def build_resource(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions,
        host_resource: HostResourceBase,
        user: UidGidModel,
        project_labels: dict[str, str],
    ) -> docker.Volume:
        change_ownership_hook = (
            ResourceHook(
                name=uuid.uuid4().hex,
                func=lambda args: self.change_ownership_hook(args, host_resource, user),
            )
            if not self.bind
            else None
        )

        return docker.Volume(
            resource_name,
            opts=ResourceOptions.merge(
                opts,
                ResourceOptions(
                    hooks=ResourceHookBinding(
                        after_create=[change_ownership_hook]
                        if change_ownership_hook
                        else None
                    )
                ),
            ),
            driver="local",
            driver_opts={
                "type": "none",
                "o": "bind",
                "device": self.bind.as_posix(),
            }
            if self.bind
            else None,
            labels=[
                docker.VolumeLabelArgs(label=k, value=v)
                for k, v in (project_labels | self.labels).items()
            ],
        )
