import docker
from docker.models import containers, images
from paramiko import BadAuthenticationType


class DockerClient:
    @classmethod
    def init_client(cls) -> docker.DockerClient:
        try:
            return docker.from_env()
        except BadAuthenticationType:
            # TODO: use paramiko again if it works with Tailscale
            return docker.from_env(use_ssh_client=True)

    def __init__(self) -> None:
        self.client = self.init_client()

    @property
    def images(self) -> images.ImageCollection:
        return self.client.images

    @property
    def containers(self) -> containers.ContainerCollection:
        return self.client.containers
