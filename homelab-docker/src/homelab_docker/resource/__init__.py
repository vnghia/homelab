import dataclasses

import pulumi_docker as docker


@dataclasses.dataclass
class Resource:
    networks: dict[str, docker.Network]
    images: dict[str, docker.RemoteImage]
    volumes: dict[str, docker.Volume]
    containers: dict[str, docker.Container]
