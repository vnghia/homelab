from homelab_pydantic import HomelabBaseModel


class DockerProcessCreationModel(HomelabBaseModel):
    service: str
    container: str | None = None
    command: list[str] | None = None
    entrypoint: list[str] | None = None


class DockerContainerCreationModel(DockerProcessCreationModel):
    name: str | None = None
