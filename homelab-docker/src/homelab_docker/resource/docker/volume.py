from __future__ import annotations

import typing
from collections import defaultdict

import pulumi
import pulumi_docker as docker
from homelab_global import ProjectArgs
from pulumi import ComponentResource, ResourceOptions

from ...model.docker.volume import LocalVolumeModel
from ...model.host import HostServiceModelModel

if typing.TYPE_CHECKING:
    from ...resource.file import FileResource
    from ...resource.host import HostResourceBase


class VolumeResource(ComponentResource):
    RESOURCE_NAME = "volume"

    DEFAULT_LOCAL_VOLUME_MODEL = LocalVolumeModel()

    def __init__(
        self,
        config: HostServiceModelModel,
        *,
        opts: ResourceOptions,
        project_args: ProjectArgs,
        host: str,
        host_resource: HostResourceBase,
    ) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.models = config.docker.volumes.local
        self.volumes: dict[str, docker.Volume] = {}

        for volume_name, volume_model in self.models.items():
            if volume_model.active:
                volume_owner = (
                    volume_model.build_owner(host_resource)
                    or host_resource.service_users[
                        LocalVolumeModel.get_service(volume_name)
                    ]
                )

                self.volumes[volume_name] = volume_model.build_resource(
                    volume_name,
                    opts=self.child_opts,
                    host_resource=host_resource,
                    owner=volume_owner,
                    project_labels=project_args.labels,
                )

                if (volume_backup := volume_model.backup) and volume_backup.sqlite:
                    sqlite_backup_volume_name = self.get_sqlite_backup_volume_name(
                        volume_name
                    )
                    self.volumes[sqlite_backup_volume_name] = (
                        volume_model.build_resource(
                            sqlite_backup_volume_name,
                            opts=self.child_opts,
                            host_resource=host_resource,
                            owner=volume_owner,
                            project_labels=project_args.labels,
                        )
                    )

        self.files: defaultdict[str, list[FileResource]] = defaultdict(list)

        for service_name, database in config.databases.items():
            for type_, database_config in database.root.items():
                type_config = config.docker.database.root[type_]
                type_user = type_config.get_user(config.users)
                for name, model in database_config.items():
                    if type_config.dir.initdb:
                        full_initdb_name = type_.get_full_name_initdb(
                            service_name, name
                        )
                        self.volumes[full_initdb_name] = (
                            self.DEFAULT_LOCAL_VOLUME_MODEL.build_resource(
                                full_initdb_name,
                                opts=self.child_opts,
                                host_resource=host_resource,
                                owner=type_user,
                                project_labels=project_args.labels,
                            )
                        )

                    for version in type_config.get_versions(model):
                        full_name = type_.get_full_name_version(
                            service_name, name, version
                        )
                        self.volumes[full_name] = (
                            self.DEFAULT_LOCAL_VOLUME_MODEL.build_resource(
                                full_name,
                                opts=self.child_opts,
                                host_resource=host_resource,
                                owner=type_user,
                                project_labels=project_args.labels,
                            )
                        )

                        if type_config.dir.tmp:
                            full_tmp_name = type_.get_full_name_version_tmp(
                                service_name, name, version
                            )
                            self.volumes[full_tmp_name] = (
                                self.DEFAULT_LOCAL_VOLUME_MODEL.build_resource(
                                    full_tmp_name,
                                    opts=self.child_opts,
                                    host_resource=host_resource,
                                    owner=type_user,
                                    project_labels=project_args.labels,
                                )
                            )

                        if type_config.backup:
                            full_backup_name = type_.get_full_name_version_backup(
                                service_name, name, version
                            )
                            self.volumes[full_backup_name] = (
                                self.DEFAULT_LOCAL_VOLUME_MODEL.build_resource(
                                    full_backup_name,
                                    opts=self.child_opts,
                                    host_resource=host_resource,
                                    owner=type_user,
                                    project_labels=project_args.labels,
                                )
                            )

        export = {name: volume.name for name, volume in self.volumes.items()}
        for name, value in export.items():
            pulumi.export("{}.{}.{}".format(host, self.RESOURCE_NAME, name), value)
        self.register_outputs(export)

    def add_file(self, file: FileResource) -> None:
        self.files[file.volume_path.volume].append(file)

    def get_sqlite_backup_volume_name(self, volume_name: str) -> str:
        return "{}-sqlite-backup".format(volume_name)

    def __getitem__(self, key: str) -> docker.Volume:
        return self.volumes[key]
