import homelab_docker as docker


class Docker:
    def __init__(self) -> None:
        self.bridge_network = docker.network.Bridge(name="bridge").build_resource()
