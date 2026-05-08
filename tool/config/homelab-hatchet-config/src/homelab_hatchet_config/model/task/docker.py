from homelab_docker.model.file.docker import (
    DockerContainerCreationModel,
    DockerProcessCreationModel,
)
from homelab_pydantic import HomelabBaseModel

from .base import HatchetTaskBaseModel


class HatchetTaskDockerExecModel(HomelabBaseModel):
    exec: DockerProcessCreationModel = DockerProcessCreationModel()


class HatchetTaskDockerRunModel(HomelabBaseModel):
    run: DockerContainerCreationModel = DockerContainerCreationModel()


class HatchetTaskDockerModel(HatchetTaskBaseModel):
    docker: HatchetTaskDockerExecModel | HatchetTaskDockerRunModel = (
        HatchetTaskDockerRunModel()
    )
