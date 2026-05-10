import logging

import aiofiles
from homelab_pydantic import HomelabBaseModel, docker

from ...config import Config

logger = logging.getLogger("docker")


class DockerContainerExecModel(HomelabBaseModel):
    service: str
    exec: str | None = None

    async def load(self, config: Config) -> tuple[docker.ContainerExecModel, str]:
        logger.debug(self)
        async with (
            aiofiles.open(
                (
                    config.docker_dir
                    / Config.DOCKER_EXEC_PREFIX
                    / self.service
                    / (self.exec or self.service)
                )
                .with_suffix(".json")
                .resolve(True),
            ) as exec_file,
            aiofiles.open(
                (config.docker_dir / Config.DOCKER_NAME_PREFIX / self.service)
                .with_suffix(".json")
                .resolve(True),
            ) as name_file,
        ):
            exec = docker.ContainerExecModel.model_validate_json(await exec_file.read())
            name = docker.ContainerServiceName.model_validate_json(
                await name_file.read()
            )[exec.container]

            return exec, name
