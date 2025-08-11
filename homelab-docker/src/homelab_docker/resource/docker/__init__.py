from homelab_global import GlobalArgs
from pulumi import ComponentResource, ResourceOptions

from ...model.host import HostServiceModelModel
from .image import ImageResource
from .network import NetworkResource
from .plugin import PluginResource
from .volume import VolumeResource


class DockerResource(ComponentResource):
    RESOURCE_NAME = "docker"

    def __init__(
        self,
        model: HostServiceModelModel,
        *,
        opts: ResourceOptions,
        global_args: GlobalArgs,
        host: str,
    ) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.host = host

        self.network = NetworkResource(
            config=model.docker.network,
            opts=self.child_opts,
            global_args=global_args,
            host=host,
        )
        self.image = ImageResource(
            config=model.docker,
            opts=self.child_opts,
            global_args=global_args,
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
            global_args=global_args,
            host=self.host,
        )

        self.register_outputs({})
