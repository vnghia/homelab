import pulumi
from homelab_global import ProjectArgs
from pulumi import ComponentResource, ResourceOptions

from ...config.docker import DockerConfig


class ImageResource(ComponentResource):
    RESOURCE_NAME = "image"

    def __init__(
        self,
        config: DockerConfig,
        *,
        opts: ResourceOptions,
        project_args: ProjectArgs,
        host: str,
    ) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.remotes = {
            name: model.build_resource(name, opts=self.child_opts, config=config)
            for name, model in config.images.remote.items()
        }

        self.builds = {
            name: model.build_resource(
                name,
                opts=self.child_opts,
                remote_images=self.remotes,
                project_prefix=project_args.prefix,
                project_labels=project_args.labels,
            )
            for name, model in config.images.build.items()
        }

        for type_, database in config.database.root.items():
            for name, versions in database.images.items():
                for version, model in versions.items():
                    image_name = type_.get_short_name_version(name, version)
                    self.remotes[image_name] = model.build_resource(
                        image_name, opts=self.child_opts, config=config
                    )

        export = {name: image.image_id for name, image in self.remotes.items()} | {
            name: image.ref for name, image in self.builds.items()
        }
        for name, value in export.items():
            pulumi.export("{}.{}.{}".format(host, self.RESOURCE_NAME, name), value)
        self.register_outputs(export)
