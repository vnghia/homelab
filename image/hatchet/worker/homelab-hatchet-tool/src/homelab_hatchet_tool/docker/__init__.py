import datetime
import logging
import secrets
from typing import Any

import aiodocker
from hatchet_sdk import Context, Hatchet
from hatchet_sdk.runnables.workflow import BaseWorkflow, Standalone
from homelab_pydantic import add_namespace, docker

from ..config import Config, ConfigDependency
from ..worker import label
from .model.exec import DockerContainerExecConfig, DockerContainerExecModel
from .model.run import DockerContainerRunConfig, DockerContainerRunModel

logger = logging.getLogger("docker")


class Docker:
    DOCKER_RUN_CONFIG_TASK = "docker-run-config"
    DOCKER_RUN_MODEL_TASK = "docker-run-model"

    DOCKER_EXEC_CONFIG_TASK = "docker-exec-config"
    DOCKER_EXEC_MODEL_TASK = "docker-exec-model"

    _docker_run_config_workflow: Standalone[DockerContainerRunConfig, None] | None = (
        None
    )
    _docker_run_model_workflow: Standalone[DockerContainerRunModel, None] | None = None

    _docker_exec_config_workflow: Standalone[DockerContainerExecConfig, None] | None = (
        None
    )
    _docker_exec_model_workflow: Standalone[DockerContainerExecModel, None] | None = (
        None
    )

    def __init__(self) -> None:
        self.client = aiodocker.Docker()

    @classmethod
    def docker_run_config_workflow(cls) -> Standalone[DockerContainerRunConfig, None]:
        if not cls._docker_run_config_workflow:
            raise RuntimeError(
                "Please call `build_workflows` at least once before accesing this function"
            )
        return cls._docker_run_config_workflow

    @classmethod
    def docker_run_model_workflow(cls) -> Standalone[DockerContainerRunModel, None]:
        if not cls._docker_run_model_workflow:
            raise RuntimeError(
                "Please call `build_workflows` at least once before accesing this function"
            )
        return cls._docker_run_model_workflow

    @classmethod
    def docker_exec_config_workflow(cls) -> Standalone[DockerContainerExecConfig, None]:
        if not cls._docker_exec_config_workflow:
            raise RuntimeError(
                "Please call `build_workflows` at least once before accesing this function"
            )
        return cls._docker_exec_config_workflow

    @classmethod
    def docker_exec_model_workflow(cls) -> Standalone[DockerContainerExecModel, None]:
        if not cls._docker_exec_model_workflow:
            raise RuntimeError(
                "Please call `build_workflows` at least once before accesing this function"
            )
        return cls._docker_exec_model_workflow

    @classmethod
    def generate_name_prefix(cls, name: str) -> str:
        return add_namespace(name, secrets.token_hex(4)[:7])

    @classmethod
    async def run_container(
        cls,
        context: Context,
        model: DockerContainerRunModel,
        stdout: bool = True,
        stderr: bool = True,
    ) -> None:
        container = await cls().client.containers.create(
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
    async def exec_container(
        cls,
        context: Context,
        model: DockerContainerExecModel,
        stdout: bool = True,
        stderr: bool = True,
    ) -> None:
        logger.debug(model)
        logger.info("Execing container {}".format(model.name))

        instance = (
            await cls()
            .client.containers.container(model.name)
            .exec(cmd=model.exec.command, stdout=stdout, stderr=stderr, tty=False)
        )
        logger.debug(instance)

        exec_id = instance.id[:7]
        async with instance.start(timeout=None, detach=False) as stream:
            while message := (await stream.read_out()):
                # TODO: use AsyncLogSender after https://github.com/hatchet-dev/hatchet/issues/3805
                logger.info(
                    "[{}] - [{}] - {}".format(
                        model.name, exec_id, message.data.decode()
                    )
                )

    @classmethod
    async def load_and_run_config(
        cls, context: Context, run_config: DockerContainerRunConfig, config: Config
    ) -> None:
        model = await run_config.load(config)
        return await cls.run_container(context, model)

    @classmethod
    async def load_and_exec_config(
        cls, context: Context, exec_config: DockerContainerExecConfig, config: Config
    ) -> None:
        model = await exec_config.load(config)
        return await cls.exec_container(context, model)

    @classmethod
    def build_workflows(cls, hatchet: Hatchet) -> list[BaseWorkflow[Any]]:
        @hatchet.task(
            name=cls.DOCKER_RUN_CONFIG_TASK,
            input_validator=DockerContainerRunConfig,
            desired_worker_labels=[
                label.DESIRED_HOST_LABEL,
                label.DESIRED_DOCKER_LABEL,
            ],
            execution_timeout=datetime.timedelta(days=7),
        )
        async def docker_run_config(
            input: DockerContainerRunConfig, context: Context, config: ConfigDependency
        ) -> None:
            return await cls.load_and_run_config(context, input, config)

        @hatchet.task(
            name=cls.DOCKER_RUN_MODEL_TASK,
            input_validator=DockerContainerRunModel,
            desired_worker_labels=[
                label.DESIRED_HOST_LABEL,
                label.DESIRED_DOCKER_LABEL,
            ],
            execution_timeout=datetime.timedelta(days=7),
        )
        async def docker_run_model(
            input: DockerContainerRunModel, context: Context
        ) -> None:
            return await cls.run_container(context, input)

        @hatchet.task(
            name=cls.DOCKER_EXEC_CONFIG_TASK,
            input_validator=DockerContainerExecConfig,
            desired_worker_labels=[
                label.DESIRED_HOST_LABEL,
                label.DESIRED_DOCKER_LABEL,
            ],
            execution_timeout=datetime.timedelta(days=7),
        )
        async def docker_exec_config(
            input: DockerContainerExecConfig, context: Context, config: ConfigDependency
        ) -> None:
            return await cls.load_and_exec_config(context, input, config)

        @hatchet.task(
            name=cls.DOCKER_EXEC_MODEL_TASK,
            input_validator=DockerContainerExecModel,
            desired_worker_labels=[
                label.DESIRED_HOST_LABEL,
                label.DESIRED_DOCKER_LABEL,
            ],
            execution_timeout=datetime.timedelta(days=7),
        )
        async def docker_exec_model(
            input: DockerContainerExecModel, context: Context
        ) -> None:
            return await cls.exec_container(context, input)

        cls._docker_run_config_workflow = docker_run_config
        cls._docker_run_model_workflow = docker_run_model

        cls._docker_exec_config_workflow = docker_exec_config
        cls._docker_exec_model_workflow = docker_exec_model

        return [
            cls._docker_run_config_workflow,
            cls._docker_run_model_workflow,
            cls._docker_exec_config_workflow,
            cls._docker_exec_model_workflow,
        ]
