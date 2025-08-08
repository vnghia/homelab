import dataclasses

from homelab_network.model.hostname import Hostnames
from pulumi import ComponentResource, ResourceOptions
from pydantic_extra_types.timezone_name import TimeZoneName

from ..config import DockerServiceModelConfig, DockerServiceModelConfigs
from ..model.service import ServiceModel
from .image import ImageResource
from .network import NetworkResource
from .plugin import PluginResource
from .volume import VolumeResource


class DockerResource(ComponentResource):
    RESOURCE_NAME = "docker"

    def __init__(
        self,
        config: DockerServiceModelConfig,
        *,
        opts: ResourceOptions,
        project_prefix: str,
        project_labels: dict[str, str],
        host: str,
    ) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.project_prefix = project_prefix
        self.project_labels = project_labels
        self.host = host

        self.network = NetworkResource(
            config=config.network,
            opts=self.child_opts,
            project_labels=project_labels,
            host=host,
        )
        self.image = ImageResource(
            config=config,
            opts=self.child_opts,
            platform=config.host.platform,
            project_prefix=project_prefix,
            project_labels=project_labels,
            host=self.host,
        )
        self.plugin = PluginResource(
            config=config.plugins,
            opts=self.child_opts,
            host=self.host,
            platform=config.host.platform,
        )
        self.volume = VolumeResource(
            config=config,
            opts=self.child_opts,
            project_labels=project_labels,
            host=self.host,
        )

        self.register_outputs({})


@dataclasses.dataclass
class DockerResourceArgs:
    resource: DockerResource
    models: dict[str, ServiceModel]
    hostnames: Hostnames
    configs: DockerServiceModelConfigs

    @property
    def host(self) -> str:
        return self.resource.host

    @property
    def config(self) -> DockerServiceModelConfig:
        return self.configs[self.host]

    @property
    def timezone(self) -> TimeZoneName:
        return self.configs[self.host].host.timezone

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

    @property
    def project_labels(self) -> dict[str, str]:
        return self.resource.project_labels
