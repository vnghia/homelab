import docker
from docker.models import containers, images


class DockerClient:
    @classmethod
    def init_client(cls) -> docker.DockerClient:
        # TODO: use paramiko after https://github.com/tailscale/tailscale/issues/14922
        return docker.from_env(use_ssh_client=True)

    def __init__(self) -> None:
        self.client = self.init_client()

    @property
    def images(self) -> images.ImageCollection:
        return self.client.images

    @property
    def containers(self) -> containers.ContainerCollection:
        return self.client.containers
