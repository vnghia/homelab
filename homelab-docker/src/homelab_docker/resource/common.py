from pulumi import ResourceOptions

from homelab_docker import config
from homelab_docker.resource.image import Image as Image
from homelab_docker.resource.network import Network as Network
from homelab_docker.resource.volume import Volume as Volume


class CommonResource:
    def __init__(
        self,
        config: config.Docker,
        *,
        opts: ResourceOptions,
        project_labels: dict[str, str],
    ) -> None:
        self.network = Network(
            config=config.network, opts=opts, project_labels=project_labels
        )
        self.image = Image(config=config.images, opts=opts)
        self.volume = Volume(
            config=config.volumes, opts=opts, project_labels=project_labels
        )
