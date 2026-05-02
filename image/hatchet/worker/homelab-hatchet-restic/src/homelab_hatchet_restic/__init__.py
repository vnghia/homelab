from aiodocker.docker import Docker

from .config import ResticConfig


class ResticTask:
    def __init__(self, config: ResticConfig) -> None:
        self.client = Docker()
        self.config = config

    async def debug(self) -> None:
        container = await self.client.containers.create(
            self.config.container, name="restic"
        )
        try:
            await container.start()
        finally:
            await container.delete(force=True, v=True, link=True)
