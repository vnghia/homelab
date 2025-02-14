import docker
from docker.models import containers, images


class DockerClient:
    @classmethod
    def init_client(cls) -> docker.DockerClient:
        return docker.from_env()

    def __init__(self) -> None:
        self.client = self.init_client()

    @property
    def images(self) -> images.ImageCollection:
        return self.client.images

    @property
    def containers(self) -> containers.ContainerCollection:
        return self.client.containers
