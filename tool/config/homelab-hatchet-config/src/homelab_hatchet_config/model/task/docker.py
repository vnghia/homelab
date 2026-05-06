from homelab_docker.model.file.docker import DockerContainerOverwriteModel
from homelab_pydantic import HomelabBaseModel


class HatchetTaskDockerExecModel(HomelabBaseModel):
    exec: DockerContainerOverwriteModel = DockerContainerOverwriteModel()


class HatchetTaskDockerRunModel(HomelabBaseModel):
    run: DockerContainerOverwriteModel = DockerContainerOverwriteModel()


class HatchetTaskDockerModel(HomelabBaseModel):
    docker: HatchetTaskDockerExecModel | HatchetTaskDockerRunModel = (
        HatchetTaskDockerRunModel()
    )
