import dataclasses

from homelab_network.model.hostname import Hostnames
from pulumi import ResourceOptions
from pydantic_extra_types.timezone_name import TimeZoneName

from ..config import DockerConfig, DockerNoServiceConfig
from ..config.service import ServiceConfigBase
from ..model.service import ServiceModel
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
        host: str,
    ) -> None:
        self.config = config
        self.host = host

        self.network = NetworkResource(
            config=config.network, opts=opts, project_labels=project_labels, host=host
        )
        self.image = ImageResource(
            config=config,
            opts=opts,
            platform=config.platform,
            project_prefix=project_prefix,
            project_labels=project_labels,
            host=self.host,
        )
        self.plugin = PluginResource(
            config=config.plugins, opts=opts, host=self.host, platform=config.platform
        )
        self.volume = VolumeResource(
            config=config, opts=opts, project_labels=project_labels, host=self.host
        )


@dataclasses.dataclass
class DockerResourceArgs:
    timezone: TimeZoneName
    resource: DockerResource
    models: dict[str, ServiceModel]
    project_labels: dict[str, str]
    hostnames: Hostnames = dataclasses.field(default_factory=Hostnames)

    @property
    def config(self) -> DockerNoServiceConfig:
        return self.resource.config

    @property
    def host(self) -> str:
        return self.resource.host

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
