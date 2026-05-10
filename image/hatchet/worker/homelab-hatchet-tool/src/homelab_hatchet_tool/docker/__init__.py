import datetime
import logging
import secrets
from typing import Any

import aiodocker
from hatchet_sdk import Context, Hatchet
from hatchet_sdk.runnables.workflow import BaseWorkflow
from homelab_pydantic import docker

from ..config import Config
from ..worker import label
from .model.run import DockerContainerRunModel

logger = logging.getLogger("docker")


class Docker:
    DOCKER_RUN_TASK = "docker-run"

    def __init__(self) -> None:
        self.client = aiodocker.Docker()

    @classmethod
    def generate_container_name(cls, service: str, name: str | None) -> str:
        result = service
        if name:
            result += "-" + name
        return result + "-" + secrets.token_hex(4)[:7]

    @classmethod
    async def run_container(
        cls,
        context: Context,
        creation: docker.ContainerCreationModel,
        name: str | None,
        stdout: bool = True,
        stderr: bool = True,
    ) -> None:
        container = await cls().client.containers.create(
            creation.model_dump(mode="json", by_alias=True, exclude_unset=True),
            name=name,
        )
        logger.debug(creation)

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
        cls, context: Context, model: DockerContainerRunModel
    ) -> None:
        creation = await model.load(Config.load())
        return await cls.run_container(
            context,
            creation,
            model.name or cls.generate_container_name(model.service, model.container),
        )

    @classmethod
    def build_workflows(cls, hatchet: Hatchet) -> list[BaseWorkflow[Any]]:
        @hatchet.task(
            name=cls.DOCKER_RUN_TASK,
            input_validator=DockerContainerRunModel,
            desired_worker_labels=[
                label.DESIRED_HOST_LABEL,
                label.DESIRED_DOCKER_LABEL,
            ],
            execution_timeout=datetime.timedelta(days=7),
        )
        async def docker_run(input: DockerContainerRunModel, context: Context) -> None:
            return await cls.load_and_run_model(context, input)

        return [docker_run]
