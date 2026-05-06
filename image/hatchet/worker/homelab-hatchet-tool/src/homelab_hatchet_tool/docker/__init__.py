import secrets

import aiodocker
import aiofiles
from hatchet_sdk import Context
from homelab_pydantic import docker

from ..config import Config


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
    async def load_config(
        cls, service: str, name: str | None
    ) -> docker.ModelContainerConfig:
        async with aiofiles.open(
            (Config.load().docker_dir / service / (name or service))
            .with_suffix(".json")
            .resolve(True),
            "r+b",
        ) as file:
            return docker.ModelContainerConfig.model_validate_json(await file.read())

    @classmethod
    async def run_config(
        cls,
        context: Context,
        config: docker.ModelContainerConfig,
        name: str | None,
        stdout: bool = True,
        stderr: bool = True,
    ) -> docker.ModelContainerWaitResponse:
        container = await cls().client.containers.create(
            config.model_dump(mode="json"), name=name
        )
        response = docker.ModelContainerInspectResponse.model_validate(
            await container.show()
        )
        context.log(
            "Running container with id={} name={}".format(response.id, response.name)
        )
        try:
            await container.start()

            async for logs in container.log(
                stdout=stdout, stderr=stderr, follow=True, timeout=None
            ):
                for log in logs.splitlines():
                    context.log(log)
            return docker.ModelContainerWaitResponse.model_validate(
                await container.wait(timeout=None)
            )
        finally:
            await container.delete(force=True, v=True, link=True)

    @classmethod
    async def load_and_run_config(
        cls,
        context: Context,
        service: str,
        name: str | None,
    ) -> docker.ModelContainerWaitResponse:
        config = await cls.load_config(service, name)
        return await cls.run_config(
            context, config, cls.generate_container_name(service, name)
        )
