from homelab_config import Config
from homelab_docker.resource.docker import DockerResource
from pulumi import ComponentResource, ResourceOptions

from .service import Service, ServiceConfig


class Docker(ComponentResource):
    RESOURCE_NAME = "docker"

    def __init__(self, config: Config[ServiceConfig]) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, None)
        self.child_opts = ResourceOptions(parent=self)

        self.config = config
        self.resource = DockerResource(
            self.config.docker,
            opts=self.child_opts,
            project_labels=Config.PROJECT_LABELS,
        )
        self.service = Service(
            self.config,
            timezone=self.config.docker.timezone,
            docker_resource=self.resource,
            opts=self.child_opts,
        )
        self.register_outputs({})
