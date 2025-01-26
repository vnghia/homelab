from homelab.docker import Docker


class Homelab:
    def __init__(self) -> None:
        self.docker = Docker()
