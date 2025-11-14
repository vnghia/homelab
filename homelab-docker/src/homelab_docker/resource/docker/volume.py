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
    ) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.volumes = {
            name: model.build_resource(
                name, opts=self.child_opts, project_labels=project_args.labels
            )
            for name, model in config.docker.volumes.local.items()
            if model.active
        }
        self.files: defaultdict[str, list[FileResource]] = defaultdict(list)

        for service_name, database in config.databases.items():
            for type_, database_config in database.root.items():
                type_config = config.docker.database.root[type_]
                for name, model in database_config.items():
                    if type_config.dir.initdb:
                        full_initdb_name = type_.get_full_name_initdb(
                            service_name, name
                        )
                        self.volumes[full_initdb_name] = (
                            self.DEFAULT_LOCAL_VOLUME_MODEL.build_resource(
                                full_initdb_name,
                                opts=self.child_opts,
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
                                    project_labels=project_args.labels,
                                )
                            )

        export = {name: volume.name for name, volume in self.volumes.items()}
        for name, value in export.items():
            pulumi.export("{}.{}.{}".format(host, self.RESOURCE_NAME, name), value)
        self.register_outputs(export)

    def add_file(self, file: FileResource) -> None:
        self.files[file.volume_path.volume].append(file)

    def __getitem__(self, key: str) -> docker.Volume:
        return self.volumes[key]
