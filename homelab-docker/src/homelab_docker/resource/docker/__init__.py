from pulumi import ComponentResource, ResourceOptions

from ...extract import ExtractorArgs
from .image import ImageResource
from .network import NetworkResource
from .plugin import PluginResource
from .volume import VolumeResource


class DockerResource(ComponentResource):
    RESOURCE_NAME = "docker"

    def __init__(
        self,
        host: str,
        *,
        opts: ResourceOptions,
        extractor_args: ExtractorArgs,
    ) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        model = extractor_args.host_model
        self.host = host
        self.host_resource = extractor_args.host

        self.network = NetworkResource(
            config=model,
            opts=self.child_opts,
            project_args=extractor_args.global_resource.project_args,
            host=host,
            extractor_args=extractor_args,
        )
        self.image = ImageResource(
            config=model.docker,
            opts=self.child_opts,
            project_args=extractor_args.global_resource.project_args,
            host=self.host,
        )
        self.plugin = PluginResource(
            config=model.docker,
            opts=self.child_opts,
            host=self.host,
        )
        self.volume = VolumeResource(
            config=model,
            opts=self.child_opts,
            project_args=extractor_args.global_resource.project_args,
            host=self.host,
            host_resource=self.host_resource,
        )

        self.register_outputs({})
