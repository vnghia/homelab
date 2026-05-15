import logging

import aiofiles
from homelab_pydantic import HomelabBaseModel, HomelabRootModel, docker

from ...config import Config
from .name import DockerContainerNameConfig

logger = logging.getLogger("docker")


class DockerContainerExecModel(HomelabBaseModel):
    exec: docker.ContainerExecModel
    name: str


class DockerContainerExecConfig(HomelabBaseModel):
    service: str
    exec: str | None = None

    async def load(self, config: Config) -> DockerContainerExecModel:
        logger.debug(self)
        async with aiofiles.open(
            (
                config.docker_dir
                / Config.DOCKER_EXEC_PREFIX
                / self.service
                / (self.exec or self.service)
            )
            .with_suffix(".json")
            .resolve(True),
        ) as exec_file:
            exec = docker.ContainerExecModel.model_validate_json(await exec_file.read())
            name = (await DockerContainerNameConfig(service=self.service).load(config))[
                exec.container
            ]

            return DockerContainerExecModel(exec=exec, name=name)


class DockerContainerExecInput(
    HomelabRootModel[DockerContainerExecModel | DockerContainerExecConfig]
):
    pass
