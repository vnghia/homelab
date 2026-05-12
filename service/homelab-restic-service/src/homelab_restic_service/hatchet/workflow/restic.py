from typing import ClassVar, Self

from homelab_hatchet_tool.config import Config
from homelab_hatchet_tool.docker.model.run import DockerContainerRunModel
from homelab_pydantic import AbsolutePath, HomelabBaseModel, docker


class HatchetResticProfileModel(HomelabBaseModel):
    volume: str
    path: AbsolutePath


class HatchetResticModel(HomelabBaseModel):
    groups: dict[str, list[str]]
    profiles: dict[str, HatchetResticProfileModel]


class HatchetResticConfig(HomelabBaseModel):
    container: str | None
    restic: HatchetResticModel


class HatchetResticModelConfig(HomelabBaseModel):
    RESTIC: ClassVar[str] = "restic"

    model: docker.ContainerCreationModel
    restic: HatchetResticModel

    @classmethod
    async def load(cls, config: Config) -> Self:
        raw_config = await config.load_service(cls.RESTIC, HatchetResticConfig)
        model = await DockerContainerRunModel(
            service=cls.RESTIC, container=raw_config.container
        ).load(config)
        return cls(model=model, restic=raw_config.restic)
