from homelab_pydantic import HomelabBaseModel


class GlobalExtractDockerSource(HomelabBaseModel):
    docker: str
