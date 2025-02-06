from homelab_config import Config
from homelab_docker.config.docker import DockerConfig
from homelab_docker.resource.docker import DockerResource
from pulumi import ComponentResource, ResourceOptions

from .service import Service, ServiceConfig


class Docker(ComponentResource):
    RESOURCE_NAME = "docker"

    def __init__(self, config: DockerConfig[ServiceConfig]) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, None)
        self.child_opts = ResourceOptions(parent=self)

        self.config = config
        self.resource = DockerResource(
            self.config, opts=self.child_opts, project_labels=Config.PROJECT_LABELS
        )
        self.service = Service(
            self.config.services,
            timezone=self.config.timezone,
            docker_resource=self.resource,
            opts=self.child_opts,
        )
        self.register_outputs({})
