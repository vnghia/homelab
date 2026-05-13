import logging

import aiofiles
from homelab_pydantic import HomelabBaseModel, docker

from ...config import Config

logger = logging.getLogger("docker")


class DockerContainerNameConfig(HomelabBaseModel):
    service: str

    async def load(self, config: Config) -> docker.ContainerServiceName:
        logger.debug(self)
        async with (
            aiofiles.open(
                (config.docker_dir / Config.DOCKER_NAME_PREFIX / self.service)
                .with_suffix(".json")
                .resolve(True),
            ) as name_file,
        ):
            return docker.ContainerServiceName.model_validate_json(
                await name_file.read()
            )
