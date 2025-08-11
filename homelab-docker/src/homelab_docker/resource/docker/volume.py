import pulumi
import pulumi_docker as docker
from homelab_global import GlobalArgs
from pulumi import ComponentResource, ResourceOptions

from ...model.docker.volume import LocalVolumeModel
from ...model.host import HostServiceModelModel


class VolumeResource(ComponentResource):
    RESOURCE_NAME = "volume"

    def __init__(
        self,
        config: HostServiceModelModel,
        *,
        opts: ResourceOptions,
        global_args: GlobalArgs,
        host: str,
    ) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.volumes = {
            name: model.build_resource(
                name, opts=self.child_opts, project_labels=global_args.project.labels
            )
            for name, model in config.docker.volumes.local.items()
        }

        for service_name, database in config.databases.items():
            for type_, database_config in database.root.items():
                for name, model in database_config.items():
                    type_config = config.docker.database.root[type_]

                    if type_config.initdb_dir:
                        full_initdb_name = type_.get_full_name_initdb(
                            service_name, name
                        )
                        self.volumes[full_initdb_name] = (
                            LocalVolumeModel().build_resource(
                                full_initdb_name,
                                opts=self.child_opts,
                                project_labels=global_args.project.labels,
                            )
                        )

                    for version in type_config.get_versions(model):
                        full_name = type_.get_full_name_version(
                            service_name, name, version
                        )
                        self.volumes[full_name] = LocalVolumeModel().build_resource(
                            full_name,
                            opts=self.child_opts,
                            project_labels=global_args.project.labels,
                        )

                        if type_config.tmp_dir:
                            full_tmp_name = type_.get_full_name_version_tmp(
                                service_name, name, version
                            )
                            self.volumes[full_tmp_name] = (
                                LocalVolumeModel().build_resource(
                                    full_tmp_name,
                                    opts=self.child_opts,
                                    project_labels=global_args.project.labels,
                                )
                            )

        export = {name: volume.name for name, volume in self.volumes.items()}
        for name, value in export.items():
            pulumi.export("{}.{}.{}".format(host, self.RESOURCE_NAME, name), value)
        self.register_outputs(export)

    def __getitem__(self, key: str) -> docker.Volume:
        return self.volumes[key]
