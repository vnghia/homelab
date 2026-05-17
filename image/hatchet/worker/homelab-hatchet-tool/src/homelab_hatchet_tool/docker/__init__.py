import datetime
import logging
import secrets
from typing import Any

import aiodocker
from hatchet_sdk import Context, Hatchet
from hatchet_sdk.runnables.workflow import BaseWorkflow, Standalone
from homelab_pydantic import add_namespace, docker

from .. import constant
from ..config import ConfigDependency
from .model.exec import (
    DockerContainerExecInput,
    DockerContainerExecModel,
    DockerContainerExecOutput,
)
from .model.run import (
    DockerContainerRunInput,
    DockerContainerRunModel,
    DockerContainerRunOutput,
)

logger = logging.getLogger("docker")


class Docker:
    DOCKER_TIMEOUT = datetime.timedelta(days=7)

    DOCKER_RUN_CONFIG_TASK = "docker-run-config"
    DOCKER_RUN_MODEL_TASK = "docker-run-model"

    DOCKER_EXEC_CONFIG_TASK = "docker-exec-config"
    DOCKER_EXEC_MODEL_TASK = "docker-exec-model"

    _client: aiodocker.Docker | None = None

    _docker_run_workflow: Standalone[DockerContainerRunInput, None] | None = None
    _docker_exec_workflow: Standalone[DockerContainerExecInput, None] | None = None

    @classmethod
    def client(cls) -> aiodocker.Docker:
        if not cls._client:
            cls._client = aiodocker.Docker()
        return cls._client

    @classmethod
    def docker_run_workflow(cls) -> Standalone[DockerContainerRunInput, None]:
        if not cls._docker_run_workflow:
            raise RuntimeError(
                "Please call `build_workflows` at least once before accesing this function"
            )
        return cls._docker_run_workflow

    @classmethod
    def docker_exec_workflow(cls) -> Standalone[DockerContainerExecInput, None]:
        if not cls._docker_exec_workflow:
            raise RuntimeError(
                "Please call `build_workflows` at least once before accesing this function"
            )
        return cls._docker_exec_workflow

    @classmethod
    def generate_name_prefix(cls, name: str) -> str:
        return add_namespace(name, secrets.token_hex(4)[:7])

    @classmethod
    async def run_container(
        cls,
        context: Context,
        model: DockerContainerRunModel,
        *,
        stdout: bool = True,
        stderr: bool = True,
        stream: bool = True,
    ) -> DockerContainerRunOutput:
        container = await cls.client().containers.create(
            model.creation.model_dump(mode="json", by_alias=True, exclude_unset=True),
            name=model.name
            or (
                cls.generate_name_prefix(model.name_prefix)
                if model.name_prefix
                else None
            ),
        )
        logger.debug(model.creation)

        container_inspect = docker.schema.ModelContainerInspectResponse.model_validate(
            await container.show()
        )
        if not container_inspect.name:
            raise RuntimeError("Container name can not be null")
        container_name = container_inspect.name.removeprefix("/")
        logger.info("Running container {}".format(container_name))
        logger.debug(container_inspect)

        try:
            await container.start()

            logs: list[str] = []
            async for raw_log in container.log(
                stdout=stdout, stderr=stderr, follow=True, timeout=None
            ):
                # TODO: use AsyncLogSender after https://github.com/hatchet-dev/hatchet/issues/3805
                lines = raw_log.splitlines()
                logs += lines

                if stream:
                    for line in lines:
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

            return DockerContainerRunOutput(name=container_name, logs=logs)
        finally:
            await container.delete(force=True, v=True)

    @classmethod
    async def exec_container(
        cls,
        context: Context,
        model: DockerContainerExecModel,
        *,
        stdout: bool = True,
        stderr: bool = True,
        stream: bool = True,
    ) -> DockerContainerExecOutput:
        logger.debug(model)
        logger.info("Execing container {}".format(model.name))

        instance = (
            await cls.client()
            .containers.container(model.name)
            .exec(cmd=model.exec.command, stdout=stdout, stderr=stderr, tty=False)
        )
        logger.debug(instance)

        exec_id = instance.id[:7]

        logs: list[str] = []
        async with instance.start(timeout=None, detach=False) as log_stream:  # pyrefly: ignore [bad-context-manager]
            while message := (await log_stream.read_out()):
                lines = message.data.decode().splitlines()
                logs += lines

                if stream:
                    for line in lines:
                        # TODO: use AsyncLogSender after https://github.com/hatchet-dev/hatchet/issues/3805
                        logger.info(
                            "[{}] - [{}] - {}".format(model.name, exec_id, line)
                        )

        if (
            status_code := int((await instance.inspect())["ExitCode"])
        ) and status_code > 0:
            raise RuntimeError(
                "[{}] - [{}] - Exec exited with non-zero status code {}".format(
                    model.name, exec_id, status_code
                )
            )

        return DockerContainerExecOutput(id=instance.id, logs=logs)

    @classmethod
    def build_workflows(cls, hatchet: Hatchet) -> list[BaseWorkflow[Any]]:
        @hatchet.task(
            name=cls.DOCKER_RUN_CONFIG_TASK,
            input_validator=DockerContainerRunInput,
            desired_worker_labels=[
                constant.DESIRED_HOST_LABEL,
                constant.DESIRED_DOCKER_LABEL,
            ],
            execution_timeout=cls.DOCKER_TIMEOUT,
        )
        async def docker_run(
            input: DockerContainerRunInput, context: Context, config: ConfigDependency
        ) -> None:
            root = input.root
            await cls.run_container(
                context,
                root
                if isinstance(root, DockerContainerRunModel)
                else (await root.load(config)),
            )

        @hatchet.task(
            name=cls.DOCKER_EXEC_CONFIG_TASK,
            input_validator=DockerContainerExecInput,
            desired_worker_labels=[
                constant.DESIRED_HOST_LABEL,
                constant.DESIRED_DOCKER_LABEL,
            ],
            execution_timeout=cls.DOCKER_TIMEOUT,
        )
        async def docker_exec(
            input: DockerContainerExecInput, context: Context, config: ConfigDependency
        ) -> None:
            root = input.root
            await cls.exec_container(
                context,
                root
                if isinstance(root, DockerContainerExecModel)
                else (await root.load(config)),
            )

        cls._docker_run_workflow = docker_run
        cls._docker_exec_workflow = docker_exec

        return [cls._docker_run_workflow, cls._docker_exec_workflow]
