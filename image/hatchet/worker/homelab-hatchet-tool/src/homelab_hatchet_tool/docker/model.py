from homelab_pydantic import HomelabBaseModel


class DockerProcessCreationModel(HomelabBaseModel):
    service: str
    model: str | None = None


class DockerContainerCreationModel(DockerProcessCreationModel):
    pass
