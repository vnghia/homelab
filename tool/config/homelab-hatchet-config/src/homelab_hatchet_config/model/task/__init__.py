from homelab_pydantic import HomelabRootModel

from .docker import HatchetTaskDockerModel


class HatchetTaskModel(HomelabRootModel[HatchetTaskDockerModel]):
    root: HatchetTaskDockerModel = HatchetTaskDockerModel()
