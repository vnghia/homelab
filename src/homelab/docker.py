from homelab_config import Config
from homelab_docker.config import DockerConfig
from homelab_docker.config.service import ServiceConfigBase
from homelab_docker.resource import DockerResource, DockerResourceArgs
from homelab_network.model.hostname import Hostnames
from pulumi import ComponentResource, ResourceOptions


class Docker[T: ServiceConfigBase](ComponentResource):
    RESOURCE_NAME = "docker"

    def __init__(
        self,
        config: DockerConfig[T],
        *,
        opts: ResourceOptions,
        project_prefix: str,
        host: str,
        hostnames: Hostnames,
    ) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.config = config
        self.resource = DockerResource(
            self.config,
            opts=self.child_opts,
            project_prefix=project_prefix,
            project_labels=Config.PROJECT_LABELS,
            host=host,
        )

        self.services_config = self.config.services
        self.resource_args = DockerResourceArgs(
            timezone=self.config.timezone,
            resource=self.resource,
            models=self.config.services.services,
            project_labels=Config.PROJECT_LABELS,
            hostnames=hostnames,
        )

        self.register_outputs({})
