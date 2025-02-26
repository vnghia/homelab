import dataclasses

from pulumi import ResourceOptions
from pydantic_extra_types.timezone_name import TimeZoneName

from ..config import DockerConfig, DockerNoServiceConfig
from ..config.service import ServiceConfigBase
from .image import ImageResource
from .network import NetworkResource
from .plugin import PluginResource
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
            config=config,
            opts=opts,
            platform=config.platform,
            project_prefix=project_prefix,
            project_labels=project_labels,
        )
        self.plugin = PluginResource(
            config=config.plugins, opts=opts, platform=config.platform
        )
        self.volume = VolumeResource(
            config=config, opts=opts, project_labels=project_labels
        )


@dataclasses.dataclass
class DockerResourceArgs:
    timezone: TimeZoneName
    config: DockerNoServiceConfig
    resource: DockerResource
    project_labels: dict[str, str]

    @property
    def network(self) -> NetworkResource:
        return self.resource.network

    @property
    def image(self) -> ImageResource:
        return self.resource.image

    @property
    def plugin(self) -> PluginResource:
        return self.resource.plugin

    @property
    def volume(self) -> VolumeResource:
        return self.resource.volume
