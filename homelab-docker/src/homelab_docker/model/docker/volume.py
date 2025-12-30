from __future__ import annotations

import dataclasses
import typing
import uuid
from typing import Literal

import pulumi
import pulumi_docker as docker
from homelab_backup.config.volume import BackupVolumeConfig
from homelab_backup.model.sqlite import BackupSqliteModel
from homelab_pydantic import AbsolutePath, HomelabBaseModel, RelativePath
from pulumi import ResourceHook, ResourceHookArgs, ResourceHookBinding, ResourceOptions

from ..user import UidGidModel

if typing.TYPE_CHECKING:
    from ...resource.host import HostResourceBase


@dataclasses.dataclass
class LocalVolumeResource:
    name: str
    service: str
    model: LocalVolumeModel
    resource: docker.Volume


@dataclasses.dataclass
class LocalSqliteBackupVolumeArgs:
    volume: LocalVolumeResource
    backup: BackupSqliteModel
    dbs: list[RelativePath]


class LocalVolumeModel(HomelabBaseModel):
    active: bool = True
    backup: Literal[False] | BackupVolumeConfig = BackupVolumeConfig()

    bind: AbsolutePath | None = None
    labels: dict[str, str] = {}

    owner: str | UidGidModel | None = None

    @classmethod
    def get_service(cls, name: str) -> str:
        return name.split("-", maxsplit=1)[0]

    @classmethod
    def change_ownership_hook(
        cls, args: ResourceHookArgs, host_resource: HostResourceBase, owner: UidGidModel
    ) -> None:
        outputs = args.new_outputs
        if not outputs:
            raise RuntimeError("This hook can only be called after resource creation")

        volume = outputs["name"]
        pulumi.info("Changing ownership of volume {} to {}".format(volume, owner))
        with host_resource.docker_client.volume_container(
            volume, command=["chown", "-R", owner.container(), "."]
        ) as _container:
            pass

    def build_owner(self, host_resource: HostResourceBase) -> UidGidModel | None:
        if isinstance(self.owner, UidGidModel):
            return self.owner
        if isinstance(self.owner, str):
            return host_resource.model.users[self.owner]
        return None

    def build_resource(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions,
        host_resource: HostResourceBase,
        owner: UidGidModel | None,
        project_labels: dict[str, str],
    ) -> LocalVolumeResource:
        service = self.get_service(resource_name)
        owner = (
            owner
            or self.build_owner(host_resource)
            or host_resource.service_users[service]
        )

        change_ownership_hook = (
            ResourceHook(
                name=uuid.uuid4().hex,
                func=lambda args: self.change_ownership_hook(
                    args, host_resource, owner
                ),
            )
            if not self.bind
            else None
        )

        return LocalVolumeResource(
            name=resource_name,
            service=service,
            model=self,
            resource=docker.Volume(
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
            ),
        )
