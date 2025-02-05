from pulumi import ResourceOptions

from homelab_docker.config.docker import Docker as DockerConfig
from homelab_docker.resource.image import Image
from homelab_docker.resource.network import Network
from homelab_docker.resource.volume import Volume


class Global:
    def __init__[T](
        self,
        config: DockerConfig[T],
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
