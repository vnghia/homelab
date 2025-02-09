from pulumi import ResourceOptions

from homelab_docker.config.docker import DockerConfig
from homelab_docker.config.service import ServiceConfigBase

from .image import ImageResource
from .network import NetworkResource
from .volume import VolumeResource


class DockerResource:
    def __init__[T: ServiceConfigBase](
        self,
        config: DockerConfig[T],
        *,
        opts: ResourceOptions,
        project_prefix: str,
        project_labels: dict[str, str],
    ) -> None:
        self.network = NetworkResource(
            config=config.network, opts=opts, project_labels=project_labels
        )
        self.image = ImageResource(
            config=config.images,
            opts=opts,
            project_prefix=project_prefix,
            project_labels=project_labels,
        )
        self.volume = VolumeResource(
            config=config, opts=opts, project_labels=project_labels
        )
