from homelab_pydantic import HomelabBaseModel


class ContainerExtractEnvSource(HomelabBaseModel):
    env: str
