from pathlib import PosixPath

from pulumi import ComponentResource, ResourceOptions

from ...model.container.volume_path import ContainerVolumePath
from ...model.database.postgres import PostgresDatabaseModel
from ..file import FileResource
from ..volume import VolumeResource


class DatabaseGlobalResource(ComponentResource):
    RESOURCE_NAME = "database"

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
            container_volume_resource_path=ContainerVolumePath(
                volume=PostgresDatabaseModel.DATABASE_ENTRYPOINT_INITDB_VOLUME,
                path=PosixPath("add-replication-hba-entry.sh"),
            ).to_resource(volume_resource),
            content="#!/bin/bash\nset -eux\necho 'host replication all all scram-sha-256' >> ${PGDATA}/pg_hba.conf\n",
            mode=0o555,
        )
