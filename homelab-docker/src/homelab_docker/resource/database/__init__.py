from pathlib import PosixPath

from homelab_pydantic import RelativePath
from pulumi import ComponentResource, ResourceOptions

from ...model.container.volume_path import ContainerVolumePath
from ..file import FileResource
from ..volume import VolumeResource


class DatabaseResource(ComponentResource):
    RESOURCE_NAME = "database"

    POSTGRES_DOCKER_ENTRYPOINT_INITDB_VOLUME = "postgres-docker-entrypoint-initdb"

    def __init__(
        self,
        *,
        opts: ResourceOptions | None,
        volume_resource: VolumeResource,
    ) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        FileResource(
            "replication",
            opts=self.child_opts,
            volume_path=ContainerVolumePath(
                volume=self.POSTGRES_DOCKER_ENTRYPOINT_INITDB_VOLUME,
                path=RelativePath(PosixPath("add-replication-hba-entry.sh")),
            ),
            content="#!/bin/bash\nset -eux\necho 'host replication all all scram-sha-256' >> ${PGDATA}/pg_hba.conf\n",
            mode=0o555,
            volume_resource=volume_resource,
        )
