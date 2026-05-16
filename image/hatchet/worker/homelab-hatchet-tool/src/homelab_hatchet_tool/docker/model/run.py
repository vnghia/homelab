import logging

import aiofiles
from homelab_pydantic import HomelabBaseModel, HomelabRootModel, add_namespace, docker

from ...config import Config

logger = logging.getLogger("docker")


class DockerContainerRunOverwriteModel(HomelabBaseModel):
    command: list[str] | None = None
    entrypoint: list[str] | None = None


class DockerContainerRunOverwriteDebugModel(HomelabBaseModel):
    debug: str


class DockerContainerRunModel(HomelabBaseModel):
    creation: docker.ContainerCreationModel
    name: str | None = None
    name_prefix: str | None = None


class DockerContainerRunConfig(HomelabBaseModel):
    service: str
    container: str | None = None
    name: str | None = None
    name_prefix: str | None = None
    overwrite: (
        DockerContainerRunOverwriteModel | DockerContainerRunOverwriteDebugModel | None
    ) = None

    async def load(self, config: Config) -> DockerContainerRunModel:
        logger.debug(self)
        async with aiofiles.open(
            (
                config.docker_dir
                / Config.DOCKER_MODEL_PREFIX
                / self.service
                / (self.container or self.service)
            )
            .with_suffix(".json")
            .resolve(True),
        ) as file:
            creation = docker.ContainerCreationModel.model_validate_json(
                await file.read()
            )

            if isinstance(self.overwrite, DockerContainerRunOverwriteModel):
                creation = creation.model_copy(
                    update={
                        "cmd": self.overwrite.command or creation.cmd,
                        "entrypoint": self.overwrite.entrypoint or creation.entrypoint,
                    }
                )
            elif isinstance(self.overwrite, DockerContainerRunOverwriteDebugModel):
                creation = creation.model_copy(
                    update={
                        "host_config": (
                            creation.host_config.model_copy(update={"init": True})
                            if creation.host_config
                            else docker.schema.ModelHostConfig.model_validate(
                                {"init": True}
                            )
                        ),
                        "cmd": [self.overwrite.debug],
                        "entrypoint": ["sleep"],
                    }
                )

            return DockerContainerRunModel(
                creation=creation,
                name=self.name,
                name_prefix=self.name_prefix or add_namespace(self.service, self.name),
            )


class DockerContainerRunInput(
    HomelabRootModel[DockerContainerRunModel | DockerContainerRunConfig]
):
    pass


class DockerContainerRunOutput(HomelabBaseModel):
    name: str
    logs: list[str]
