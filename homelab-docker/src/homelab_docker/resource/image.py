import pulumi
from pulumi import ComponentResource, ResourceOptions

from homelab_docker.config.image import ImageConfig
from homelab_docker.model.build.model import BuildModel
from homelab_docker.model.database.postgres import PostgresDatabaseModel


class ImageResource(ComponentResource):
    RESOURCE_NAME = "image"

    def __init__(
        self,
        config: ImageConfig,
        *,
        opts: ResourceOptions,
        project_prefix: str,
        project_labels: dict[str, str],
    ) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.remotes = {
            name: model.build_resource(
                name, opts=self.child_opts, platform=config.platform
            )
            for name, model in config.remote.items()
        }

        self.builds = {
            name: model.build_resource(
                name,
                opts=self.child_opts,
                remote_images=self.remotes,
                project_prefix=project_prefix,
                project_labels=project_labels,
            )
            for name, model in config.build.items()
        }

        for name, versions in config.postgres.items():
            for version, model in versions.items():
                image_name = PostgresDatabaseModel.get_short_name_version(name, version)
                self.remotes[image_name] = model.build_resource(
                    image_name,
                    opts=self.child_opts,
                    platform=config.platform,
                )

        export = {name: image.image_id for name, image in self.remotes.items()} | {
            name: image.ref for name, image in self.builds.items()
        }
        for name, value in export.items():
            pulumi.export("{}.{}".format(self.RESOURCE_NAME, name), value)
        self.register_outputs(export)
