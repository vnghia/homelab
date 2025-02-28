import pulumi
import pulumi_docker as docker
from pulumi import ComponentResource, ResourceOptions

from homelab_docker.config.service import ServiceConfigBase
from homelab_docker.model.volume import LocalVolumeModel

from ..config import DockerConfig


class VolumeResource(ComponentResource):
    RESOURCE_NAME = "volume"

    def __init__[T: ServiceConfigBase](
        self,
        config: DockerConfig[T],
        *,
        opts: ResourceOptions,
        project_labels: dict[str, str],
    ) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.volumes = {
            name: model.build_resource(
                name, opts=self.child_opts, project_labels=project_labels
            )
            for name, model in config.volumes.local.items()
        }

        for service_name, database in config.services.databases.items():
            for type_, database_config in database.root.items():
                for name, model in database_config.items():
                    type_config = config.database.root[type_]
                    for version in type_config.get_versions(model):
                        full_name = type_.get_full_name_version(
                            service_name, name, version
                        )
                        self.volumes[full_name] = LocalVolumeModel().build_resource(
                            full_name,
                            opts=self.child_opts,
                            project_labels=project_labels,
                        )

                        if type_config.tmp_dir:
                            full_tmp_name = type_.get_full_name_version_tmp(
                                service_name, name, version
                            )
                            self.volumes[full_tmp_name] = (
                                LocalVolumeModel().build_resource(
                                    full_tmp_name,
                                    opts=self.child_opts,
                                    project_labels=project_labels,
                                )
                            )

        export = {name: volume.name for name, volume in self.volumes.items()}
        for name, value in export.items():
            pulumi.export("{}.{}".format(self.RESOURCE_NAME, name), value)
        self.register_outputs(export)

    def __getitem__(self, key: str) -> docker.Volume:
        return self.volumes[key]
