import pulumi
import pulumi_docker as docker
from pulumi import ComponentResource, ResourceOptions

from homelab_docker.config.image import ImageConfig
from homelab_docker.model.database.postgres import PostgresDatabaseModel


class ImageResource(ComponentResource):
    RESOURCE_NAME = "image"

    def __init__(
        self,
        config: ImageConfig,
        *,
        opts: ResourceOptions,
    ) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.remotes = {
            name: model.build_resource(
                name, opts=self.child_opts, platform=config.platform
            )
            for name, model in config.remote.items()
        }

        for name, versions in config.postgres.items():
            for version, model in versions.items():
                image_name = PostgresDatabaseModel.get_short_name_version(name, version)
                self.remotes[image_name] = model.build_resource(
                    image_name,
                    opts=self.child_opts,
                    platform=config.platform,
                )

        export = {name: image.repo_digest for name, image in self.remotes.items()}
        for name, value in export.items():
            pulumi.export("{}.{}".format(self.RESOURCE_NAME, name), value)
        self.register_outputs(export)

    def __getitem__(self, key: str) -> docker.RemoteImage:
        return self.remotes[key]
