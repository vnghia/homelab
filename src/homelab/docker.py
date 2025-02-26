from homelab_config import Config
from homelab_docker.resource import DockerResource, DockerResourceArgs
from pulumi import ComponentResource, ResourceOptions

from homelab.service.config import ServiceConfig


class Docker(ComponentResource):
    RESOURCE_NAME = "docker"

    def __init__(self, config: Config[ServiceConfig], project_prefix: str) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, None)
        self.child_opts = ResourceOptions(parent=self)

        self.config = config.docker
        self.resource = DockerResource(
            config.docker,
            opts=self.child_opts,
            project_prefix=project_prefix,
            project_labels=Config.PROJECT_LABELS,
        )

        self.services_config = self.config.services
        self.resource_args = DockerResourceArgs(
            timezone=self.config.timezone,
            config=self.config,
            resource=self.resource,
            project_labels=Config.PROJECT_LABELS,
        )

        self.register_outputs({})
