from typing import Literal

import pulumi_docker as docker
from homelab_backup.config.volume import BackupVolumeConfig
from homelab_pydantic import AbsolutePath, HomelabBaseModel
from pulumi import ResourceOptions


class LocalVolumeModel(HomelabBaseModel):
    backup: Literal[False] | BackupVolumeConfig = BackupVolumeConfig()

    bind: AbsolutePath | None = None
    labels: dict[str, str] = {}

    @classmethod
    def get_service(cls, name: str) -> str:
        return name.split("-", maxsplit=1)[0]

    def build_resource(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions,
        project_labels: dict[str, str],
    ) -> docker.Volume:
        return docker.Volume(
            resource_name,
            opts=opts,
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
