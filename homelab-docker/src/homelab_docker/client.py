import docker
from docker.models import containers, images


class DockerClient:
    def __init__(self, base_url: str) -> None:
        self.client = docker.DockerClient(base_url)

    @property
    def images(self) -> images.ImageCollection:
        return self.client.images

    @property
    def containers(self) -> containers.ContainerCollection:
        return self.client.containers
