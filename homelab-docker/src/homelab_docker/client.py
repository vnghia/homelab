import docker
from docker.models import containers, images


class DockerClient:
    UTILITY_IMAGE = "busybox"

    def __init__(self, base_url: str) -> None:
        self.client = docker.DockerClient(base_url)

    @property
    def images(self) -> images.ImageCollection:
        return self.client.images

    def pull_utility_image(self) -> None:
        self.images.pull(repository=self.UTILITY_IMAGE)

    @property
    def containers(self) -> containers.ContainerCollection:
        return self.client.containers
