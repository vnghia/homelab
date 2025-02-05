from homelab_config import Config, config
from homelab_docker.config.docker import Docker as DockerConfig
from homelab_docker.resource.global_ import Global as GlobalResource
from pulumi import ComponentResource, ResourceOptions

from homelab.docker.resource import Resource
from homelab.docker.service import Service

from .service import ServiceConfig, ServiceTest


class Docker(ComponentResource):
    RESOURCE_NAME = "docker"

    def __init__(self) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, None)
        self.child_opts = ResourceOptions(parent=self)

        self.resource = Resource(opts=self.child_opts)
        self.service = Service(resource=self.resource, opts=self.child_opts)

        self.register_outputs({})


class DockerTest(ComponentResource):
    RESOURCE_NAME = "docker-test"

    def __init__(self) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, None)
        self.child_opts = ResourceOptions(parent=self)

        self.config = Config.build_key(DockerConfig[ServiceConfig], "docker-test")
        self.global_resource = GlobalResource(
            self.config, opts=self.child_opts, project_labels=config.PROJECT_LABELS
        )
        self.service = ServiceTest(
            self.config.services,
            timezone=self.config.timezone,
            global_resource=self.global_resource,
            opts=self.child_opts,
        )
        self.register_outputs({})
