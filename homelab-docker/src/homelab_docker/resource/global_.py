from pulumi import ResourceOptions
from pydantic import BaseModel

from homelab_docker.config.docker import DockerConfig

from .image import ImageResource
from .network import NetworkResource
from .volume import VolumeResource


class GlobalResource:
    def __init__[T: BaseModel](
        self,
        config: DockerConfig[T],
        *,
        opts: ResourceOptions,
        project_labels: dict[str, str],
    ) -> None:
        self.network = NetworkResource(
            config=config.network, opts=opts, project_labels=project_labels
        )
        self.image = ImageResource(config=config.images, opts=opts)
        self.volume = VolumeResource(
            config=config.volumes, opts=opts, project_labels=project_labels
        )
