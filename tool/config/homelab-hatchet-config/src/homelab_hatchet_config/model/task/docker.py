from homelab_docker.model.file.docker import DockerContainerOverwriteModel
from homelab_pydantic import HomelabBaseModel

from .base import HatchetTaskBaseModel


class HatchetTaskDockerExecModel(HomelabBaseModel):
    exec: DockerContainerOverwriteModel = DockerContainerOverwriteModel()


class HatchetTaskDockerRunModel(HomelabBaseModel):
    run: DockerContainerOverwriteModel = DockerContainerOverwriteModel()


class HatchetTaskDockerModel(HatchetTaskBaseModel):
    docker: HatchetTaskDockerExecModel | HatchetTaskDockerRunModel = (
        HatchetTaskDockerRunModel()
    )
