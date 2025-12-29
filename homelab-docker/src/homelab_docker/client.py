from contextlib import contextmanager
from pathlib import PosixPath
from typing import Iterator

import docker
from docker.models import containers, images
from docker.models.containers import Container
from homelab_pydantic import AbsolutePath


class DockerClient:
    UTILITY_IMAGE = "busybox"
    VOLUME_CONTAINER_WORKING_DIR = AbsolutePath(PosixPath("/mnt/volume"))

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

    @contextmanager
    def volume_container(
        self, volume: str, command: list[str] | None = None
    ) -> Iterator[Container]:
        container = self.containers.create(
            image=self.UTILITY_IMAGE,
            command=command,
            detach=True,
            network_mode="none",
            volumes={
                volume: {
                    "bind": self.VOLUME_CONTAINER_WORKING_DIR.as_posix(),
                    "mode": "rw",
                }
            },
            working_dir=self.VOLUME_CONTAINER_WORKING_DIR.as_posix(),
        )
        try:
            yield container
        finally:
            container.remove(force=True)
