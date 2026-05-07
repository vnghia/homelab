import logging
import secrets

import aiodocker
import aiofiles
from hatchet_sdk import Context
from homelab_pydantic import docker

from ..config import Config

logger = logging.getLogger(__name__)


class Docker:
    def __init__(self) -> None:
        self.client = aiodocker.Docker()

    @classmethod
    def generate_container_name(cls, service: str, name: str | None) -> str:
        result = service
        if name:
            result += "-" + name
        return result + "-" + secrets.token_hex(4)[:7]

    @classmethod
    async def load_model(
        cls, service: str, name: str | None
    ) -> docker.ContainerCreationModel:
        async with aiofiles.open(
            (
                Config.load().docker_dir
                / Config.DOCKER_RUN_PREFIX
                / service
                / (name or service)
            )
            .with_suffix(".json")
            .resolve(True),
        ) as file:
            return docker.ContainerCreationModel.model_validate_json(await file.read())

    @classmethod
    async def run_model(
        cls,
        context: Context,
        model: docker.ContainerCreationModel,
        name: str | None,
        stdout: bool = True,
        stderr: bool = True,
    ) -> None:
        container = await cls().client.containers.create(
            model.model_dump(mode="json", by_alias=True, exclude_unset=True),
            name=name,
        )

        container_inspect = docker.schema.ModelContainerInspectResponse.model_validate(
            await container.show()
        )
        container_name = (
            container_inspect.name.removeprefix("/") if container_inspect.name else None
        )
        logger.info("Running container {}".format(container_name))
        logger.debug(container_inspect)

        try:
            await container.start()

            async for logs in container.log(
                stdout=stdout, stderr=stderr, follow=True, timeout=None
            ):
                # TODO: use AsyncLogSender after https://github.com/hatchet-dev/hatchet/issues/3805
                for line in logs.splitlines():
                    logger.info("[{}] - {}".format(container_name, line))

            exit_status = docker.schema.ModelContainerWaitResponse.model_validate(
                await container.wait(timeout=None)
            )
            if exit_status.status_code > 0:
                raise RuntimeError(
                    exit_status,
                    docker.schema.ModelContainerInspectResponse.model_validate(
                        await container.show()
                    ),
                )
        finally:
            await container.delete(force=True, v=True)

    @classmethod
    async def load_and_run_model(
        cls, context: Context, service: str, name: str | None
    ) -> None:
        config = await cls.load_model(service, name)
        return await cls.run_model(
            context, config, cls.generate_container_name(service, name)
        )
