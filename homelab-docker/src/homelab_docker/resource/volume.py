import pulumi
import pulumi_docker as docker
from pulumi import ComponentResource, ResourceOptions

from homelab_docker import config


class Volume(ComponentResource):
    RESOURCE_NAME = "volume"

    def __init__(
        self,
        config: config.Volume,
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
            for name, model in config.local.items()
        }

        export = {name: volume.name for name, volume in self.volumes.items()}
        pulumi.export(self.RESOURCE_NAME, export)
        self.register_outputs(export)

    def __getitem__(self, key: str) -> docker.Volume:
        return self.volumes[key]
