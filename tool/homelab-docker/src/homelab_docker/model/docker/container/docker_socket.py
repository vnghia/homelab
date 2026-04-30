from homelab_pydantic import HomelabBaseModel


class ContainerDockerSocketConfig(HomelabBaseModel):
    write: bool
